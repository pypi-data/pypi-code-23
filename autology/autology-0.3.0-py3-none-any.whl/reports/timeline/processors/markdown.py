"""
Defines the markdown file processor.  Registers the mimetype that will be used to fetch the time values from the
markdown file, as well as a means of translating the data into a data definition.

This will be registered in the generator as part of the report initialization plugin.
"""
import frontmatter
from autology.reports.timeline import keys as fmkeys
from autology.utilities import log_file
from autology.reports.models import Entry


MIME_TYPE = 'text/markdown'


def load_file(path):
    """
    Translate the file pointed to by path into a front matter post.  It will also go through all of the timestamps that
    are stored in the front matter and make them timezone aware.
    :param path:
    :return:
    """
    with path.open() as loaded_file:
        entry = frontmatter.load(loaded_file)

    log_file.process_datetimes(entry.metadata)

    return Entry(entry.metadata[fmkeys.TIME], MIME_TYPE, entry.metadata, entry.content, path)


def register():
    """Register the markdown file processor."""
    log_file.register_mime_type('.md', MIME_TYPE)
    log_file.register_mime_type('.markdown', MIME_TYPE)
    log_file.register_file_processor(MIME_TYPE, load_file)
