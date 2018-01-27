from communardo.metadata.models.metadatavalue import MetadataValue
from communardo.metadata.models.pagemetadata import PageMetadata
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_create_no_metadata():
    p = PageMetadata(1, "title", "url", "content_type", [])
    assert p.page_id == 1
    assert p.page_title == "title"
    assert p.page_url == "url"
    assert p.page_content_type == "content_type"
    assert len(p.page_metadata) == 0


def test_create_with_metadata():
    m = MetadataValue(1, "key", "title", "content")
    p = PageMetadata(1, "title", "url", "content_type", [m])
    assert len(p.page_metadata) == 1