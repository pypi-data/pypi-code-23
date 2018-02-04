"""Essay model."""
from brainlamp_toolbox import log
from .utils import tokenize, get_sentences, get_paragraphs


class Paragraph:
    """Class Paragraph."""

    def __init__(self, text):
        """Init Paragraph.

        param text: tring to split
        type text: str
        """
        self.text = text
        log.debug('Init Paragraph: %s' % self.text)

    @property
    def words(self):
        """List of words."""
        log.debug("Get the words in the paragraph.")
        return tokenize(self.text)

    @property
    def sentences(self):
        """List of sentences."""
        log.debug("Get the sentences in the paragraph.")
        return get_sentences(self.text)

    @property
    def size(self):
        """Paragraph size."""
        log.debug("Get paragraph size.")
        return len(self.text)

    @property
    def words_count(self):
        """Count of words."""
        return len(self.words)

    def __str__(self):
        return self.text

    def __repr__(self):
        """Represent Paragraph."""
        return 'Paragraph({!r})'.format(self.text)


class Essay:
    """Class Essay."""

    def __init__(self, title, text):
        """Init Essay.

        param title: tring to split
        type title: str
        param text: body essay
        type text: str
        """
        self.title = title
        self.text = text
        self.paragraphs = [Paragraph(p) for p in get_paragraphs(text)]
        log.debug('Init Essay: %s' % self.title)

    @property
    def chars_count(self):
        """Characters count."""
        log.debug("Get the characters count in the essay.")
        return len(self.text)

    @property
    def words_count(self):
        """Words count."""
        log.debug("Get the words count in the essay.")
        return sum((p.words_count for p in self.paragraphs))

    @property
    def paragraphs_count(self):
        """Paragraph count."""
        log.debug("Get the paragraphs count in the essay.")
        return len(self.paragraphs)

    def __iter__(self):
        """Iterate."""
        return iter(self.paragraphs)

    def __str__(self):
        return self.title

    def __repr__(self):
        """Represent Essay."""
        return 'Essay({!r})'.format(self.title)
