from pc23 import xrange
from .base import KeyAttributeAbstract


class IndexKey(KeyAttributeAbstract):
    @property
    def key_name(self):
        return "%s_ix_%s" % (self.model.table, self.tbl_k)

    def declaration_sql(self, session):
        uk_name = self.tbl_k
        uk_keys = self.get_column_names(quoted=True, session=session)
        return "KEY %s (%s)" % (session.quote_name(uk_name), (",".join(uk_keys)))


class UniqueKey(KeyAttributeAbstract):
    @property
    def key_name(self):
        return "%s_uix_%s" % (self.model.table, self.tbl_k)

    def declaration_sql(self, session):
        uk_name = self.tbl_k
        uk_keys = self.get_column_names(quoted=True, session=session)
        return "CONSTRAINT %s UNIQUE (%s)" % (session.quote_name(uk_name), (",".join(uk_keys)))


def compare_keys(key1_columns, key2_columns):
    """ Compares two given simple (not foreign) keys by given _attrs. """
    if not isinstance(key1_columns, (list, tuple)):
        key1_columns = [key1_columns, ]
    if not isinstance(key2_columns, (list, tuple)):
        key2_columns = [key2_columns, ]
    sz1 = len(key1_columns)
    sz2 = len(key2_columns)
    if sz1 != sz2:
        return False
    for x in xrange(sz1):
        k1 = key1_columns[x]
        k2 = key2_columns[x]
        cn1 = k1 if isinstance(k1, str) else k1.tbl_k
        cn2 = k2 if isinstance(k2, str) else k2.tbl_k
        if cn1 != cn2:
            return False
    return True

