from pathlib import Path
import pandas as pd
from fitchain import dummy_data as dd

class Project:
    def __init__(self, **data):
        self.__dict__.update(data)

    def __str__(self):
        return '{:s} - {:s} by {:s}'.format(self.id, self.name, self.owner)

    def __repr__(self):
        return '{:s} - {:s} by {:s}'.format(self.id, self.name, self.owner)

    def load(self, datasource_id):
        ds = None
        for item in self.datasources:
            if item['id'] == datasource_id:
                ds = item

        if ds is None:
            print("No datasource with id " + datasource_id + " found in project " + self.id)
            return

        # -- Check if the data file is available within the data folder
        file = Path('/data/in/{:s}'.format(datasource_id))

        if file.is_file():
            return pd.read_csv(str(file.as_posix()))
        else:
            schema = ds['schema']
            if schema is None:
                print("Datasource " + datasource_id + " does not contain a valid schema")
                return

            return dd.DummyData(schema).generate_data()