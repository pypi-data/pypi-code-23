#!/usr/bin/env python
# -*- coding: utf-8  -*-

def detect_charset(filepath):
	'''检测文件的字符集，并提供置信度。
	'''
	import cchardet as chardet
	charset = None
	with open(filepath, "rb") as f:
		charset = chardet.detect(f.read())
	return charset

def detect_encoding(filepath):
	'''检测文件的编码。
	'''
	cset = detect_charset(filepath)
	encoding = cset["encoding"]
	confidence = cset["confidence"]
	if confidence < 0.9:
		encoding = "utf-8" if encoding == "WINDOWS-1252" else encoding
	return encoding

def try_read(filepath, raise_on_fail = True):
	'''尝试读取文件。
		首先尝试使用常用字符编码方式依次读取文件，
		如果文件没有被正确读取，使用检测的编码读取文件，
		如果文件没有被正确读取，使用codecs忽略不可用字节进行读取。
	Args:
		raise_on_fail: 经过尝试后文件没有被正常读取后抛出异常。默认为True。
	Returns:
		文件内容
	'''

	filetext = None
	read_succeed = False

	try_traces = []
	# 尝试使用常用字符编码读取文件
	common_encodings = ["utf-8", "gbk", "gb2312", "ascii", "utf_8_sig"]
	for encoding in common_encodings:
		try_read = {"try_method": "open", "encoding": encoding}
		try:
			with open(filepath, "r", encoding = encoding) as file:
				filetext = file.read()
				read_succeed = True
		except Exception as e:
			try_read["exception"] = str(e)
		finally:
			try_traces.append(try_read)
		if read_succeed == True:
			break

	# 尝试使用检测的编码读取文件
	if read_succeed == False:
		decteded_encoding = detect_encoding(filepath)
		try_read = {"try_method": "open", "encoding": decteded_encoding}
		try:
			with open(filepath, "r", encoding = decteded_encoding) as file:
				filetext = file.read()
				read_succeed = True
		except Exception as e:
			try_read["exception"] = str(e)
		finally:
			try_traces.append(try_read)

	# 尝试使用codecs忽略不可用字节进行读取
	if read_succeed == False:
		try_read = {"try_method": "codecs.open", "encoding": "utf-8"}
		import codecs
		try:
			with codecs.open(filepath, 'r', 'utf-8', 'ignore') as file:
				filetext = file.read()
				read_success = True
		except Exception as e:
			try_read["exception"] = str(e)
		finally:
			try_traces.append(try_read)

	if filetext is None and read_succeed == False and raise_on_fail == True:
		raise Exception(("try to read file failed. try traces: %s, filetext: %s") % (try_traces, filetext))

	return filetext


def convert_encoding(filepath, src_encoding = None, target_encoding = "utf-8", inplace = False):
	'''转换编码格式
	默认情况下，自动识别原始文件编码格式，将文件内容存储为UTF-8格式。

	Args:
		src_encoding: 原始文件编码格式
		target_encoding: 目标编码格式
		inplace: Default False. If set True, will replace the old file.

	Returns:
		the saved filepath.
	'''
	if src_encoding is None:
		import codecs
		src_charset = detect_charset(filepath)
		src_encoding = src_charset["encoding"]
		src_encoding = "gb2312" if src_encoding == "WINDOWS-1252" else src_encoding
	target_encoding = "utf-8" if target_encoding is None else target_encoding
	text = None
	with codecs.open(filepath, "r", encoding = src_encoding) as file:
		text = file.read()
	tosave_filepath = None
	if inplace == False:
		import os
		(dirname, filefullname) = os.path.split(filepath)
		(filename, extname) = filefullname.split('.')
		new_filename = filename + "_" + target_encoding
		new_filefullname = new_filename + "." + extname
		tosave_filepath = os.path.join(dirname, new_filefullname)
	else:
		tosave_filepath = filepath
	if text is not None:
		with codecs.open(tosave_filepath, "w", encoding = target_encoding) as file:
			file.write(text)
		return tosave_filepath
	else:
		raise Exception
