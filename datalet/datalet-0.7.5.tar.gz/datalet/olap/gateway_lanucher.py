#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import sys
import subprocess
import shutil

'''
compile:
>>> javac -encoding utf-8 -Djava.ext.dirs=./lib -d ./build/classes  ./src/com/ilanever/dozer/olap/*.java

-encoding: 指定编码
-Djava.ext.dirs: 指定编译的时候调用的类
-d：要生成到的目录

package:
>>> jar cvfm ./bin/com.ilanever.dozer.olap.jar MANIFEST.MF -C ./build/classes .

"-C ./build/classes ."： 把./build/classes中的所有文件归档到jar文件中。

run:
>>> java -jar -Djava.ext.dirs=./lib ./bin/com.ilanever.dozer.olap.jar


'''

class GatewayLanucher(object):
	
	def __init__(self, port = 25333, force = True):
		self.__cur_dir = os.path.split(os.path.realpath(__file__))[0]
		self.__java_root_dir = os.path.join(self.__cur_dir, "java")
		self.__java_src_dir = os.path.join(self.__java_root_dir, "src")
		self.__java_lib_dir = os.path.join(self.__java_root_dir, "lib")
		self.__build_root_dir = os.path.join(self.__java_root_dir, "build")
		if not os.path.exists(self.__build_root_dir):
			os.makedirs(self.__build_root_dir)
		self.__build_classes_dir = os.path.join(self.__build_root_dir, "classes")
		if not os.path.exists(self.__build_classes_dir):
			os.makedirs(self.__build_classes_dir)
		self.__java_bin_dir = os.path.join(self.__java_root_dir, "bin")
		if not os.path.exists(self.__java_bin_dir):
			os.makedirs(self.__java_bin_dir)
		self.__target_jar = os.path.join(self.__java_bin_dir, "com.ilanever.dozer.olap.jar")
		self.__manifest_path = os.path.join(self.__java_root_dir, "MANIFEST.MF")
		#self.__run_process = None
		self.__port = port
		self.__force = force

	def __check_env(self):
		not_found = []
		try:
			subprocess.call(["javac"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		except FileNotFoundError as err:
			not_found.append("javac")

		try:
			subprocess.call(["jar"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		except FileNotFoundError as err:
			not_found.append("jar")

		try:
			subprocess.call(["java"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		except FileNotFoundError as err:
			not_found.append("java")

		return not_found

	def __remove_files(self):
		if os.path.exists(self.__target_jar):
			os.remove(self.__target_jar)
		if os.path.exists(self.__build_classes_dir):
			shutil.rmtree(self.__build_classes_dir)
			os.mkdir(self.__build_classes_dir)

	def __compile(self):
		print("start to compile...")
		try:
			for root, dirs, files in os.walk(self.__java_src_dir): 
				for file in files:
					cmd = "javac -encoding utf-8 -Djava.ext.dirs=%s -d %s -sourcepath %s -classpath %s %s" % \
						(self.__java_lib_dir, self.__build_classes_dir, self.__java_src_dir, \
						self.__build_classes_dir ,os.path.join(root, file))
					print(cmd)
					# or use subprocess.call()
					p = subprocess.Popen(cmd)
					p.wait()

		except Exception as err:
			raise err

	def __package(self):
		print("start to package...")
		try:
			cmd = "jar cvfm %s %s -C %s ." % (self.__target_jar, self.__manifest_path, self.__build_classes_dir)
			print(cmd)
			return subprocess.Popen(cmd)
		except Exception as err:
			raise err

	def __run(self):
		print("start to run...")
		try:
			cmd = "java -jar -Djava.ext.dirs=%s %s" % (self.__java_lib_dir, self.__target_jar)
			print(cmd)
			return subprocess.Popen(cmd)
		except Exception as err:
			raise err

	def start(self):
		not_founds = self.__check_env()
		if len(not_founds) > 0:
			raise EnvironmentError("not found in PATH: ", ", ".join(not_founds))

		if self.__force == True:
			self.__remove_files()

		self.__compile()
		pk_proc = self.__package()
		pk_proc.wait()
		run_proc = self.__run()
		run_proc.wait()

	#def stop(self):
	#	self.__run_process.kill()


#if __name__ == "__main__":
#	lanucher = GatewayLanucher()
#	lanucher.start()