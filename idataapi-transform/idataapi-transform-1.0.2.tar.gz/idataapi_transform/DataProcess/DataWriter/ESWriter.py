import logging
from .BaseWriter import BaseWriter
from ..Config.MainConfig import main_config


class ESWriter(BaseWriter):
    def __init__(self, config):
        if not main_config.has_es_configured:
            raise ValueError("You must config es_hosts before using ESWriter, Please edit configure file: %s" % (main_config.ini_path, ))

        super().__init__()
        self.config = config
        self.total_miss_count = 0
        self.success_count = 0
        self.fail_count = 0

    async def write(self, responses):
        origin_length = len(responses)
        if self.config.filter:
            responses = [self.config.filter(i) for i in responses]
            responses = [i for i in responses if i]
        miss_count = origin_length - len(responses)
        self.total_miss_count += miss_count
        if responses:
            if self.config.expand:
                responses = [self.expand_dict(i) for i in responses]

            success, fail, response = await self.config.es_client.add_dict_to_es(
                self.config.indices, self.config.doc_type, responses,
                self.config.id_hash_func, self.config.app_code,
                self.config.actions, self.config.create_date,
                self.config.error_if_fail, self.config.timeout)
            if response is not None:
                self.success_count += success
                self.fail_count += fail
                logging.info("Write %d items to index: %s, doc_type: %s, fail: %d, filtered: %d" % (
                    len(responses), self.config.indices, self.config.doc_type, fail, miss_count))
            else:
                # exception happened
                logging.info("Write 0 items to index: %s, doc_type: %s" % (self.config.indices, self.config.doc_type))
            return response
        else:
            # all filtered, or pass empty result
            logging.info("Write 0 items to index: %s, doc_type: %s" % (self.config.indices, self.config.doc_type))

    async def delete_all(self, body=None):
        """
        inefficient delete
        """
        if not body:
            body = {
                "query": {
                    "match_all": {}
                }
            }
        result = await self.config.es_client.delete_by_query(index=self.config.indices, doc_type=self.config.doc_type,
                                                             body=body, params={"conflicts": "proceed"})
        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("%s->%s write done, total filtered %d item, total write %d item, total fail: %d item" %
                     (self.config.indices, self.config.doc_type, self.total_miss_count, self.success_count,
                      self.fail_count))
