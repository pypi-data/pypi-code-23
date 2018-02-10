"""
Convert Quark Xpress xtags to XML.

The aim is to generate XML files as a preliminary stage in the conversion of Quark tagged text files to HTML,
and therefore not all xtags features are supported since many are relevant only in a typesetting context
(for example: tracking, kerning...).

In addition, since we eventually want to generate semantic HTML, we make no attempt at parsing paragraph and character style sheet definitions.
The definition are lost; only the name of the stylesheets is preserved. 
Paragraph style sheets should be handled with CSS. 
Character style sheets should be mapped to HTML tags when converting the XML to HTML (For example, a characater style called "Bold Ital" may be represented by a <strong/> tag).


Post-processing and conversion to HTML:
The XML is returned as an lxml.etree.ET object and may be turned to a string representation with the etree.tostring() function (preferably with argument encoding="unicode").
You can then use BeautifulSoup to get HTML=ised XML.

LOADING XTAGS

Use the get_encoding function to determine the file's encoding (from the xtag <e> tag).

Two public functions:

get_encoding()
to_xml()

See Quark's "A Guide to XPress Tags 8 - Quark"  for reference https://www.google.co.uk/url?sa=t&rct=j&q=&esrc=s&source=web&cd=4&cad=rja&uact=8&ved=0ahUKEwjJxM229ZLXAhXoCcAKHQqsCZIQFgg5MAM&url=http%3A%2F%2Ffiles.quark.com%2Fdownload%2Fdocumentation%2FQuarkXPress%2F8%2FEnglish%2FGuide_to_XPress_Tags_8_US.pdf&usg=AOvVaw3ddDQi38GALh-oEE_2_QSF

:todo:

- fix @  
- non-breaking special characters
"""

from pypeg2 import *
from pypeg2 import parse as pparse
from pypeg2.xmlast import create_tree
from lxml.etree import strip_tags, tostring, SubElement
import logging as log



#############################
### PART 1: PREPROCESSING ###
#############################

QUARK_ENCODINGS = {
  8: 'utf16',        #• Unicode (UTF-16): <e8>
  9: 'utf_8_sig',    #• Unicode (UTF-8): <e9> (with BOM)
  0: 'mac-roman',    #• Mac Roman (x-mac-roman): <e0>
  1: 'windows-1252', #• Windows Latin (windows–1252): <e1>
  2: 'iso-8859-1',   #• Western (iso–8859–1): <e2>
  3: 'ms932',        #• Japanese Win (windows–932–2000): <e3>
  # ?                #• Japanese Mac (x-mac-japanese): <e21>
  19: 'cp949',       #• Korean Windows (MS codePage 949): <e19>
  20: 'ksc5601',     #• Korean Mac (KSC5601): <e20>
  6: 'big5',         #• Traditional Chinese (BIG5): <e6>
  7: 'gb2312'}       #• Simplified Chinese (GB2312): <e7>

#QUARK_ESCAPED_CHARACTERS = {} # See the first three special characters below.

QUARK_SPECIAL_CHARACTERS = {
"@": "@", #• @: <\@>
"<": "&lt;", #• <: <\<>
"\\": "&#92;", #• \: <\\>  
#<\n> is bit of a pain. It should become <br> in HTML, but we can't just to a text substition here as it will break the parser.
#on the other hand, it can *often* be treated as a space.
"n": " ", #"&#x0A;", #• New line (Soft return): <\n> (\n marks a paragraph end in xtag, so we cannot replace it directly - use HTML code instead)
"d": "\u200B", #• Discretionary return: <\d> (?)
"-": "\u2010", #• Hyphen*: <\->
#"i": "", #• Indent Here: <\i>
"t": "\t", #• Right-indent tab: <\t>
"s": " ", #• Standard space*: <\s>
"e": "\u2002", #• En space*: <\e>
"p": "\u2008", #• Punctuation space*: <\p>
"f": "\u202F", #• Flex space*: <\f>
"_": "\u2014", #• Em dash*: <\_>
"a": "\u2013", #• En dash*: <\a>
"h": "\u00AD", #• Discretionary hyphen: <\h>
#"2": "", #• Previous Text Box Page Number character: <\2>
#"3": "", #• Current Page Number character: <\3>
#"4": "", #• Next Text Box Page Number character: <\4>
#"c": "", #• New column: <\c>
#"b": "", #• New box: <\b>
"m": "\u2003", #• Em space*: <\m>
"#": "\u2004", #• 3-per-Em space*: <\#>
"$": "\u2005", #• 4-per-Em space*: <\$>
"^": "\u2006", #• 6-per-Em space*: <\^>
"*": "\u2007", #• Figure space*: <\8>
"{": "\u200A", #• Hair space*: <\{>
"}": "\u2009", #• Thin space*: <\[>
"j": "\u2060", #• Word joiner*: <\j>
"o": "\u3000", #• Ideographic space*: <\o>
}
#*Placing a ! before any of the commands in this group makes the space or hyphen nonbreaking (for example, <\!m>).
  
# All Quark character attributes. Only if the dictionary value is not an empty string will
# the key be converted to an HTML tag.
# Character attributes are divided in two categories: type styles (can be reset with the <P> tag) and all the others.
# This division is relevant e.g. for the <$> and <$$> vs <a$> and <a$$> tags, so we create two dicts and then a combined dict.
QUARK_CHAR_ATTRIBUTES_TYPE_STYLE = {
"P" : "", #•  Plain: <P>
"B" : "b", #•  Bold: <B>
"I" : "i", #•  Italic: <I>
"O" : "", #•  Outline: <O>
"S" : "", #•  Shadow: <S>
"U" : "u", #•  Underline: <U>
"W" : "", #•  Word Underline: <W>
"/" : "", #•  Strikethrough: </>
"R" : "", #•  Double Strikethrough: <R>
"K" : "", #•  All Caps: <K>
"H" : "", #•  Small Caps: <H>
"+" : "+", #•  Superscript: <+>
"-" : "-", #•  Subscript: <-> (hyphen)
"V" : "", #•  Superior: <V>
}

QUARK_CHAR_ATTRIBUTES_OTHERS = {
"f" : "", #•  Change font*: <f"font name">
"z" : "", #•  Change font size*: <z###.##> in points
"c" : "", #•  Change color*: <c"color name"> or <cC, cM, cY, cK, and cW>
"s" : "", #•  Change shade*: <s###.#> in percentage of shade
"h" : "", #•  Horizontal scale*: <h###.#> in percentage of scale
"k" : "", #•  Kern*: <k###.##> in 1/200 em space
"t" : "", #•  Track*: <t###.##> in 1/200 em space
"b" : "", #•  Set baseline shift*: <b###.##> in points
"y" : "", #•  Vertical scale*: <y###.#> in percentage of scale
"G" : "", #•  Ligatures: <G1> to turn on, or <G0> to turn off
"p" : "", #•  Opacity*: <p###.#> in percentage of opacity
"o" : "", #•  OpenType: <o"xxxx")> where "xxxx" = the OpenType® feature code
"n" : "", #•  Language: <n##> (see "Languages")
"A" : "", #•  Character alignment†: <*An>, where n indicates the type of alignment; <AT> = Em box, top/right, <AO> = ICF top/right, <AC> = center, <AM> = ICF bottom/left, <AB> = Em box,bottom/ left, <AL> = baseline†
"L" : "", #•  Keep half width characters upright† (a character attribute used only in vertical stories):<Ln>, where <L0> = sideways, <L1> = upright, and <L$> = revert to style sheet
"M" : "", #•  Emphasis marks†: <Mn>, where n is the emphasis mark
"Y" : "", #•  Apply sending to non-CJK characters†: <Y1> to turn on, <Y0> to turn it off, or <Y$> to use the current style sheet setting")}
}
 
QUARK_CHAR_ATTRIBUTES = dict(QUARK_CHAR_ATTRIBUTES_TYPE_STYLE, **QUARK_CHAR_ATTRIBUTES_OTHERS)

def get_encoding(filename):
	"""
	Read the first line of a tagged text file; parses the encoding tag;
	lookup and return the corresponding Python encoding name.
	"""
	log.info('Encoding detection: inspecting file: ' + filename)
	try:
		# First try UTF16 (which has a BOM). Is there a better way of detecting the BOM?
		with open(filename, 'r', encoding='utf16') as f:
			encoding_tag = f.readline()
	except UnicodeError:
		with open(filename, 'r', encoding='mac-roman') as f:
			encoding_tag = f.readline()
	tag_content = re.compile(r'[^<]*<v(.+)><e(.+)>').search(encoding_tag).group(2)
	encoding = QUARK_ENCODINGS[int(tag_content)]
	log.info('  | Detected encoding id ' + tag_content + ' -> ' + encoding)		
	return encoding

# See "A GUIDE TO XPRESS TAGS 8", section "Special characters"
# Note we have a problem with "@": we can't replace it here without breaking everything...
#unicode_lookup = {"f": "\u202F", "_": "\u2014", "a": "\u2013", "h": "\u00AD", 's': ' ', 'n': ' ', 'p': ' ', 'e': ' ', '@': ' at '}#"\u0040"}

# Make list of special characters - have to manually escaped some of them for regex
#In [4]: "".join(list(q.QUARK_SPECIAL_CHARACTERS))
#Out[4]: '@<\\nd-tsepf_ahm#$^*{}jo'

def replace_unicode(tagged_text):
	"""Replace Quark escaped character by their unicode codepoint."""
	escaped_chars_regex = re.compile(r'<\\!{0,1}([@<\\nd\-tsepf_ahm#\$\^\*{}jo])>')    #'<\\!{0,1}([fhsnpea@_])>')
	ket_regex = re.compile(r' >(\w)')
	t = ket_regex.sub(lambda match: ' '+match.group(1), tagged_text) # hack -- apparently a solitary ">" before a word is a soft hyphen (undocumented?) 
	return escaped_chars_regex.sub(lambda match: QUARK_SPECIAL_CHARACTERS[match.group(1)], t)



#################################
### PART 2: PARSE TAGGED TEXT ###
#################################

version  = '<v', attr('version', re.compile(r'[0-9\.]+')), '>'
encoding = '<e' , attr('encoding', re.compile(r'\d+')), '>'

class StylesheetDefinition(str):
	grammar = '@' , attr('name', re.compile(r'[^<>:=]+')), '=', restline

class Text(str):
	grammar = re.compile(r'[^<\n]+')  # @ is OK?

# PARAGRAPH STYLE SHEETS AND ATTRIBUTES
#• Apply Normal paragraph style sheet:   @$:paragraph text
#• Apply No Style paragraph style sheet: @:paragraph text
#• Apply defined paragraph style sheet:  @stylesheetname:paragraph text
para_stylesheet = ('@', attr('class', re.compile(r'[^:]*')) , ':')
para_attributes = ('<*', attr('para_attributes', re.compile(r'[^<>]+')), '>')
	
# CHARACTER STYLE SHEETS AND ATTRIBUTES
#• Apply Normal character style sheet:          <@$>
#• Apply the paragraph's character style sheet: <@$p>
#• Apply No Style character style sheet:        <@>
#• Apply defined character style sheet:         <@stylesheetname>
# Use <x@... to reset all previously set character attributes overrides 
char_stylesheet = ['<x@', '<@'], attr('char_stylesheet', re.compile(r'[^<>:]*')), '>'  # '<a',
#reset_char_attributes = '<a', attr('char_attributes', re.compile(r'\${1,2}')), '>'  # "<a$$>", 
char_attributes = '<', attr('char_attributes', re.compile('[^@<>\*]+')), '>'


#• Set type style according to character attributes in the applied paragraph style sheet:               <$>
#• Set type style according to character attributes in the currently applied character style sheet:     <$$>
#• Set all character attributes according to character attributes in the applied paragraph style sheet: <a$>
#• Set all character attributes to character attributes in the currently applied character style sheet: <a$$>

class CharStyle(str):
	grammar = (maybe_some(char_stylesheet),
	           maybe_some(char_attributes),
	           Text)
	          #maybe_some([char_stylesheet, char_attributes], Text)

#class EscapeCharacter(str):
#	grammar = "<\\", re.compile(r'[@<\\]'), ">"
			   
# Paragraph
class P(List):
	grammar = (maybe_some(char_stylesheet),
	           omit(maybe_some(char_attributes)), # omit() because char attrs are reset on each new para anyway.
	           '\n',
	           maybe_some(para_stylesheet),
	           maybe_some(char_stylesheet),
	           omit(maybe_some(para_attributes)),
	           maybe_some([Text, CharStyle]),
			   )

class Article(List):
	grammar = contiguous(omit(version, encoding), 
	                     omit(some(('\n', StylesheetDefinition))),
	                     some(P),
	                     omit(maybe_some([char_stylesheet, char_attributes])))

###########################################
### PART 3a: PARSE CHARACTER ATTRIBUTES ###
###########################################

XTG_BOOLEAN_CHARACTER_ATTRIBUTES = 'PBIOSUWRKHVp\+\-'
XTG_NUMERIC_CHARACTER_ATTRIBUTES = 'Gshktbypnfcz'

class BooleanCharacterAttribute(str):
	grammar = attr('name', re.compile('(a$|a\$\$|[\$PBIOSUWRKHV\+\-])')) #'((a{0,1}\${0,1,2})|[\$PBIOSUWRKHV\+\-])'  # '([\$PBIOSUWRKHV\+\-]|@\$p|o\(\$\))' Move o($) to StringCharacterAttribute
class NumericCharacterAttribute(str):
	grammar = attr('name', re.compile('[Gshktbypnfcaz]')), attr('value', re.compile('[0-9\.\$\-]+'))
class StringCharacterAttribute(str):
	grammar = attr('name', re.compile('[fco]')), attr('value', re.compile('(\"[a-zA-Z_\-0-9 ]+\")|([CMYKW])|\(((\${0,2})|(\"[a-zA-Z]+\",{0,1}))+\)|(\$)'))
	#                                                                             font (f)       |color (c)| OpenType (o)

class CharacterAttributes(List):
	grammar = some([BooleanCharacterAttribute,
	                NumericCharacterAttribute,
	                StringCharacterAttribute])

#############################################
### PART 3b: PROCESS CHARACTER ATTRIBUTES ###
#############################################

class CharacterAttributesTracker:
	"""A "counter" that keep track of the style as we walk the tree.	
	"""
	def __init__(self): #, mapping):
		self.attributes = {}
		self.character_stylesheet = None
		self.reset_all()
		#self.cmap = sorted(mapping.character.items(), key = lambda p: len(p[0]), reverse=True)
	
	def reset_type_styles(self):
		log.debug("RESET type styles")
		for name in "".join(list(QUARK_CHAR_ATTRIBUTES_TYPE_STYLE)):
			self.attributes[name] = False
	
	def reset_all(self):
		"""Reset all attributes, e.g. upon encountering a <$> tag."""
		log.debug("RESET all styles")
		for name in XTG_BOOLEAN_CHARACTER_ATTRIBUTES + XTG_NUMERIC_CHARACTER_ATTRIBUTES:
			self.attributes[name] = False
	
	def update_attribute(self, a):
		log.debug("Updating character attribute " + a.name)
		if a.name in ('$' , '$$', 'P'):
			self.reset_type_styles()
		elif a.name in('a$', 'a$$'):
			self.reset_all()
		elif isinstance(a, BooleanCharacterAttribute):
			self.attributes[a.name] = not self.attributes[a.name]
		elif isinstance(a, NumericCharacterAttribute):		
			self.attributes[a.name] = a.value if a.value is not '$' else False
		else: 
			pass # placeholder for handling StringCharacterAttributes if and when required.
			
	
	def update(self, tag):
		"""Update the counter from tag."""
		log.debug(str(tag) +  str(tag.text) + str(tag.attrib))
		# First process the character stylesheet, if present. <@$>, <@$p> and <@> mean 'Normal', 'Paragraph' and 'No styleseet'
		# respectively; for our purpose they are all equivalent to 'No stylesheet'.
		try: 
			stylesheet = tag.attrib['char_stylesheet']
			if stylesheet == "$p":
				# This should the paragraph's character stylesheet but
				# but we don't parse definitions yet...
				# Used to set all to None. Revert?
				self.character_stylesheet = 'Normal'
			elif stylesheet == "$":
				self.character_stylesheet = 'Normal'
			elif stylesheet == "":
				self.character_stylesheet = 'No Style'
			else:
				self.character_stylesheet = stylesheet
		except KeyError:
			pass  # No character stylesheet

		# Then process the character attributes:
		try:
			for a in pparse(tag.attrib['char_attributes'], CharacterAttributes):
			  self.update_attribute(a)
		except KeyError:
		  pass	# No character attributes
		
def propagate_class(tree):
	"""Propagate the "class" attribute to <p> tags that don't have one."""
	for t in tree.iter('P'):
		try:
			# If there is a "class" already make a note of it
			new_class =  t.attrib['class']
			if new_class == '$':
				_class = 'Normal'
				t.attrib['class'] = _class
			elif new_class == '':
				_class = 'No Style'
				t.attrib['class'] = _class
			else:
				_class = new_class
			#else:
			#	del t.attrib['class']
			#	_class = None
		except KeyError:
			# If there is no "class" attribute add the last (current) one
			#if _class is not None:
				t.attrib['class'] = _class

			
def fix_character_attributes(tree, keep={}):
	"""Walk the DOM to keep track of characater attributes and replace the xtag with XML tags.
	The "keep" argument determine which xtags to retain in the XML: if True, keep all; if a dict of {"xtags": xmltag}
	pairs, add this dict to QUARK_CHAR_ATTRIBUTES and only attributes with an explicit mapping will be preserved."""
	log.info('Processing character attributes...')
	QUARK_CHAR_ATTRIBUTES.update(keep)
	tracker = CharacterAttributesTracker()
	for p in tree.iter('P'):
		tracker.reset_all() # I *think* we reset all character attributes with a new paragraph. 
		tracker.update(p)
		log.info('p:+str: ' + str(p.text))
		log.info('  |atr: ' + str(p.attrib))
		log.info('  |trk: ' + ''.join([k for k, v in tracker.attributes.items() if v is not False]))
		# attributes other than 'class', if present, are no longer needed:
		try:
			del(p.attrib['char_attributes'])
		except KeyError:
			pass
		try:
			del(p.attrib['char_stylesheet'])
		except KeyError:
			pass
		for t in p.iter('CharStyle'):
			tracker.update(t)
			log.info('t:+str: ' + str(t.text))
			log.info('  |atr: ' + str(t.attrib))
			log.info('  |trk: ' + ''.join([k for k, v in tracker.attributes.items() if v is not False]))			
			t.attrib.clear()  # remove existing attributes before setting our own
			
			if tracker.character_stylesheet is not None:
				# There is a stylesheet applied. Rename the tag and set the style attribute.
				t.tag = 'StyledText'
				t.attrib["style"] = tracker.character_stylesheet
			# Wrap the tag's text into a subtag for each attribute, recursively 
			sub = t
			t_text = t.text
			for a, v in tracker.attributes.items():
				if v and QUARK_CHAR_ATTRIBUTES[a] != "":
					#print('  |atr1: ' + a+ ' '+ str(v))
					log.info('  |atr1: ' + a+ ' '+ str(v))
					sub.text = None
					sub = SubElement(sub, a)
					sub.text = t_text
					if v is not True:
						# For non-boolean attributes, set the value.
						sub.attrib['value'] = v
	# All CharStyle tags are now empty and can be deleted
	strip_tags(tree, 'CharStyle')
					
					
# Consider replacing the code above with the following function 			
def recursive_wrap(tag, tag_list):
	if len(tag_list) == 0:
		return tag
	else:
		text = tag.text
		tag.text = ''
		sub = SubElement(tag, tag_list[-1])
		sub.text = text
		recursive_wrap(tag, tag_list[0::-2])
			
			
#####################################
### PART 4: PUBLIC PARSE FUNCTION ###
#####################################

def to_xml(tagged_text, extra_tags_to_keep={}):
	log.info('Quark tagged text parser: Starting!')
	#with open("log/current_xtag_transcoded.xml", "w") as f:
	#	f.write(replace_unicode(tagged_text))
	tree = create_tree(pparse(replace_unicode(tagged_text), Article))
	#with open("log/current_parsed.xml", "w") as f:
	#	f.write(str(tostring(tree, encoding='utf-8')))
	strip_tags(tree, 'Text') # Text tags are unstyled text and can be stripped
	propagate_class(tree)
	fix_character_attributes(tree, extra_tags_to_keep)
	log.info('Quark tagged text parser: Done.')
	#log.info(tostring(tree, encoding='utf-8'))
	return tree
	

