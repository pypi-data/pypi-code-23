import datetime
import time
from .d import D
from .f import F
import re

def toD (dict, engine):	
	d = D (**dict)
	d.encode (engine)
	return d

def make_orders (order_by, keyword = "ORDER"):
	if isinstance (order_by, str):
		order_by = [order_by]
	orders = []
	for f in order_by:
		if f[0] == "-":
			orders.append (f[1:] + " DESC")
		else:
			orders.append (f)	
	return "{} BY {}".format (keyword, ", ".join (orders))

def mkdatetime (unixtime):	
	return datetime.datetime.utcfromtimestamp (unixtime)

ENDING = re.compile ("[.,\s]")
def omit (data, limit = 50):
	if len (data) < limit:
		return data	
	m = ENDING.search (data, limit - 10)
	if m:
		data = data [:m.start ()].strip ()
		if len (data) <= (limit - 3):
			return data + "..."	
	return data [:limit - 3].strip () + "..."

def as_dict (conn, row):
	fields = [x.name for x in conn.description]
	return dict ([(f, _row [i]) for i, f in enumerate (fields)])
    