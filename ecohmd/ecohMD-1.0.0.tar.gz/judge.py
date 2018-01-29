import re
line = '####### this is a one-title'

def judgeNormal(lines, start):
	if judgeTitle(lines, start):
		return False
	if judgeTitleOne(lines, start):
		return False
	if judgeTitleTwo(lines, start):
		return False
	if judgeUnorderedListPlus(lines, start):
		return False
	if judgeUnorderedListSub(lines, start):
		return False
	if judgeUnorderedListStar(lines, start):
		return False
	if judgeOrderedListStart(lines, start):
		return False
	if judgeCutOff(lines, start):
		return False
	if judgeQuote(lines, start):
		return False
	if judgeNormalCode(lines, start):
		return False
	return True

def judgeTitle(lines, start):
	if re.match(r'#+ .*$', lines[start]):
		return True
	return False

def judgeTitleOne(lines, start):
	if start < len(lines) - 1:
		if lines[start] != '\n' and re.match(r'^(\=+)$', lines[start + 1]):
			return True
	return False

def judgeTitleTwo(lines, start):
	if start < len(lines) - 1:
		if lines[start] != '\n' and re.match(r'^(\-+ *)$', lines[start + 1]):
			return True
	return False

def judgeUnorderedListPlus(lines, start):
	if re.match(r'\+ .*$', lines[start]):
		return True
	return False

def judgeUnorderedListSub(lines, start):
	if re.match(r'\- .*$', lines[start]):
		return True
	return False

def judgeUnorderedListStar(lines, start):
	if re.match(r'\* .*$', lines[start]):
		return True
	return False


def judgeOrderedListStart(lines, start):
	if re.match(r'[0-9]\. .*$', lines[start]):
		return True
	return False

def judgeCutOff(lines, start):
	if re.match(r'\-+ *$', lines[start]):
		return True
	return False

def judgeQuote(lines, start):
	if re.match(r'>(.*)$', lines[start]):
		return True
	return False

def judgeNormalCode(lines, start):
	if re.match(r'```( *)$', lines[start]):
		return True
	return False
















