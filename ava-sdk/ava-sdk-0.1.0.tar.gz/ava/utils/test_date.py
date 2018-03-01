from date import get_datetime_in_rfc3339
from datetime import datetime

def test_get_datetime_in_rfc3339():
  assert get_datetime_in_rfc3339(1503305955) == '2017-08-21T16:59:15+08:00'
  current_time = datetime.now()
  current_rfc3339 = get_datetime_in_rfc3339()
  assert current_rfc3339 == '{:%Y-%m-%dT%H:%M:%S+08:00}'.format(current_time)
