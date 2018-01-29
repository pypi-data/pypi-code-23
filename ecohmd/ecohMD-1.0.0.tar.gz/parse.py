import re
import judge

start = 0
state = "BEGIN"

def parse(text):
	lines = text.split('\n')
	ans = ""
	while start < len(lines):
		ans = ans + parseLine(lines)
	return ans

def parseStrong(test):
    match = 0
    while(test.find('**') != -1):
        pos = test.find('**')
        if match % 2 == 0:
            if pos + 2 < len(test):
                test = test[: pos] + '<strong>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '<strong>'
                match = match + 1
        elif match % 2 == 1:
            if pos + 2 < len(test):
                test = test[: pos] + '</strong>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '</strong>'
                match = match + 1
    if match % 2 == 1:
        if pos + 8 < len(test):
            test = test[: pos] + '**' + test[pos + 8:]
        else:
            test = test[: pos] + '**'
    match = 0
    while(test.find('__') != -1):
        pos = test.find('__')
        if match % 2 == 0:
            if pos + 2 < len(test):
                test = test[: pos] + '<strong>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '<strong>'
                match = match + 1
        elif match % 2 == 1:
            if pos + 2 < len(test):
                test = test[: pos] + '</strong>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '</strong>'
                match = match + 1
    if match % 2 == 1:
        if pos + 8 < len(test):
            test = test[: pos] + '__' + test[pos + 8:]
        else:
            test = test[: pos] + '__'
    return test

def parseItalic(test):
    match = 0
    while(test.find('*') != -1):
        pos = test.find('*')
        if match % 2 == 0:
            if pos + 1 < len(test):
                test = test[: pos] + '<em>' + test[pos + 1:]
                match = match + 1
            else:
                test = test[: pos] + '<em>'
                match = match + 1
        elif match % 2 == 1:
            if pos + 1 < len(test):
                test = test[: pos] + '</em>' + test[pos + 1:]
                match = match + 1
            else:
                test = test[: pos] + '</em>'
                match = match + 1
    if match % 2 == 1:
        if pos + 4 < len(test):
            test = test[: pos] + '*' + test[pos + 4:]
        else:
            test = test[: pos] + '*'
    match = 0
    while(test.find('_') != -1):
        pos = test.find('_')
        if match % 2 == 0:
            if pos + 1 < len(test):
                test = test[: pos] + '<em>' + test[pos + 1:]
                match = match + 1
            else:
                test = test[: pos] + '<em>'
                match = match + 1
        elif match % 2 == 1:
            if pos + 1 < len(test):
                test = test[: pos] + '</em>' + test[pos + 1:]
                match = match + 1
            else:
                test = test[: pos] + '</em>'
                match = match + 1
    if match % 2 == 1:
        if pos + 4 < len(test):
            test = test[: pos] + '_' + test[pos + 4:]
        else:
            test = test[: pos] + '_'
    return test

def parseUnderLine(test):
    match = 0
    while(test.find('++') != -1):
        pos = test.find('++')
        if match % 2 == 0:
            if pos + 2 < len(test):
                test = test[: pos] + '<u>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '<u>'
                match = match + 1
        elif match % 2 == 1:
            if pos + 2 < len(test):
                test = test[: pos] + '<u>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '</u>'
                match = match + 1
    if match % 2 == 1:
        if pos + 8 < len(test):
            test = test[: pos] + '++' + test[pos + 3:]
        else:
            test = test[: pos] + '++'
    return test

def parseDeleteLine(test):
    match = 0
    while(test.find('~~') != -1):
        pos = test.find('~~')
        if match % 2 == 0:
            if pos + 2 < len(test):
                test = test[: pos] + '<s>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '<s>'
                match = match + 1
        elif match % 2 == 1:
            if pos + 2 < len(test):
                test = test[: pos] + '</s>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '</s>'
                match = match + 1
    if match % 2 == 1:
        if pos + 8 < len(test):
            test = test[: pos] + '~~' + test[pos + 3:]
        else:
            test = test[: pos] + '~~'
    return test

def parseBackground(test):
    match = 0
    while(test.find('==') != -1):
        pos = test.find('==')
        if match % 2 == 0:
            if pos + 2 < len(test):
                test = test[: pos] + '<strong style = \"background:red\">' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '<strong style = \"background:red\">'
                match = match + 1
        elif match % 2 == 1:
            if pos + 2 < len(test):
                test = test[: pos] + '</strong>' + test[pos + 2:]
                match = match + 1
            else:
                test = test[: pos] + '</strong>'
                match = match + 1
    if match % 2 == 1:
        if pos + 8 < len(test):
            test = test[: pos] + '==' + test[pos + 33:]
        else:
            test = test[: pos] + '=='
    return test

def parseHyperLink(test):
	while(re.search(r'\[(.*?)\]\((.*?)\)', test) != None):
		obj = re.search(r'\[(.*?)\]\((.*?)\)', test)
		print(obj)
		text1 = ""
		text2 = ""
		if obj.span(0)[0] == 0:
			pass
		else:
			text1 = test[: obj.span(0)[0]]

		if obj.span(0)[1] == len(test) - 1:
			pass
		else:
			text2 = test[obj.span(0)[1] + 1:]
		test = text1 + "<a href=\"" + obj.group(2) + "\">" + obj.group(1) + "</a>" + text2
	return test

# <p><img src="http://i4.piimg.com/1949/66a86de9c5c16aa8.png" alt="image"></p>
def parseImage(test):
	while(re.search(r'\!\[(.*?)\]\((.*?)\)', test) != None):
		obj = re.search(r'\!\[(.*?)\]\((.*?)\)', test)
		print(obj)
		text1 = ""
		text2 = ""
		if obj.span(0)[0] == 0:
			pass
		else:
			text1 = test[: obj.span(0)[0]]

		if obj.span(0)[1] == len(test) - 1:
			pass
		else:
			text2 = test[obj.span(0)[1] + 1:]
		test = text1 + "<p><img src=\"" + obj.group(2) + "\" alt=\"" + obj.group(1) + "\"></img></p>" + text2
	return test
def parsePara(para):
	para = parseStrong(para)
	para = parseUnderLine(para)
	para = parseBackground(para)
	para = parseItalic(para)
	para = parseDeleteLine(para)
	para = parseImage(para)
	para = parseHyperLink(para)

	return para 

def parseLine(lines):
	ans = ""
	global start
	global state
	if state == "BEGIN":
		if judge.judgeTitle(lines, start):
			state = "TITLE"
			return ""
		if judge.judgeTitleOne(lines, start):
			state = "TITLEONE"
			return ""
		if judge.judgeTitleTwo(lines, start):
			state = "TITLETWO"
			return ""
		if judge.judgeUnorderedListPlus(lines, start):
			state = "UNORDEREDLISTPLUS"
			ans = ans + "<ul>\n"
			return ans
		if judge.judgeUnorderedListSub(lines, start):
			state = "UNORDEREDLISTSUB"
			ans = ans + "<ul>\n"
			return ans
		if judge.judgeUnorderedListStar(lines, start):
			state = "UNORDEREDLISTSTAR"
			ans = ans + "<ul>\n"
			return ans
		if judge.judgeOrderedListStart(lines, start):
			state = "ORDEREDLISTSTART"
			ans = ans + "<ol>\n"
			return ans
		# "<blockquote class = \"style2\">" + text + "</blockquote>"
		if judge.judgeQuote(lines, start):
			state = "QUOTE"
			ans = ans + "<blockquote class = \"style2\">"
			return ans
		# "<pre><code class = \"language-css\">\n" + codeBlock + "</code></pre>\n"
		if judge.judgeNormalCode(lines, start):
			state = "NORMALCODE"
			ans = ans + "<pre><code class = \"language-css\">\n"
			return ans
		ans = ans + "<p>" + parsePara(lines[start]) + "</p>\n"
		start = start + 1
		return ans
	



	if state == "TITLE":
		if judge.judgeTitle(lines, start):
			obj = re.match(r'(#+) (.*)$', lines[start])
			if len(obj.group(1)) > 6:
				ans = ans + "<p>" + parsePara(lines[start]) + "</p>\n"
				start = start + 1
				state = "BEGIN"
				return ans
			ans = ans + "<h" + str(len(obj.group(1))) + ">" + parsePara(obj.group(2)) + "</h" + str(len(obj.group(1))) + ">\n"
			start = start + 1
			state = "BEGIN"
			return ans

	if state == "TITLEONE":
		ans = ans + "<h1>" + parsePara(lines[start]) + "</h1>\n"
		start = start + 2
		state = "BEGIN"
		return ans

	if state == "TITLETWO":
		ans = ans + "<h2>" + parsePara(lines[start]) + "</h2>\n"
		start = start + 2
		state = "BEGIN"
		return ans

	if state == "UNORDEREDLISTSUB":
		obj = re.match(r'\- (.*)$', lines[start])
		ans = ans + "<li>" + parsePara(obj.group(1))
		start = start + 1
		if start == len(lines):
			ans = ans + "</li>\n"
			ans = ans + "</ul>\n"
			state = "BEGIN"
			return ans
		while (judge.judgeNormal(lines, start)) and (not lines[start] == ''):
			ans = ans + "&nbsp;" + parsePara(lines[start])
			start = start + 1
			if start == len(lines):
				ans = ans + "</li>\n"
				ans = ans + "</ul>\n"
				state = "BEGIN"
				return ans
		ans = ans + "</li>\n"
		if judge.judgeUnorderedListSub(lines, start):
			return ans
		if lines[start] == '':
			ans = ans + "</ul>\n"
			start = start + 1
			state = "BEGIN"
			return ans
		if not judge.judgeNormal(lines, start):
			ans = ans + "</ul>\n"
			state = "BEGIN"
			return ans

	if state == "UNORDEREDLISTPLUS":
		obj = re.match(r'\+ (.*)$', lines[start])
		ans = ans + "<li>" + parsePara(obj.group(1))
		start = start + 1
		if start == len(lines):
			ans = ans + "</li>\n"
			ans = ans + "</ul>\n"
			state = "BEGIN"
			return ans
		while (judge.judgeNormal(lines, start)) and (not lines[start] == ''):
			ans = ans + "&nbsp;" + parsePara(lines[start])
			start = start + 1
			if start == len(lines):
				ans = ans + "</li>\n"
				ans = ans + "</ul>\n"
				state = "BEGIN"
				return ans
		ans = ans + "</li>\n"
		if judge.judgeUnorderedListPlus(lines, start):
			return ans
		if lines[start] == '':
			ans = ans + "</ul>\n"
			start = start + 1
			state = "BEGIN"
			return ans
		if not judge.judgeNormal(lines, start):
			ans = ans + "</ul>\n"
			state = "BEGIN"
			return ans
	if state == "UNORDEREDLISTSTAR":
		obj = re.match(r'\* (.*)$', lines[start])
		ans = ans + "<li>" + parsePara(obj.group(1))
		start = start + 1
		if start == len(lines):
			ans = ans + "</li>\n"
			ans = ans + "</ul>\n"
			state = "BEGIN"
			return ans
		while (judge.judgeNormal(lines, start)) and (not lines[start] == ''):
			ans = ans + "&nbsp;" + parsePara(lines[start])
			start = start + 1
			if start == len(lines):
				ans = ans + "</li>\n"
				ans = ans + "</ul>\n"
				state = "BEGIN"
				return ans
		ans = ans + "</li>\n"
		if judge.judgeUnorderedListStar(lines, start):
			return ans
		if lines[start] == '':
			ans = ans + "</ul>\n"
			start = start + 1
			state = "BEGIN"
			return ans
		if not judge.judgeNormal(lines, start):
			ans = ans + "</ul>\n"
			state = "BEGIN"
			return ans

	if state == "ORDEREDLISTSTART":
		obj = re.match(r'[0-9]\. (.*)$', lines[start])
		ans = ans + "<li>" + parsePara(obj.group(1))
		start = start + 1
		if start == len(lines):
			ans = ans + "</li>\n"
			ans = ans + "</ol>\n"
			state = "BEGIN"
			return ans
		while (judge.judgeNormal(lines, start)) and (not lines[start] == ''):
			ans = ans + "&nbsp;" + parsePara(lines[start])
			start = start + 1
			if start == len(lines):
				ans = ans + "</li>\n"
				ans = ans + "</ol>\n"
				state = "BEGIN"
				return ans
		ans = ans + "</li>\n"
		if judge.judgeOrderedListStart(lines, start):
			return ans
		if lines[start] == '':
			ans = ans + "</ol>\n"
			start = start + 1
			state = "BEGIN"
			return ans
		if not judge.judgeNormal(lines, start):
			ans = ans + "</ol>\n"
			state = "BEGIN"
			return ans

	if state == "QUOTE":
		obj = re.match(r'>(.*)$', lines[start])
		ans = ans + parsePara(obj.group(1))
		start = start + 1
		if start == len(lines):
			ans = ans + "</blockquote>\n"
			state = "BEGIN"
			return ans
		while (judge.judgeNormal(lines, start)) and (not lines[start] == ''):
			ans = ans + "&nbsp;" + parsePara(lines[start])
			start = start + 1
			if start == len(lines):
				ans = ans + "</blockquote>\n"
				state = "BEGIN"
				return ans
		if lines[start] == '':
			ans = ans + "</blockquote>\n"
			start = start + 1
			state = "BEGIN"
			return ans
		if not judge.judgeNormal(lines, start):
			ans = ans + "</blockquote>\n"
			state = "BEGIN"
			return ans

	if state == "NORMALCODE":
		block = ""
		start = start + 1
		if start == len(lines):
			ans = ans + "</code></pre>\n"
			state = "BEGIN"
			return ans
		while (start <= len(lines) - 1) and (re.match(r'```( *)', lines[start]) == None):
			block = block + lines[start] + "\n"
			start = start + 1
		if start >= len(lines):
			ans = ans + block + "\n"
			ans = ans + "</code></pre>\n"
			state = "BEGIN"
			return ans
		if (re.match(r'```( *)', lines[start]) != None):
			ans = ans + block + "\n"
			ans = ans + "</code></pre>"
			start = start + 1
			state = "BEGIN"
			return ans
	return "FUCK"
