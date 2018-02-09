
import sys
import re
from cfgpy.tools import FMT_INI, Cfg
from pgdbpy.tools import PgDb
#import psycopg2
import time
import pprint

MYNAME = 'pgpumpy'
DEFAULT_DATA_WINDOW_SIZE = 0
DEFAULT_SLEEP_TIME = 0
DEBUGGING = True
pp = pprint.PrettyPrinter(indent=4)

is_link_pattern = re.compile(r'^:link.*$')
link_statement_parse_pattern = re.compile(r'^:link tables ([\S]+) ([\S]+) and ([\S]+) ([\S]+) on ([\S]+) = ([\S]+)')
plan_line_classifier_pattern = re.compile(r'^([\S]+)\s+[-=]*([<>])[-=]*\s+(.*$)')
default_source_pattern = re.compile(r'^default.*')
primarykey_pattern = re.compile(r'([^*]+)\*')

def parse_link_statement(line):

	m = link_statement_parse_pattern.match(line)
	if not m:
		return None

	linkage = {
	 'on-clause': "{} = {}".format(m.group(5),m.group(6)),
	 'table-nicknames': {
	   m.group(1): m.group(2),
	   m.group(3): m.group(4)
	 },
	 'table-list': [m.group(1), m.group(3)]
	}
	return linkage


class TableLinkage(object):

	def __init__(self, link_statement):

		r = parse_link_statement(link_statement)
		self.on_clause 		= r['on-clause']
		self.table_nicknames 	= r['nicknames']
		self.table_list 		= r['table-list']


def parse_data_source_path_sans_join(data_source_path):

	m = default_source_pattern.match(data_source_path)
	if m:
		return {'use_default_value': True}

	fields = data_source_path.split('/')
	db = fields[0]
	table = fields[1]
	lastfield = fields[2]
	m = primarykey_pattern.match(lastfield)
	if m:
		column = m.group(1)
		result_dict = {
			'db': db, 
			'table': table, 
			'column': column, 
			'is_primary_key': True 
			}
		return result_dict 

	column = lastfield
	result_dict = {
		'db': db, 
		'table': table, 
		'column': column, 
		'is_primary_key': False 
		}

	return result_dict

def parse_data_source_path_with_join(linkage, data_source_path):

	m = default_source_pattern.match(data_source_path)
	if m:
		result_dict = {
			'use_default_value': True, 
			'db': None, 
			'table': None, 
			'nickname': None, 
			'column': None 
		}
		return result_dict

	fields = data_source_path.split('/')
	tablename = fields[1]
	nickname = linkage.table_nicknames[tablename]
	result_dict = { 
		'use_default_value': False, 
		'db': fields[0], 
		'table': tablename, 
		'nickname': nickname, 
		'column': fields[2] 
		}

	return result_dict

def parse_data_target_path_sans_join(data_target_path):

	fields = data_target_path.split('/')
	db = fields[0]
	table = fields[1]
	lastfield = fields[2]
	m = primarykey_pattern.match(lastfield)
	if m:
		column = m.group(1)
		result_dict = {
			'db': db, 
			'table': table, 
			'column': column, 
			'is_primary_key': True 
			}
		return result_dict 

	column = lastfield
	result_dict = {
		'db': db, 
		'table': table, 
		'column': column, 
		'is_primary_key': False 
		}

	return result_dict 

def parse_data_target_path_with_join(linkage, data_target_path):

	fields = data_target_path.split('/')
	tablename = fields[1]
	nickname = linkage.table_nicknames[tablename]
	result_dict = {
		'db': fields[0], 
		'table': tablename, 
		'nickname': nickname, 
		'column': fields[2]
		}

	return result_dict

def get_transfer_plan_content(filepath):

	lines = []
	with open(filepath, 'r') as fh:
		lines = fh.readlines()

	return lines


class TableColumn(object):

	def __init__(self, role, table_column_transfer_statement, linkage=None):
		"""
		 where 'role' ::= 'source'|'target'
		"""
		if linkage and role == 'source':
			r = parse_data_source_path_with_join(linkage, table_column_transfer_statement)
		elif linkage and role == 'target':
			r = parse_data_target_path_with_join(linkage, table_column_transfer_statement)
		elif not linkage and role == 'source':
			r = parse_data_source_path_sans_join(table_column_transfer_statement)
		elif not linkage and role == 'target':
			r = parse_data_target_path_sans_join(table_column_transfer_statement)
		else:
			raise ValueError("unrecognized role: {}, expecting 'source' or 'target'".format(role))

		self.role = role
		self.linkage = linkage
		if not 'use_default_value' in r:
			self.use_default_value = None
		else:
			self.use_default_value = r['use_default_value']

		if not 'db' in r:
			self.db = None
		else:
			self.db = r['db']

		if not 'table' in r:
			self.table = None
		else:
			self.table = r['table']

		if not 'column' in r:
			self.column = None
		else:
			self.column = r['column']

		if not 'is_primary_key' in r:
			self.is_primary_key = None
		else:
			self.is_primary_key = r['is_primary_key']

		if not 'nickname' in r:
			self.nickname = None
		else:
			self.nickname = r['nickname']


class Transference(object):

	def __init__(self, data_source, data_target):

		self.data_source = data_source
		self.data_target = data_target


def parse_xfer_plan_line_sans_join(line):

	m = plan_line_classifier_pattern.match(line)
	if m:
		directional_symbol = m.group(2)
		if directional_symbol == '>':
			data_source_path = m.group(1)
			data_target_path = m.group(3)
		elif directional_symbol == '<':
			data_source_path = m.group(3)
			data_target_path = m.group(1)
		else:
			raise ValueError('bad directional symbol: {}'.format(directional_symbol))
	else:
		raise ValueError('failed to parse transfer plan line: {}'.format(line))

	if DEBUGGING:
		print "source: {}".format(data_source_path)
		print "target: {}".format(data_target_path)

	data_source = TableColumn('source', data_source_path)
	data_target = TableColumn('target', data_target_path)
		
	return Transference(data_source, data_target)


def parse_xfer_plan_line_with_join(linkage, line):

	m = plan_line_classifier_pattern.match(line)
	if m:
		directional_symbol = m.group(2)
		if directional_symbol == '>':
			data_source_path = m.group(1)
			data_target_path = m.group(3)
		elif directional_symbol == '<':
			data_source_path = m.group(3)
			data_target_path = m.group(1)
		else:
			raise ValueError('bad directional symbol: {}'.format(directional_symbol))
	else:
		raise ValueError('failed to parse transfer plan line: {}'.format(line))

	if DEBUGGING:
		print "source: {}".format(data_source_path)
		print "target: {}".format(data_target_path)

	data_source = TableColumn('source', data_source_path, linkage)
	data_target = TableColumn('target', data_target_path, linkage)
	return Transference(data_source, data_target)


def build_upsert_template_from_transfer_column_transference_list(tablename, column_transference_list):

	sql_header = 'INSERT INTO {} ('.format(tablename)
	sql_middle = ') VALUES ('
	sql_tail = ')'

	target_column_name_list = []
	values_list = []
	parameters_list = []
	target_primary_keys_list = []
	for column_transference in column_transference_list:
		if column_transference.data_target.is_primary_key:
			target_primary_keys_list.append(column_transference.data_target.column)
		if column_transference.data_source.use_default_value:
			continue
		target_column_name_list.append(column_transference.data_target.column)
		values_list.append('%s')

	target_column_list_string = ','.join(target_column_name_list)
	target_primary_keys_list_string = ','.join(target_primary_keys_list)
	values_list_string = ','.join(values_list)

	template = 'INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO NOTHING'
	sql = template.format( 	tablename,
				target_column_list_string,
				values_list_string,
				target_primary_keys_list_string )
	return sql

def is_link_statement(line):

	if is_link_pattern.match(line):
		return True

	return False


class TransferPlan(object):

	def __init__(self, target_tablename, transfer_plan_filespec):

		self.target_tablename = target_tablename
		transfer_plan_content = get_transfer_plan_content(transfer_plan_filespec)

		column_transference_list = []
		using_join = False
		linkage = None
		for line in transfer_plan_content:
			""" skip comments """

			if is_link_statement(line):
				linkage = TableLinkage(line)
				using_join = True
				continue

			if not using_join:
				column_transference = parse_xfer_plan_line_sans_join(line)
				column_transference_list.append(column_transference)
				if column_transference.data_source.is_primary_key:
					self.source_table_primary_key = column_transference.data_source.column
				if column_transference.data_target.is_primary_key:
					self.target_table_primary_key = column_transference.data_target.column
				continue

			column_transference = parse_xfer_plan_line_with_join(linkage,line)
			column_transference_list.append(column_transference)
			if column_transference.data_source.is_primary_key:
				self.source_table_primary_key = column_transference.data_source.column
			if column_transference.data_target.is_primary_key:
				self.target_table_primary_key = column_transference.data_target.column

		self.use_join = using_join
		self.linkage = linkage
		self.column_transference_list = column_transference_list
		self.upsert_template = build_upsert_template_from_transfer_column_transference_list(
			target_tablename, column_transference_list)

	def build_select_query(self):

		use_join = self.use_join
		linkage = self.linkage
		if not linkage == None:
			table_list = linkage.table_list
			if DEBUGGING:
				print "TABLE LIST =>"
				pp.pprint(table_list)

		column_transference_list = self.column_transference_list
		table_column_list = []

		previous_table_name = None
		for c in column_transference_list:
			if c.data_source.use_default_value == True:
				""" skip columns that are flagged as using default values """
				continue

			if len(table_column_list) == 0:
				tablename = c.data_source.table
				colname = c.data_source.column
				if use_join:
					nickname = linkage.table_nicknames[tablename]
					table_column_list.append("{}.{}".format(nickname,colname))
				else:
					table_column_list.append(colname)
				previous_table_name = tablename
				continue

			""" otherwise not first column """
			if not use_join and not previous_table_name == c.data_source.table:
				raise ValueError('not using join but sourcing columns from different tables!')
				sys.exit(1)

			tablename = c.data_source.table
			colname = c.data_source.column
			if use_join:
				nickname = linkage.table_nicknames[tablename]
				table_column_list.append("{}.{}".format(nickname,colname))
			else:
				table_column_list.append(colname)
			previous_table_name = tablename

		column_name_string = ','.join(table_column_list)
		""" and build the FROM string """
		if use_join:
			nicknames = linkage.table_nicknames
			tables = nicknames.keys()
			from_string = "{} AS {}".format(table_list[0],nicknames[table_list[0]])
			join_string = "{} AS {}".format(table_list[1],nicknames[table_list[1]])
			on_string = linkage.on_clause
			sql = """SELECT {} FROM {} LEFT OUTER JOIN {} ON {}
			""".format(column_name_string,from_string,join_string,on_string)

		else:
			from_string = previous_table_name
			sql = """SELECT {} from {}
			""".format(column_name_string, previous_table_name)

		return sql


	def build_select_query_with_windowing(self, offset, limit):

		""" want source table's primary key """
		source_table_pk = self.source_table_primary_key
		use_join = self.use_join
		linkage = self.linkage
		if not linkage == None:
			table_list = linkage.table_list
			if DEBUGGING:
				print "TABLE LIST =>"
				pp.pprint(table_list)

		column_transference_list = self.column_transference_list
		table_column_list = []

		previous_table_name = None
		for c in column_transference_list:
			if c.data_source.use_default_value == True:
				""" skip columns that are flagged as using default values """
				continue

			if len(table_column_list) == 0:
				tablename = c.data_source.table
				colname = c.data_source.column
				if use_join:
					nickname = linkage.table_nicknames[tablename]
					table_column_list.append("{}.{}".format(nickname,colname))
				else:
					table_column_list.append(colname)
				previous_table_name = tablename
				continue

			""" otherwise not first column """
			if not use_join and not previous_table_name == c.data_source.table:
				raise ValueError('not using join but sourcing columns from different tables!')
				sys.exit(1)

			tablename = c.data_source.table
			colname = c.data_source.column
			if use_join:
				nickname = linkage.table_nicknames[tablename]
				table_column_list.append("{}.{}".format(nickname,colname))
			else:
				table_column_list.append(colname)
			previous_table_name = tablename

		column_name_string = ','.join(table_column_list)
		""" and build the FROM string """
		if use_join:
			nicknames = linkage.table_nicknames
			tables = nicknames.keys()
			from_string = "{} AS {}".format(table_list[0],nicknames[table_list[0]])
			join_string = "{} AS {}".format(table_list[1],nicknames[table_list[1]])
			on_string = linkage.on_clause
			sql = """SELECT {} FROM {} LEFT OUTER JOIN {} ON {}
			""".format(column_name_string,from_string,join_string,on_string)

		else:
			from_string = previous_table_name
			sql = """SELECT {} FROM {} OFFSET {} LIMIT {}
			""".format(
				column_name_string, 
				previous_table_name,
				offset,
				limit
				)

		return sql



class PgPumpPy(object):

	def __init__(self,cfg):

		if not type(cfg).__name__ == 'CfgPy' and not type(cfg).__name__ == 'Cfg':
			raise ValueError('expecting config argument to be a CfgPy or Cfg object')
			sys.exit(1)

		self.cfg = cfg.cfg_dict

		self.source = PgDb( cfg, 'datasource')
		self.target = PgDb( cfg, 'datatarget')

		self.data_window_size = DEFAULT_DATA_WINDOW_SIZE
		self.sleep_time = DEFAULT_SLEEP_TIME
		if MYNAME in cfg.cfg_dict:
			module_cfgdict = cfg.cfg_dict[MYNAME]
			if 'data_window_size' in module_cfgdict:
				self.data_window_size = int(module_cfgdict['data_window_size'])
			if 'sleep_time' in module_cfgdict:
				self.sleep_time = float(module_cfgdict['sleep_time'])


	def retrieve_data_from_source(self, transferplan):

		sql = transferplan.build_select_query()
		if DEBUGGING:
			print "sql: {}".format(sql)
		rows = self.source.execute('all', sql, None)
		return rows


	def update_target(self, tablename, upsert_template, result_set_from_source):

		disable_cmd = 'ALTER TABLE {} DISABLE TRIGGER ALL'.format(tablename)
		enable_cmd = 'ALTER TABLE {} ENABLE TRIGGER ALL'.format(tablename)

		self.target.execute('none', disable_cmd)

		for row in result_set_from_source:
			self.target.execute('none', upsert_template, row)

		self.target.execute('none', enable_cmd)

	def retrieve_and_update_with_data_windowing(self, target_tablename, xferplan):

		if DEBUGGING:
			print "using data windowing, window size {}".format(self.data_window_size)
			pp.pprint(xferplan.__dict__)
			pp.pprint(xferplan.column_transference_list[0].__dict__)
			pp.pprint(xferplan.column_transference_list[0].data_source.__dict__)
			print "source table: {}".format(xferplan.column_transference_list[0].data_source.table)

		sql = xferplan.build_select_query()
		query_result_set_row_count = int(self.source.get_query_result_set_rowcount(sql))
		if DEBUGGING:
			print "query result set count: {}".format(query_result_set_row_count)
		if query_result_set_row_count <= self.data_window_size:
			if DEBUGGING:
				msg = "{} <= {}, so not using windowing"
				print msg.format(query_result_set_row_count,self.data_window_size)
			result_set = self.retrieve_data_from_source(xferplan)
			self.update_target(target_tablename, xferplan.upsert_template, result_set)
			return

		for start in range(0,query_result_set_row_count,self.data_window_size):
			end = min(start + self.data_window_size, query_result_set_row_count)
			if DEBUGGING:
				print "start: {}, end: {}".format(start, end)
			sql = xferplan.build_select_query_with_windowing(start, self.data_window_size)
			if DEBUGGING:
				print "{}".format(sql)
			result_set = self.source.execute('all', sql, None)
			self.update_target(target_tablename, xferplan.upsert_template, result_set)
			if DEBUGGING:
				print "sleeping for {} seconds".format(self.sleep_time)
			time.sleep(self.sleep_time)		



	def fill_table_using_plan_from_file(self, target_tablename, filepath):

		xferplan = TransferPlan(target_tablename, filepath)

		if DEBUGGING:
			print "UPSERT TEMPLATE =>"
			pp.pprint(xferplan.upsert_template)

		if self.data_window_size > 0:
			self.retrieve_and_update_with_data_windowing(target_tablename, xferplan)
			return

		result_set = self.retrieve_data_from_source(xferplan)
		self.update_target(target_tablename, xferplan.upsert_template, result_set)



class PgPump(PgPumpPy):

	def __init__(self, cfg):

		PgPumpPy.__init__(self, cfg)


if __name__ == "__main__":

	# from cfgpy.tools import FMT_INI, Cfg
	# from pgpumpy.tools import PgPump
	cfg = Cfg(FMT_INI, None, '<config-filespec>')
	p = PgPump(cfg)
	p.fill_table_using_plan_from_file('<target-tablename>', '<transfer-plan-filepath>')


		
