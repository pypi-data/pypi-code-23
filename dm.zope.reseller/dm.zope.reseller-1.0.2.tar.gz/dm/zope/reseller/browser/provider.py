# Copyright (C) 2017 by Dr. Dieter Maurer <dieter@handshake.de>
"""`Provider` related views."""
from zope.interface import Invalid

from z3c.form.interfaces import WidgetActionExecutionError

from ..provider import Providers as ProvidersCollection

from .view import CrudMixin, CrudAddForm
from .traversal import Proxy, CollectionProxy, Constant, Namespace

class Providers(CollectionProxy):
  obj = Constant(ProvidersCollection())

class ProvidersCrud(CrudMixin):
  def item_delete_check(self, item): return item.id != -3

class Provider(CollectionProxy): pass

class ProviderAddForm(CrudAddForm):
  """this adds an article."""
  def createAndAdd(self, data):
    collection = self._crud().context.obj
    order_no = data.pop("provider_order_no", "").strip()
    if collection.list((("provider_order_no", order_no),)):
      raise WidgetActionExecutionError(
        "provider_order_no",
        Invalid(_("We already have an article with this provider order no"))
        )
    data.update(dict(
      provider_id=collection.id,
      provider_order_no=order_no,
      ))
    return super(ProviderAddForm, self).createAndAdd(data)

from .article import BaseArticlesCrud
class ProviderCrud(BaseArticlesCrud):
  ADD_FORM_FACTORY = ProviderAddForm

from .article import BaseArticlesSearch
class ProviderArticlesSearch(BaseArticlesSearch):
  def set_condition(self, form, data):
    super(ProviderArticlesSearch, self).set_condition(form, data)
    if self.condition is not None:
      self.condition.append(("provider_id", form.context.obj.id, "="))
