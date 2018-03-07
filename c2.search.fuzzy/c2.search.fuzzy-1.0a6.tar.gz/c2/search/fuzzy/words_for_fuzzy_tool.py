# coding: utf-8

import bisect
from persistent import Persistent

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass

from plone.app.contenttypes.indexers import SearchableText

from logging import getLogger
logger = getLogger(__name__)
info = logger.info
debug = logger.debug

try:
    import MeCab
    from c2.splitter.mecabja.main import get_wakati_only_part
    HAS_MECAB = True
except ImportError:
    HAS_MECAB =False

try:
    import sqlalchemy
    import psycopg2
    USE_SQL = True
except ImportError:
    USE_SQL = False

if USE_SQL:
    # from sqlalchemy.orm import sessionmaker
    # from sqlalchemy import MetaData
    # from sqlalchemy import create_engine
    from sqlalchemy import distinct
    from c2.search.fuzzy.sql_connection import DB_CONNECTION_NAME, get_db_status
    from c2.search.fuzzy.words_for_fuzzy_model import Word
    import transaction



def _s_uni(s):
    assert isinstance(s, basestring)
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    return s

def _normalize(s):
    assert isinstance(s, basestring)
    su = _s_uni(s)
    su_lower = su.lower()
    return su_lower


class FuzzyBase(SimpleItem):
    """
    """
    def __init__(self):
        self.words = []

    def adds(self, xs):
        for y, x in xs:
            self.add(y, x)

    def get_all_yomi(self):
        words = list(y for y, li in self.words) # TODO: list ok?
        return words

    def get_all_dic(self):
        words = self.words
        return dict((y, k) for y, k in words)

    def get_index(self, x):
        words = self.words
        if x in words:
            return bisect.bisect_left(words, x)
        else:
            return None

    def length(self):
        return len(self.words)

    def wakati_part(self, txt, part=None):
        if part is None:
            part = ("名詞", "動詞")
        if HAS_MECAB:
            part_adaptor = MeCab.Tagger()
            return get_wakati_only_part(txt, adaptor=part_adaptor, part=part)
        else:
            return ((t, t) for t in _normalize(txt).split())

    def _sub_process(self, txt):
        for p, y in self.wakati_part(txt):
            if p:
                #TODO: use NLTK if ascii
                yomi = _normalize(y) #To base form
                prototype = _s_uni(p.lower())
                yield yomi, prototype

    def _process(self, text):
        if isinstance(text, basestring):
            txt = text
        else:
            txt = ' '.join(text)
        return self._sub_process(txt)

    def _get_all_indexes_text(self):
        catalog = getToolByName(self, "portal_catalog")
        items = catalog()
        for item in items:
            obj = item.getObject()
            try:
                # text = obj.SearchableText()
                text = SearchableText(obj)
                yield text
            except AttributeError:
                pass

    def _get_indexes_data(self):
        for text in self._get_all_indexes_text():
            yield self._process(text)

    def _add_index(self, index_data):
        for texts in index_data:
            for yomi, word in texts:
                self.add(yomi, word)

    def add_index_form_text(self, text):
        for yomi, word in self._process(text):
            self.add(yomi, word)

    def _add_index_all(self, index_obj):
        self.words = index_obj

    def _create_all_index_obj(self, index_data):
        words_dict = dict()
        for texts in index_data:
            for yomi, word in texts:
                assert isinstance(yomi, unicode)
                assert isinstance(word, unicode)
                if len(yomi) < 3: # ignore if less than 3 character
                    continue
                words_dict.setdefault(yomi, set()).add(word)
        words_orderd_list = sorted((y, s) for y, s in words_dict.items())
        return words_orderd_list


class WordsForFuzzy(UniqueObject, FuzzyBase, Persistent):
    """

    """
    id = 'words_for_fuzzy'
    meta_type= 'Words for Fuzzy'
    plone_tool = 1

    def add(self, y, x):
        assert isinstance(x, unicode)
        assert isinstance(y, unicode)
        if len(y) < 3: # ignore if less than 3 character
            return None
        words_tuple = self.words
        if y not in set(self.get_all_yomi()):
            bisect.insort_left(words_tuple, (y, set([x])))
            self._p_changed = True
        else:
            words_tuple[bisect.bisect_left(words_tuple, (y,))][1].add(x)
            # default type を使えば、これだけで十分行けるか？
            self._p_changed = True

    def remove(self):
        self.words = []
        self._p_changed = True

    def rebuild(self):
        index_data = self._get_indexes_data()
        index_obj = self._create_all_index_obj(index_data)
        self.remove()
        self._add_index_all(index_obj)
        self._p_changed = True
#        self._add_index(index_data)


class WordYomiOrg(object):
    def __init__(self):
        db_status, session, db_status_msg = get_db_status(DB_CONNECTION_NAME)
        if not session:
            debug("No session for add, " + db_status_msg)
        self.session = session

    def get(self, yomi, default=None):
        org_words = self.session.query(Word).filter(Word.yomi==_s_uni(yomi))
        if org_words is None:
            if default is not None:
                return default
            else:
                return []
        return [w.org_word for w in org_words]


class WordsForFuzzyBySQL(FuzzyBase):
    """
    """
    id = 'words_for_fuzzy'
    meta_type= 'Words for Fuzzy'
    plone_tool = 1

    def __init__(self):
        """"""
        pass

    def add(self, y, x, commit=True):
        assert isinstance(x, unicode) # x is Original character
        assert isinstance(y, unicode) # y is yomi
        if len(y) < 3: # ignore if less than 3 character
            return None
        db_status, session, db_status_msg = get_db_status(DB_CONNECTION_NAME)
        if not session:
            debug("No session for add, " + db_status_msg)
            return None
        db_word = session.query(Word).filter(Word.yomi==y).filter(Word.org_word==x).first()
        if db_word:
            return None
        db_word = Word(y, x)
        session.add(db_word)
        if commit:
            transaction.commit()

    def remove(self):
        db_status, session, db_status_msg = get_db_status(DB_CONNECTION_NAME)
        if not session:
            debug("No session for add, " + db_status_msg)
            return None
        num_deleted_words = session.query(Word).delete()
        return num_deleted_words

    def rebuild(self):
        index_data = self._get_indexes_data()
        self.remove()
        self._create_all_index_obj(index_data)

    def get_all_yomi(self):
        db_status, session, db_status_msg = get_db_status(DB_CONNECTION_NAME)
        if not session:
            debug("No session for add, " + db_status_msg)
            return None
        words = [w[0] for w in session.query(distinct(Word.yomi)).order_by(Word.yomi)]
        return words

    @property
    def words(self):
        return []

    def get_all_dic(self):
        return WordYomiOrg()

    def get_index(self, x):
        info("Not implement.")
        raise

    def length(self):
        db_status, session, db_status_msg = get_db_status(DB_CONNECTION_NAME)
        if not session:
            debug("No session for add, " + db_status_msg)
            return None
        word_count = session.query(Word.yomi).count()
        return word_count

    def add_index_form_text(self, text):
        changed = False
        for yomi, word in self._process(text):
            self.add(yomi, word, commit=False)
            changed = True
        if changed:
            transaction.commit()


    def _create_all_index_obj(self, index_data):
        count = 0
        for texts in index_data:
            for yomi, word in texts:
                assert isinstance(yomi, unicode)
                assert isinstance(word, unicode)
                if len(yomi) < 3: # ignore if less than 3 character
                    continue
                self.add(yomi, word, commit=False)
                count += 1
                if count / 100 == 0:
                    transaction.commit()
        if count and count / 100 != 100:
            transaction.commit()


if USE_SQL:
    WordsForFuzzy = WordsForFuzzyBySQL
InitializeClass(WordsForFuzzy)
