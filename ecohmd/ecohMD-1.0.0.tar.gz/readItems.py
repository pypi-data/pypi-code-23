import os
import shutil
def readQuoteStyle():
	f = open("quoteStyle.css", 'r')
	ans = ""
	try:
		ans = f.read()
	finally:
		f.close()
	return ans + "\n"

def readCodeStyle():
	f = open("codeStyle.css", 'r')
	ans = ""
	try:
		ans = f.read()
	finally:
		f.close()
	return ans + "\n"

def readCodeJS():
	f = open("codeJS.css", 'r')
	ans = ""
	try:
		ans = f.read()
	finally:
		f.close()
	return ans + "\n"

def readSourceMD(filePath, filename):
	f = open(filePath + "/" + filename, 'r')
	ans = ""
	try:
		ans = f.read()
	finally:
		f.close()
	return ans + "\n"

def output(html, outputPath, outputname):
	if os.path.exists(outputPath + '/output'):
		pass
	else:
		os.mkdir(outputPath + '/output')
	shutil.copy('prism.css', outputPath + '/output')
	shutil.copy('prism.js',  outputPath + '/output')

	f = open(outputPath + '/output/' + outputname, 'w')
	f.write(html)
	f.close()