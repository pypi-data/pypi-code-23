import psycopg2
from query import *

#from cargo_simplequery.query import *

db = psycopg2.connect("host=127.0.0.1 dbname=user user=postgres password=sttrala1")

s = SelectQueryBuilder('users', ['id'])
s.where().sub().eq('email', 'mike@roetgers.org')
s.where().or_().sub().eq('email', 'du@roe.sad')
print(s.get_query().as_string(db))