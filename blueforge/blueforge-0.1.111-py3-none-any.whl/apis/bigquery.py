from google.cloud import bigquery
from google.cloud.bigquery import SchemaField


class BigQuery(object):
    def __init__(self, project, data_set, table, schemas):
        self.__project = bigquery.Client(project=project)
        self.__data_set = self.__project.dataset(data_set)
        self.__table = self.__table.table(name=table, schema=schemas)

        if self.__table.exists():
            self.__table.reload()
        else:
            self.__table.create()

    def is_table_exists(self):
        return self.__table.exists()

    def insert_data(self, data, step=10000):
        prev_idx = step

        for start_num in range(0, len(data), step):
            request_data = []

            for key in data[start_num:prev_idx]:
                row_data = []
                for schema in self.__table.schema:
                    if key[schema.name] is None:
                        row_data.append(None)
                    else:
                        row_data.append(key[schema.name])
                request_data.append(row_data)

            if len(request_data) > 0:
                print(self.__table.insert_data(request_data))

            prev_idx = prev_idx + step \
 \
            # TODO: Bigquery에서 특정 필드를 가져와서, 해당 필드가 존재할 경우 업데이트, 없을 경우에는 추가하는 로직을 개발한다.


class ForgeSchemaField(SchemaField):
    pass
