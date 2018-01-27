from communardo.metadata.models.metadatavalue import MetadataValue
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_create():
    m = MetadataValue(1, "key", "title", "content")
    assert m.metadata_id == 1
    assert m.key == "key"
    assert m.title == "title"
    assert m.content == "content"
