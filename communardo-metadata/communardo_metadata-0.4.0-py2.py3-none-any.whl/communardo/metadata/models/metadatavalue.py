import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class MetadataValue:
    """
    Represents a single piece of metadata about a piece of Confluence content.
    """
    def __init__(self, metadata_id, key, title, content):  # type: (int, str, str, str) -> None
        self.metadata_id = metadata_id
        self.key = key
        self.title = title
        self.content = content

    def __str__(self):
        return '{} | {} | {} | {}'.format(self.metadata_id, self.key, self.title, self.content[:10])
