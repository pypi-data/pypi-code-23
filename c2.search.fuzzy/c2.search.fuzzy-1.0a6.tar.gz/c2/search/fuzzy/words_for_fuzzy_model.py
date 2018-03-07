
from c2.search.fuzzy.words_for_fuzzy_tool import USE_SQL

if USE_SQL:
    from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Unicode
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relation, backref
    from sqlalchemy import Column, Integer, UniqueConstraint
    Base = declarative_base()
else:
    Base = object

class Word(Base):
    """

    """
    __tablename__ = 'words'
    __table_args__ = tuple(UniqueConstraint('yomi', 'org_word', name='yomi_org_word_2uniq'))

    id = Column(Integer, primary_key=True)
    yomi = Column(Unicode, index=True)
    org_word = Column(Unicode)

    # original = relation("OriginalWord", order_by=OriginalWord.id, backref="word")

    def __init__(self, yomi, org_word):
        self.yomi = yomi
        self.org_word = org_word

    def __repr__(self):
        return "<Word('%s', '%s')>" % (self.yomi, self.org_word)

#
# class OriginalWord(Base):
#     """
#
#     """
#     __tablename__ = 'original_words'
#
#     id = Column(Integer, primary_key=True)
#     # yomi = Column(String) # TODO: check
#     org_word = Column(String)
#     word_id = Column(Integer, ForeignKey('words.id'))
#
#     word = relation(Word, backref=backref('original_words', order_by=id))
#
#     def __init__(self, org_word):
#         # self.yomi = yomi
#         self.org_word = org_word
#
#     def __repr__(self):
#         return "<OrgWord('%s', '%s')>" % (self.org_word, self.word_id)

