import logging

stringtype = unicode

logging.basicConfig() #TODO: necessary???
logger = logging.getLogger(__name__) #TODO: necessary???

templateregex = r"""
    %(delimiter)s(?:
      (?P<escaped>%(delimiter)s)    |   # Escape sequence of two delimiters
      {(?P<braced>%(pathpattern)s)}     # delimiter and a braced identifier
    )
"""

validationmessage = '''Schema validation for Transformator failed: %(message)s"
    document-path: %(docpath)s
    schema-path:   %(schemapath)s'''

verificationmessage='''Verifying sample %(id)s failed

Expected:
%(expected)s
Got:
%(result)s'''

yaml_defaults={
    'width': 128,
    'default_flow_style': False,
    'default_style': None,
}
