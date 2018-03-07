# Copyright (C) 2017 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.interface import implements, alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from .i18n import _
from .db import ObjectBase, Table
from .interfaces import IProviderSchema, IProvider
from .article import Articles


class Provider(ObjectBase, Articles):
  implements(IProvider)

  _SCHEMA_ = IProviderSchema
  _CONTEXT_FIELD_MAP_ = dict(provider_id="id")

class Providers(Table):
  _TABLE_ = "reseller.provider"
  _FACTORY_ = Provider
  
providers = Providers()


def vocabulary(unused):
  return SimpleVocabulary(tuple(
    SimpleTerm(p.id, title=p.title)
    for p in providers.list()
    ))
alsoProvides(vocabulary, IVocabularyFactory)
