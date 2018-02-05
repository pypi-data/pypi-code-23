import sqlite3
import os
import errno
import decimal


class DBConnection(object):
    def __init__(self, vc):
        self.vc = vc

        sqlite3.register_adapter(float, self._adapt_decimal)
        sqlite3.register_converter('money_type', self._convert_to_money)

        db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              'db_for_entities'))

        try:
            os.makedirs(db_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        self.conn = sqlite3.connect(os.path.join(db_dir, 'budget_db'),
                                    detect_types=sqlite3.PARSE_DECLTYPES)
        with self.conn:
            self.c = self.conn.cursor()

            self.c.execute("""CREATE TABLE IF NOT EXISTS budget (
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             date TEXT,
                             amount money_type,
                             comment TEXT,
                             total money_type
                            )""")

    @staticmethod
    def _convert_to_money(entry):
        float_value = float(entry)
        return float_value

    @staticmethod
    def _adapt_decimal(entry):
        kopecks = decimal.Decimal('.01')
        decimal_value = decimal.Decimal(entry)
        res = decimal_value.quantize(kopecks, decimal.ROUND_HALF_UP)
        return str(res)

    @property
    def last_total_amount(self):
        with self.conn:
            self.c.execute("SELECT * FROM budget ORDER BY id DESC LIMIT 1;")
            res = self.c.fetchone()
        if res is None:
            return 0
        return res[4]

    def add_record(self, date, amount, comment, total_amount):
        with self.conn:
            self.c.execute("""INSERT INTO budget(
                             date,
                             amount,
                             comment,
                             total
                            ) VALUES (?, ?, ?, ?);""",
                           (date, amount, comment, total_amount))

    def get_all_rows(self):
        with self.conn:
            self.c.execute("SELECT * FROM budget ORDER BY id;")
            res = self.c.fetchall()
        return res
