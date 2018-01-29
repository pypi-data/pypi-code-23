#!/usr/bin/env python
# -*- coding: utf-8  -*-

def encrypt_by_md5(src_str):
	import hashlib
	m = hashlib.md5()
	m.update(src_str.encode('utf-8'))
	return m.hexdigest()