from .filter_by import FilterByMixin
from .sql import SQL


class DeleteSQL(SQL, FilterByMixin):

    def get_data(self):
        for filter_ in self.filters:
            for data in filter_.data:
                yield data


    def __str__(self):
        sql = [
            'DELETE FROM ' + self.schema.TABLE_NAME,
        ]

        if self.filters:
            if len(self.filters) > 1:
                filter_ = self.create_and_filter(*self.filters)
            else:
                filter_ = self.filters[0]

            filter_ = str(filter_)
            if filter_:
                sql.append('WHERE ' + filter_)

        return ' '.join(sql)
