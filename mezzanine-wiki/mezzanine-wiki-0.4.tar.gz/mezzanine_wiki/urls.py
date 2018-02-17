from django.conf.urls import url

from .views import *

# Wiki patterns.
urlpatterns = [url("^$", Wiki_index.as_view(), name="wiki_index"),
    url("^pages/$", Wiki_page_list.as_view(), name="wiki_page_list"),
    url("^pages:new/$", Wiki_page_new.as_view(), name="wiki_page_new"),
    url("^pages:changes/$", Wiki_page_changes.as_view(), name="wiki_page_changes"),
    url("^tag:(?P<tag>.*)/$", Wiki_page_list.as_view(), name="wiki_page_list_tag"),
    url("^category:(?P<category>.*)/$", Wiki_page_list.as_view(), name="wiki_page_list_category"),
    url("^author:(?P<username>.*)/$", Wiki_page_list.as_view(), name="wiki_page_list_author"),
    url("^(?P<slug>.*)/history/$", Wiki_page_history.as_view(), name="wiki_page_history"),
    url("^(?P<slug>.*)/history/(?P<rev_id>\d+)/$", Wiki_page_revision.as_view(), name="wiki_page_revision"),
    url("^(?P<slug>.*)/diff/", Wiki_page_diff.as_view(), name="wiki_page_diff"),
    url("^(?P<slug>.*)/revert/(?P<revision_pk>[0-9]+)/$", Wiki_page_revert.as_view(), name="wiki_page_revert"),
    url("^(?P<slug>.*)/undo/(?P<revision_pk>[0-9]+)/$", Wiki_page_undo.as_view(), name="wiki_page_undo"),
    url("^(?P<slug>.*)/edit/$", Wiki_page_edit.as_view(), name="wiki_page_edit"),
    url("^(?P<slug>.*)/$", Wiki_page_detail.as_view(), name="wiki_page_detail"),
]