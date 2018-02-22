from datetime import datetime
from dateutil.relativedelta import relativedelta


class DateFunctions(object):

    # this static method allows to use any of the other methods and apply them to a Pandas Dataframe
    @staticmethod
    def apply_to_df(df, new_col, col, func, *args):
        df[new_col] = df[col].apply(lambda x: func(x, *args))

    @classmethod
    def add_months(cls, s, n):
        s = str(s)
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s, fmt)
                dt2 = dt + relativedelta(days=+1)
                if dt.month == dt2.month:
                    dt3 = dt + relativedelta(months=+n)
                    return dt3.strftime(fmt)
                else:
                    dt3 = dt2 + relativedelta(day=1, months=1, days=-1)
                    return dt3.strftime(fmt)
            except ValueError:
                pass
        raise ValueError('No valid date format found')

    @classmethod
    def to_date(cls, s):
        s = str(s)
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        raise ValueError('No valid date format found')

    @classmethod
    def to_timestamp(cls, s):
        s = str(s)
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        try:
            dt = datetime.strptime(s, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d 00:00:00")
        except ValueError:
            raise ValueError('No valid date format found')

    @classmethod
    def date_cmp(cls, s1, s2):
        s1 = cls.to_date(s1)
        s2 = cls.to_date(s2)
        dt1 = datetime.strptime(s1, "%Y-%m-%d")
        dt2 = datetime.strptime(s2, "%Y-%m-%d")
        if dt1 > dt2:
            return 1
        elif dt1 < dt2:
            return -1
        else:
            return 0

    @classmethod
    def timestamp_cmp(cls, s1, s2):
        s1 = cls.to_timestamp(s1)
        s2 = cls.to_timestamp(s2)
        dt1 = datetime.strptime(s1, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(s2, "%Y-%m-%d %H:%M:%S")
        if dt1 > dt2:
            return 1
        elif dt1 < dt2:
            return -1
        else:
            return 0

    @classmethod
    def trunc(cls, s):
        return cls.to_date(s)

    @classmethod
    def months_between(cls, s1, s2):
        s1 = cls.to_date(s1)
        s2 = cls.to_date(s2)
        dt1 = datetime.strptime(s1, "%Y-%m-%d")
        dt2 = datetime.strptime(s2, "%Y-%m-%d")
        r = relativedelta(dt1, dt2)
        return r.months

    @classmethod
    def month_trunc(cls, s):
        s = str(s)
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-01")
            except ValueError:
                pass
        raise ValueError('No valid date format found')


if __name__ == '__main__':
    print('Calling datefunctions module')