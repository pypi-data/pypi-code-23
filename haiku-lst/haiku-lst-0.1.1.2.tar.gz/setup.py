try:
	from setuptools import setup, Extension
except ImportError:	
	from distutils.core import setup, Extension
from distutils.command.build import build as Build
from distutils.command.install import install as DistutilsInstall
from distutils.command.clean import clean as Clean
import shutil
import os, sys
from os.path import join
import re

with open('haiku/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)

if sys.argv[-1] == 'publish':
	buildopt = ['sdist', 'upload']
	os.system('python setup.py %s' % " ".join (buildopt))
	#os.system('twine upload dist/haiku-%s*' % version)
	for each in os.listdir ("dist"):
		os.remove (os.path.join ('dist', each))
	sys.exit()
	
libutil = os.name == "posix" and "util.so.1" or "util.dll"
liblinear = os.name == "posix" and "liblinear.so.3" or "liblinear.dll"

class MakeCommand(Build):
	def run(self):
		if os.name == "posix":
			os.system('cd haiku && make')
			cpcmd = 'cp'
		else:
			os.system('haiku\\make.cmd')
			cpcmd = 'copy'

		common_dir = 'haiku/classifier/learner'
		target_dir = '%s/%s' % (self.build_lib, common_dir)
		self.mkpath(target_dir)
		cmd = '%s %s/%s %s' % (cpcmd, common_dir, libutil, target_dir)
		if os.name == "nt":
			cmd = cmd.replace ("/", "\\")
		os.system(cmd)
			
		if os.name == "posix":
			common_dir = 'haiku/classifier/learner/liblinear'
			target_dir = '%s/%s' % (self.build_lib, common_dir)
		else:			
			common_dir = 'haiku/classifier/learner/liblinear/windows'
			target_dir = '%s/%s' % (self.build_lib, common_dir)					
		cmd = '%s %s/%s %s' % (cpcmd, common_dir, liblinear, target_dir)
		if os.name == "nt": 
			cmd = cmd.replace ("/", "\\")
		self.mkpath(target_dir)
		os.system(cmd)
		Build.run(self)


class CleanCommand(Clean):
	description = "Remove build artifacts from the source tree"

	def run(self):
		Clean.run(self)
		if os.path.exists('build'):
			shutil.rmtree('build')
		for dirpath, dirnames, filenames in os.walk('haiku'):
			for filename in filenames:
				if (filename.endswith('.o') or filename.endswith('.a') or filename.endswith(
						'.so.1') or filename.endswith(
						'.pyd') or filename.endswith(
						'.dll') or filename.endswith('.pyc')):
					os.unlink(os.path.join(dirpath, filename))
			for dirname in dirnames:
				if dirname == '__pycache__':
					shutil.rmtree(os.path.join(dirpath, dirname))

classifiers = [
  'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
  'Development Status :: 3 - Alpha',
  'Environment :: Console',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'Programming Language :: Python'
	'Programming Language :: Python :: 3',
	'Topic :: Text Processing :: Indexing'	
]
	
with open ('README.rst', encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='haiku-lst',
	version=version,
	packages=[
		'haiku', 'haiku.analyzer', 'haiku.converter', "haiku.features",
	  'haiku.classifier', 'haiku.classifier.learner', 'haiku.classifier.learner.liblinear',
	  'haiku.classifier.learner.liblinear.python', 'haiku.export.skitai'
	],
	package_data={
		'haiku': [			
			'Makefile',
			'make.cmd',
			'classifier/learner/test.cpp',
			'classifier/learner/util.c',
			'classifier/learner/Makefile',			
			'classifier/learner/liblinear/windows/*.mexw64', 
			'classifier/learner/liblinear/blas/*.h',
			'classifier/learner/liblinear/blas/*.c',
			'classifier/learner/liblinear/blas/Makefile',
			'classifier/learner/liblinear/python/README',
			'classifier/learner/liblinear/python/Makefile',
			'classifier/learner/liblinear/*.c',
			'classifier/learner/liblinear/*.cpp',
			'classifier/learner/liblinear/*.def',
			'classifier/learner/liblinear/*.h',			
			'classifier/learner/liblinear/Makefile',
			'classifier/learner/liblinear/Makefile.win',
			'classifier/learner/liblinear/COPYRIGHT',
			'classifier/learner/liblinear/README',
			'classifier/learner/liblinear/heart_scale',
		]
	},
	url='https://gitlab.com/hansroh/haiku',
	license='',
	author='Hans Roh',
	author_email='hansroh@gmail.com',
	description='Short Text Classification',
	long_description = long_description,
	platforms = ["posix", "nt"],
	cmdclass={
		'build': MakeCommand,
		'clean': CleanCommand,
	},
	install_requires=['delune'],
)

