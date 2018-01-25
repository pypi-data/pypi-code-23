from generic_report_generator import DropTempTableStrategy


class RedshiftDropTempTableStrategy(DropTempTableStrategy):
    def __init__(self, logger):
        self.logger = logger

    def list_temp_table(self, connection):
        rows = connection.execute("""SELECT
        DISTINCT name AS table_name
    FROM
        stv_tbl_perm
    WHERE
        temp = 1    
    """)  # http://docs.aws.amazon.com/redshift/latest/dg/r_STV_TBL_PERM.html
        return [row['table_name'] for row in rows]

    def drop_temp_table(self, connection, temp_table):
        connection.execute("DROP TABLE IF EXISTS \"{}\"".format(temp_table))
