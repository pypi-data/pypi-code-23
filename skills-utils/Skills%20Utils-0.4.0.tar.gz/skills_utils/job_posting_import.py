"""Common Schema Job Posting utilities"""
import logging


class JobPostingImportBase(object):
    """Base class for extracting and transforming job postings from
    some source into a common schema. (http://schema.org/JobPosting)

    Subclasses must implement _id, _iter_postings, and _transform.

    Args:
        partner_id (str) An short identifier for the partner (ie NLX, VA)
        s3_conn (boto.s3.connection) an s3 connection, if needed
        onet_cache (skills_ml.onet_cache.OnetCache) a wrapper for ONET data, if needed
    """
    def __init__(self, partner_id, s3_conn=None, onet_cache=None):
        self.partner_id = partner_id
        self.s3_conn = s3_conn
        self.onet_cache = onet_cache

    def postings(self, quarter, stats_counter=None):
        """Yield job postings in common schema format

        Args:
            quarter (str) The quarter, in format '2015Q1'
            stats_counter (object, optional) A counter that can track both
                input and output documents using a 'track' method.
        """
        logging.info('Finding postings for %s', quarter)
        for posting in self._iter_postings(quarter):
            transformed = self._transform(posting)
            transformed['id'] = '{}_{}'.format(
                self.partner_id,
                self._id(posting)
            )
            if stats_counter:
                stats_counter.track(
                    input_document=posting,
                    output_document=transformed
                )
            yield transformed

    def _id(self, document):
        """Given a document, compute a source-specific id for the job posting.
        To be implemented by subclasses

        Args:
            document - The document, in original form

        Returns: (str) an id for the document
        """
        pass

    def _iter_postings(self, quarter):
        """Given a quarter, yield all relevant raw job posting documents.
        To be implemented by subclasses

        Args:
            quarter (str) The quarter, in format '2015Q1'

        Yields: job posting documents in their original format
        """
        pass

    def _transform(self, document):
        """Given a job posting document, transform it into the common schema.
        (http://schema.org/JobPosting)
        To be implemented by subclasses.

        Args:
            document - The document, in original form

        Returns: (dict) The job posting, in common schema form
        """
        pass
