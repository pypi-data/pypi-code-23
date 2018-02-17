from django.conf.urls import  url
from . import views_page,views_site,views_editor


urlpatterns = [
     url(r'site/edit/$', views_site.Edit.as_view(),name='site_edit' ),

     url(r'add/upload/$', views_page.Upload_File.as_view(),name='page_add_upload' ),
     url(r'add/links/$', views_page.Edit_Links.as_view(),name='page_add_links' ),
     url(r'add/$', views_page.Add.as_view(),name='page_add' ),
     url(r'list/$', views_page.List.as_view(),name='page_list' ),
     url(r'(?P<slug>.*)/edit/links/$', views_page.Edit_Links.as_view(),name='page_edit_links' ),
     url(r'(?P<slug>.*)/edit/images/$', views_page.Edit_Images.as_view(),name='page_edit_images' ),
     url(r'(?P<slug>.*)/edit/editor/add$', views_editor.Add.as_view(),name='editor_add' ),
     url(r'(?P<slug>.*)/edit/editor/delete/(?P<editor>.*)/$', views_editor.Delete.as_view(),name='editor_delete' ),
     url(r'(?P<slug>.*)/edit/$', views_page.Edit.as_view(),name='page_edit' ),
     url(r'(?P<slug>.*)/delete/$', views_page.Delete.as_view(),name='page_delete' ),

]

