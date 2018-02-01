import csv
from redash_client.utils import upload_as_json
from redash_client.constants import TTableSchema

schema = [
    {
        "name": "Date",
        "type": "string",
        "friendly_name": "Date"
    }, {
        "name": "Type",
        "type": "string",
        "friendly_name": "Type"
    }, {
        "name": "Average",
        "type": "float",
        "friendly_name": "Average"
    }, {
        "name": "Error",
        "type": "float",
        "friendly_name": "Error"
    }
]

FILENAME = 'active_ticks_existing_users'
TABLE_TEMPLATE = {"columns": schema, "rows": []}

with open('active_ticks_graph.csv') as ticks_file:
  meep = csv.reader(ticks_file, delimiter=',')
  print meep
  break




#upload_as_json("experiments", FILENAME, self._ttables[title])