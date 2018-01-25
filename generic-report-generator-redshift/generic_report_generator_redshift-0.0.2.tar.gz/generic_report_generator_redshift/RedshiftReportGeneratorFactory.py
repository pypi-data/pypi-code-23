from collections import OrderedDict
from urllib import parse

import sqlalchemy

from generic_report_generator import ReportGeneratorFactory

from .model import AWSCredential, RedshiftDBPersistent
from .RedshiftPersistenceStrategy import RedshiftPersistenceStrategy
from .RedshiftDropTempTableStrategy import RedshiftDropTempTableStrategy
from .RedshiftResultDownloadStrategy import RedshiftResultDownloadStrategy

class RedshiftReportGeneratorFactory(ReportGeneratorFactory):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.aws_credential = AWSCredential(
            kwargs["aws_access_key"],
            kwargs["aws_secret_access_key"]
        )
        self.generic_storage = kwargs["generic_storage"]

    def _create_sa_engine(self, connection_dialect, *args, **kwargs):
        parsed_connection_dialect = parse.urlparse(connection_dialect)
        query_params = OrderedDict(parse.parse_qsl(parsed_connection_dialect.query))
        ssl_root_cert_is_set = "sslrootcert" in query_params
        if ssl_root_cert_is_set:
            connection_dialect = self._reconstruct_connection_dialect(
                connection_dialect,
                query_params
            )
        return sqlalchemy.create_engine(connection_dialect, *args, **kwargs)

    def _reconstruct_connection_dialect(self, connection_dialect, query_params):
        ssl_root_cert = query_params["sslrootcert"]
        query_params["sslrootcert"] = self._download_redshift_ssl_cert(
            ssl_root_cert)
        parsed_connection_dialect = parse.urlparse(connection_dialect)
        return "{url.scheme}://{url.netloc}{url.path}?{qs}".format(
            url=parsed_connection_dialect,
            qs="&".join([key + "=" + value for key, value in query_params.items()])
        )

    def _download_redshift_ssl_cert(self, cert_location):
        parsed_cert_location = parse.urlparse(cert_location)
        is_saved_as_local = parsed_cert_location.scheme == ''
        if is_saved_as_local:
            return cert_location
        return self.generic_storage.download(cert_location)

    def persistence_strategy(self, create_table_statement, schema, buffer_prefix, fixed_buffer_id):
        return RedshiftPersistenceStrategy(RedshiftDBPersistent(
            create_table_statement,
            schema,
            buffer_prefix,
            fixed_buffer_id
        ), self.aws_credential)

    def drop_all_temp_table_strategy(self, logger):
        return RedshiftDropTempTableStrategy(logger)

    def result_download_strategy(self):
        return RedshiftResultDownloadStrategy(self.generic_storage)
