# -*- coding: utf-8 -*-

import requests
import json
import squid
import re
import string


def tokenize_sentences(text):
    return re.split(r'\n|(?:\.\s)', text)

def tokenize_sentences_agressive(text):
    return re.split(r'\n|(?:\.\s)|(?:\.[^\d])', text)


class MEL:
    """Simple interface to IOMED's Medical Language API.

    Example of usage:

        mel = MEL('you-api-key')
        text = 'refiere dolor en el pecho desde hace tres días'
        results = mel.parse(text)

    Visit https://docs.iomed.es for more information.
    Visit https://console.iomed.es to obtain your API keys.

    Args:
        apikey (str): api key, get it from https://console.iomed.es.
        test (boolean): whether to use the testing platform instead of
        production.

    Attributes:
        url (str): URL of the API.

    """

    def __init__(self, apikey, test=False, url=None, timeout=(3.05, 30)):
        self.__apikey = apikey
        self.__host = 'test.iomed.es' if test else 'api.iomed.es'
        self.__url = (url if url else
                      'https://{}/tagger/annotation'.format(self.__host))
        self.__timeout = timeout

    @property
    def url(self):
        return self.__url

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        self.__timeout = timeout

    def parse(self, text, as_json=False):
        """
        Parse a text to find medical concepts. Returns either a dictionary or a
        json string.

        Args:
            text (str): text to be processed. Keep into account there are
                length limits: http://docs.iomed.es/pricing/#limits
            as_json (boolean): whether to return a json string, instead of
               the parsed response from the API.

        Returns:
            (dict) A dictionary with entries "version" (version of the IOMED
            MEL API), and "annotations". "annotations" contains a list of
            medical concepts.

            Learn more at https://docs.iomed.es/api_usage/find_concepts/.

        """
        if len(text) > 2000:
            return self.__parse_long_text(text, as_json)

        data = {"text": text}
        headers = {
            'apikey': self.__apikey,
            'X-Consumer-ID': 'iomed-cli',
            'Access-Method': 'iomed-cli'
        }
        response = requests.post(
            self.__url,
            json=data,
            headers=headers,
            timeout=self.__timeout
        )
        body = response.content.decode('utf-8')
        if as_json:
            return body
        try:
            return json.loads(body)
        except json.decoder.JSONDecodeError as e:
            raise e

    def __parse_long_text(self, text, as_json=False):
        """
        Parse a text to find medical concepts. Returns either a dictionary or a
        json string.

        Args:
            text (str): text to be processed. Keep into account there are
                length limits: http://docs.iomed.es/pricing/#limits
            as_json (boolean): whether to return a json string, instead of
               the parsed response from the API.

        Returns:
            (dict) A dictionary with entries "version" (version of the IOMED
            MEL API), and "annotations". "annotations" contains a list of
            medical concepts.

            Learn more at https://docs.iomed.es/api_usage/find_concepts/.

        """

        def adjust_position(concept, offset):
            """Adjust positions of a concept."""
            o = offset
            concept['match']['begin'] += o
            concept['match']['end'] += o
            chars = concept['characteristics']
            if 'negative' in chars:
                chars['negative']['trigger']['begin'] += o
                chars['negative']['trigger']['end'] += o

            if 'family_member' in chars:
                chars['family_member']['match']['begin'] += o
                chars['family_member']['match']['end'] += o
            return concept

        # tokenize text into sentences, and annotate each sentence.
        sentences = []
        # use a soft tokenizer. If any sentence exceeds 2000 chars, use a more
        # agressive tokenizer.
        for sent in tokenize_sentences(text):
            if len(sent) < 2000:
                sentences.append(sent)
            else:
                sentences.extend(tokenize_sentences_agressive(sent))
        annotations = []
        offset = 0
        for sent in sentences:
            if not sent.strip(string.punctuation + string.whitespace):
                offset += len(sent)
                continue
            res = self.parse(sent)
            offset = text.index(sent, offset)
            annots = res['annotations']
            for annot in annots:
                adjust_position(annot, offset)
            annotations.extend(annots)
            offset += len(sent)
        result = {'version': res['version'], 'annotations': annotations}
        if as_json:
            return json.dumps(result)
        return result


class ParallelMEL:
    """Parallel text processor.
    This class allows to process texts in parallel, using either a single
    instance of IOMED Medical Language API or several of them APIs.

    Usage:

        pmel = ParallelMEL(num_workers=4)
        pmel.add_api('https://api.iomed.es/tagger/annotation', 'your-api-key')
        results = pmel.process(['this is a text', 'this is another text'])

    Args:
        num_workers (int): number of parallel jobs.
        retry_always (bool): if True, on failure retries always, until
          succeeding. Note this means the process could run forever.
          Defaults to False.

    """

    def __init__(self, num_workers=4, retry_always=False):
        self.__apikeys = []
        self.__urls = []
        self.num_workers = num_workers
        self.retry_always = retry_always

    def add_api(self, url, apikey):
        """Add an api with its apikey.
        Args:
            url (str): FULL url of the API.
            apikey (str): apikey for this url.

        Returns:
            None

        """
        self.__urls.append(url)
        self.__apikeys.append(apikey)

    def __parse(self, mel, text):
        try:
            result = mel.parse(text)
            assert 'error' not in result
            return result
        except Exception:
            return None

    def process(self, texts, progress=True):
        """Given an iterable of texts, process all of them and return
        the results in order. If a given text could not be processed, its entry
        in the results list is filled by a None.

        Args:
            texts (list of str): lists of texts to parse.
            progress (bool): whether to show progress bar (tqdm).

        Returns:
            resulting annotations(list of dicts). Each entry in the list is
            a dict with entries 'annotations' and 'version', as returned by
            the IOMED Medical Language API.n

        """

        def error_checker(r):
            return type(r) != dict or 'annotations' not in r

        if not self.__urls:
            raise Exception(('No APIs defined. Please add MEL APIs '
                             'through ParallelMEL.add_api'))

        mels = [MEL(key, url=url)
                for key, url in zip(self.__apikeys, self.__urls)]

        agents = [lambda text, mel_=mel: self.__parse(mel_, text)
                  for mel in mels]

        processor = squid.ParallelProcessor(
            agents,
            self.num_workers,
            error_checker=error_checker,
            retry_always=self.retry_always
        )
        processor.feed(texts)
        return [r if type(r) != squid.SquidError else None
                for r in processor.process_all(progress=progress)]
