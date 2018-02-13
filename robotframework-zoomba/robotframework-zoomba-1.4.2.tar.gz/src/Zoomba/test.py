import APILibrary
import datetime

library = APILibrary.APILibrary()
expected_date = '2018-01-19T21:01:51.67Z'
# expected_date = str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]) + "Z"
actual_date =   '2018-01-19T21:01:56.67Z'
# actual_date = str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]) + "Z"


result = library.date_string_comparator(expected_date=expected_date,
                                 actual_date=actual_date,
                                 key='date', unmatched_keys_list=[])

print(result)

# print(str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]) + "Z")