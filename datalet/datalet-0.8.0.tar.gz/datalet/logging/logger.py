#!/usr/bin/env python
# -*- coding: utf-8  -*-

import logging as lg
import logging.config as lgcfg
import os
import shutil

default_config_filename = "logging-default.cfg"

class Logger(object):
	'''生成一个Logger

	lgr = Logger()

	Args:
		config_filepath: 配置文件路径。如果参数为空，且当前工作目录没有默认配置文件（logging-default.cfg），则将包中配置文件复制到工作目录。
		logger_name: 使用Logger的名称。默认使用root。
	
	Returns:
		返回一个Logger对象。

	Raises:
		

	'''
	def __init__(self, config_filepath = None, logger_name = None):
		if config_filepath is None:
			if not os.path.exists(default_config_filename): 
				src_script_dir = os.path.split(os.path.realpath(__file__))[0]
				exec_script_dir = os.getcwd()
				src_config = os.path.join(src_script_dir, default_config_filename)
				exec_config = os.path.join(exec_script_dir, default_config_filename)
				shutil.copy(src_config, exec_config)
			config_filepath = default_config_filename
		lgcfg.fileConfig(config_filepath)
		self.logger = lg.getLogger(logger_name)

	
	def debug(self, obj):
		self.logger.debug(obj)

	def info(self, obj):
		self.logger.info(obj)
	
	def warning(self, obj):
		self.logger.warning(obj)
	
	def error(self, obj):
		self.logger.error(obj)
	
	def critical(self, obj):
		self.logger.critical(obj)

	