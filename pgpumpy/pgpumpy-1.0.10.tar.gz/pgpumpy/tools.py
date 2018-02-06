# -*- coding: utf-8 -*-

import sys
import re
from cfgpy.tools import FMT_INI, Cfg
import psycopg2
import pprint

DEBUGGING = True
pp = pprint.PrettyPrinter(indent=4)

is_link_pattern = re.compile(r'^:link.*$')
link_statement_parse_pattern = re.compile(r'^:link tables ([\S]+) ([\S]+) and ([\S]+) ([\S]+) on ([\S]+) = ([\S]+)')
plan_line_classifier_pattern = re.compile(r'^([\S]+)\s+[-=]*([<>])[-=]*\s+(.*$)')
default_source_pattern = re.compile(r'^default.*')
target_primarykey_pattern = re.compile(r'([^*]+)\*')

class PgPumpPy(object):

	def __init__(self,cfg):

		if not type(cfg).__name__ == 'CfgPy' and not type(cfg).__name__ == 'Cfg':
			raise ValueError('expecting config argument to be a CfgPy or Cfg object')
			sys.exit(1)

		self.cfg = cfg.cfg_dict
		self.source_host = self.cfg['datasource']['host']
		self.source_name = self.cfg['datasource']['name']
		self.source_user = self.cfg['datasource']['user']
		self.source_pass = self.cfg['datasource']['password']

		cnxstr = "host='{}' user='{}' dbname='{}' password='{}'".format(
			self.source_host,
			self.source_user,
			self.source_name,
			self.source_pass
			)

		self.source_dbh = psycopg2.connect(cnxstr)
			
		self.target_host = self.cfg['datatarget']['host']
		self.target_name = self.cfg['datatarget']['name']
		self.target_user = self.cfg['datatarget']['user']
		self.target_pass = self.cfg['datatarget']['password']

		cnxstr = "host='{}' user='{}' dbname='{}' password='{}'".format(
			self.target_host,
			self.target_user,
			self.target_name,
			self.target_pass
			)

		self.target_dbh = psycopg2.connect(cnxstr)


	def is_link_statement(self, line):

		if is_link_pattern.match(line):
			return True

		return False


	def parse_link_statement(self,line):

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


	def parse_data_source_path(self, data_source_path):


		m = default_source_pattern.match(data_source_path)
		if m:
			return {'use_default_value': True}

		fields = data_source_path.split('/')
		return { 'use_default_value': False, 'db': fields[0], 'table': fields[1], 'column': fields[2] }


	def parse_data_source_path_using_join(self, link_dict, data_source_path):

		m = default_source_pattern.match(data_source_path)
		if m:
			return {'use_default_value': True}

		fields = data_source_path.split('/')
		tablename = fields[1]
		nickname = link_dict['table-nicknames'][tablename]
		return { 'use_default_value': False, 'db': fields[0], 'table': tablename, 'nickname': nickname, 'column': fields[2] }


	def parse_data_target_path(self, data_target_path):

		fields = data_target_path.split('/')
		db = fields[0]
		table = fields[1]
		lastfield = fields[2]
		m = target_primarykey_pattern.match(lastfield)
		if m:
			column = m.group(1)
			return {'db': db, 'table': table, 'column': column, 'is_primary_key': true }

		column = lastfield
		return {'db': db, 'table': table, 'column': column, 'is_primary_key': false }


	def parse_data_target_path_using_join(self, link_dict, data_target_path):

		fields = data_target_path.split('/')
		tablename = fields[1]
		nickname = link_dict['table-nicknames'][tablename]
		return {'db': fields[0], 'table': tablename, 'nickname': nickname, 'column': fields[2]}


	def parse_xfer_plan_line(self, line):

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

		data_source_dict = self.parse_data_source_path(data_source_path)
		data_target_dict = self.parse_data_target_path(data_target_path)
		return { 'data_source': data_source_dict, 'data_target': data_target_dict }


	def parse_xfer_plan_line_using_join(self, link_dict, line):

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

		data_source_dict = self.parse_data_source_path(data_source_path)
		data_target_dict = self.parse_data_target_path(data_target_path)
		return { 'data_source': data_source_dict, 'data_target': data_target_dict }


	def get_table_transfer_plan(self, tablename, filepath):
		"""
		 where 'table_transfer_plan' is a list of transfer plan statements
		"""

		lines = []
		with open(filepath, 'r') as fh:
			lines = fh.readlines()

		return lines

	"""
	def convert_transfer_plan_to_transfer_column_dict_list(self, lines):

		column_dict_list = []
		for line in lines:
			column_transfer_dict = self.parse_xfer_plan_line(line)
			column_dict_list.append(column_transfer_dict)

		return column_dict_list
	"""


	def convert_transfer_plan_to_dictionary(self, lines):

		column_dict_list = []
		using_join = False
		link_dict = None
		for line in lines:
			""" skip comments """

			if self.is_link_statement(line):
				link_dict = self.parse_link_statement(line)
				using_join = True
				continue

			if not using_join:
				column_transfer_dict = self.parse_xfer_plan_line(line)
				column_dict_list.append(column_transfer_dict)
				continue

			column_transfer_dict = self.parse_xfer_plan_line_using_join(link_dict,line)
			column_dict_list.append(column_transfer_dict)

		result = {
		 'use_join': using_join,
		 'link_dict': link_dict,
		 'column_dict_list': column_dict_list
		}

		return result


	def build_select_query(self, d):

		use_join = d['use_join']
		if 'link_dict' in d and not d['link_dict'] == None:
			link_dict = d['link_dict']
			table_list = link_dict['table-list']
			if DEBUGGING:
				print "TABLE LIST =>"
				pp.pprint(table_list)

		column_dict_list = d['column_dict_list']
		table_column_list = []

		previous_table_name = None
		for c in column_dict_list:
			if c['data_source']['use_default_value'] == True:
				""" skip columns that are flagged as using default values """
				continue

			if len(table_column_list) == 0:
				tablename = c['data_source']['table']
				colname = c['data_source']['column']
				if use_join:
					nickname = link_dict['table-nicknames'][tablename]
					table_column_list.append("{}.{}".format(nickname,colname))
				else:
					table_column_list.append(colname)
				previous_table_name = tablename
				continue

			""" otherwise not first column """
			if not use_join and not previous_table_name == c['data_source']['table']:
				raise ValueError('not using join but sourcing columns from different tables!')
				sys.exit(1)

			tablename = c['data_source']['table']
			colname = c['data_source']['column']
			if use_join:
				nickname = link_dict['table-nicknames'][tablename]
				table_column_list.append("{}.{}".format(nickname,colname))
			else:
				table_column_list.append(colname)
			previous_table_name = tablename

		column_name_string = ','.join(table_column_list)
		""" and build the FROM string """
		if use_join:
			nicknames = link_dict['table-nicknames']
			tables = nicknames.keys()
			from_string = "{} AS {}".format(table_list[0],nicknames[table_list[0]])
			join_string = "{} AS {}".format(table_list[1],nicknames[table_list[1]])
			on_string = link_dict['on-clause']
			sql = """SELECT {} FROM {} LEFT OUTER JOIN {} ON {}
			""".format(column_name_string,from_string,join_string,on_string)

		else:
			from_string = previous_table_name
			sql = """SELECT {} from {}
			""".format(column_name_string, previous_table_name)

		return sql

	def retrieve_data_from_source(self,d):

		sql = self.build_select_query(d)
		print "sql: {}".format(sql)
		cur = self.source_dbh.cursor()
		cur.execute(sql)
		self.source_dbh.commit()
		rows = cur.fetchall()
		if DEBUGGING:
			pp.pprint(rows)
		return rows


	def build_upsert_template_from_transfer_column_dict_list(self, tablename, column_dict_list):

		sql_header = 'INSERT INTO {} ('.format(tablename)
		sql_middle = ') VALUES ('
		sql_tail = ')'

		target_column_name_list = []
		values_list = []
		parameters_list = []
		target_primary_keys_list = []
		for column_dict in column_dict_list:
			if column_dict['data_target']['is_primary_key']:
				target_primary_keys_list.append(column_dict['data_target']['column'])
			if column_dict['data_source']['use_default_value']:
				continue
			target_column_name_list.append(column_dict['data_target']['column'])
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


	def disable_table_triggers(self, tablename):

		cur = self.target_dbh.cursor()
		""" last time I looked, psycopg2 didn't support parameter substitution on table names """
		q = 'ALTER TABLE {} DISABLE TRIGGER ALL'.format(tablename)
		cur.execute(q)
		self.target_dbh.commit()


	def enable_table_triggers(self, tablename):

		cur = self.target_dbh.cursor()
		""" last time I looked, psycopg2 didn't support parameter substitution on table names """
		q = 'ALTER TABLE {} ENABLE TRIGGER ALL'.format(tablename)
		cur.execute(q)
		self.target_dbh.commit()	


	def update_target(self, tablename, upsert_template, result_set_from_source):

		disable_cmd = 'ALTER TABLE {} DISABLE TRIGGER ALL'.format(tablename)
		enable_cmd = 'ALTER TABLE {} ENABLE TRIGGER ALL'.format(tablename)

		cur = self.target_dbh.cursor()

		cur.execute(disable_cmd )
		self.target_dbh.commit()

		for row in result_set_from_source:
			cur.execute(upsert_template, row)
		self.target_dbh.commit()

		cur.execute(enable_cmd )
		self.target_dbh.commit()


	def fill_table_using_plan_from_file(self, tablename, filepath):
		
		#transfer_plan_lines = poc.get_table_transfer_plan('accounts',datfile)
		#result = poc.convert_transfer_plan_to_dictionary(transfer_plan_lines)
		#poc.retrieve_data_from_source(result)
		transfer_plan_lines = self.get_table_transfer_plan(tablename, filepath)
		#column_dict_list = self.convert_transfer_plan_to_transfer_column_dict_list(transfer_plan_lines)
		transfer_plan_dict = self.convert_transfer_plan_to_dictionary(transfer_plan_lines)
		if DEBUGGING:
			print "TRANSFER PLAN DICT =>"
			pp.pprint(transfer_plan_dict)

		column_dict_list = transfer_plan_dict['column_dict_list']
		upsert_template = self.build_upsert_template_from_transfer_column_dict_list(tablename, column_dict_list)
		if DEBUGGING:
			print "upsert: {}".format(upsert_template)
		result_set = self.retrieve_data_from_source(transfer_plan_dict)
		if DEBUGGING:
			pp.pprint(result_set)
			#sys.exit(1)
		self.update_target(tablename, upsert_template, result_set)


class PgPump(PgPumpPy):

	def __init__(self, cfg):

		PgPumpPy.__init__(self, cfg)



if __name__ == "__main__":

	# from cfgpy.tools import FMT_INI, Cfg
	# from pgpumpy.tools import PgPump
        cfg = Cfg(FMT_INI, None, '<config-filespec>')
	p = PgPump(cfg)
	p.fill_table_using_plan_from_file('<tablename>', '<transfer-plan-filepath>')

