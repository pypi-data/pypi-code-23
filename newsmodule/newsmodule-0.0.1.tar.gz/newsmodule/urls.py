# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from . import api_views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^api/tag/$', api_views.TagListView.as_view()),
    url(r'^api/tag/(?P<pk>[0-9]+)/$', api_views.TagDetailView.as_view()),
    url(r'^api/category/$', api_views.CategoryListView.as_view()),
    url(r'^api/category/(?P<pk>[0-9]+)/$', api_views.CategoryDetailView.as_view()),
    url(r'^api/post/$', api_views.PostListView.as_view()),
    url(r'^api/post/(?P<pk>[0-9]+)/$', api_views.PostDetailView.as_view()),
    url(r'api/post/web/', api_views.WebReadPostView.as_view()),
    url(r'api/post/mobile/', api_views.MobileReadPostView.as_view()),
    url(r'api/post/read/', api_views.UserReadPostView.as_view()),
    url(r'api/post/unread/', api_views.UserUnReadPostView.as_view()),
]