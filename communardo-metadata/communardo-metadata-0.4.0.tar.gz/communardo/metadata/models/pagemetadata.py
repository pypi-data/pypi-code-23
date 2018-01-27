from communardo.metadata.models.metadatavalue import MetadataValue
import logging
from typing import List

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class PageMetadata:
    """
    Represents the set of communardo metadata about a page.
    """
    def __init__(self, page_id, page_title, page_url, page_content_type, page_metadata):
        # type: (int, str, str, str, List[MetadataValue]) -> None
        self.page_id = page_id
        self.page_title = page_title
        self.page_url = page_url
        self.page_content_type = page_content_type
        self.page_metadata = page_metadata

    def __str__(self):
        return '{} | {}'.format(self.page_id, self.page_title)
