class RedshiftDBPersistent:
    def __init__(self, create_table_statement, schema, buffer_prefix, fixed_buffer_id):
        validate_create_table_statement(create_table_statement)
        self.create_table_statement = create_table_statement
        self.schema = schema
        self.buffer_prefix = buffer_prefix
        self.fixed_buffer_id = fixed_buffer_id

    def get_init_buffer_sql(self):
        return self.create_table_statement.format(
            __schema__=self.schema,
            __temp_table__=self.get_temp_table()
        )

    def get_flush_buffer_sql(self, aws_credential, buffer_destination):
        return """
UNLOAD ('
    SELECT
        *
    FROM
        {__schema__}.{__temp_table__} AS buff
'
)
TO
    '{__export_destination__}'
WITH CREDENTIALS AS
   'aws_access_key_id={__aws_key__};aws_secret_access_key={__aws_secret__}'
DELIMITER AS
    ','
PARALLEL
    OFF
ADDQUOTES
ESCAPE
ALLOWOVERWRITE
GZIP;
DROP TABLE IF EXISTS {__schema__}.{__temp_table__};
""".format(
    __schema__=self.schema,
    __temp_table__=self.get_temp_table(),
    __export_destination__=buffer_destination,
    __aws_key__=aws_credential.aws_access_key,
    __aws_secret__=aws_credential.aws_secret_access_key
)

    def get_temp_table(self):
        return "{}_{}".format(
            self.buffer_prefix.lower().replace('-', '_'),
            str(self.fixed_buffer_id).lower().replace('-', '_')
        )

def validate_create_table_statement(create_table_statement):
    is_statement_valid = "{__schema__}.{__temp_table__}" in create_table_statement
    if is_statement_valid:
        return True
    else:
        raise Exception('Table name must be {__schema__}.{__temp_table__}')
