import logging
import os
import yaml

from deepspeech.model import Model
import scipy.io.wavfile as wav

from jeeves.stt import AbstractSTTEngine
from jeeves import diagnose, settings


class DeepSpeechSTT(AbstractSTTEngine):
    """
    DeepSpeech Speech-to-Text implementation
    """

    SLUG = 'deepspeech'

    def __init__(self, graph="models/output_graph.pb",
                 alphabet="models/alphabet.txt"):

        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initializing DeepSpeech with graph '%s' " +
                           "and alphabet '%s'", graph, alphabet)
        self._model = Model(graph, 26, 9, alphabet, 500)

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        profile_path = settings.config('profile.yml')

        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                try:
                    config['graph'] = profile['deepspeech']['graph']
                    config['alphabet'] = profile['deepspeech']['alphabet']
                except KeyError:
                    pass

        return config

    def transcribe(self, fp):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
            fp -- a file object containing audio data
        """

        fs, audio = wav.read(fp)
        return self._model.stt(audio, fs)

    @classmethod
    def is_available(cls):
        return diagnose.check_python_import('deepspeech')
