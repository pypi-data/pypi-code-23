from webdb.typehandling.date_and_time import DateAdapter, DatetimeAdapter, TimeAdapter


def test_date():
	dct = {"__type__": "date", "year": 2018, "month": 2, "day": 2}
	date = DateAdapter.from_dict(dct)
	assert date.to_dict() == dct

def test_time():
	dct = {"__type__": "time", "hour": 10, 
		"minute": 12, "second": 13, 
		"microsecond": 4, "utcoffset": 60}
	time = TimeAdapter.from_dict(dct)
	assert time.to_dict() == dct

def test_datetime():
	dct = {"__type__": "datetime", "hour": 10, 
		"minute": 12, "second": 13, 
		"microsecond": 4, "utcoffset": 60 ,
		"year": 2018, "month": 2, "day": 2}
	date = DatetimeAdapter.from_dict(dct)
	assert date.to_dict() == dct
