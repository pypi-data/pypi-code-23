import yaml

stringtype = unicode

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

# TODO: make the schema more strict (oneOf)
docparamschema = yaml.load("""
type: object
properties:
    type: {type: string, enum: [file, dir]}
    dir: {type: string}
    name: {type: string}
additionalProperties: false
required: [type, name]
""")
