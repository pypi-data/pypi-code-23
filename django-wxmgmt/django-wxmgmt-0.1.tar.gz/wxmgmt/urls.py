# coding = utf-8

"""
    @version: v1.0 
    @author: 李大炎 (dayan.li@chinaredstar.com) 
    @contact: 840286247@qq.com 
    @project: PyCharm 
    @file: urls.py 
    @time: 2018/2/25 下午10:55 
"""
from django.urls import path

from . import views

urlpatterns = [
    # ex: /wxmgmt/test/api/
    path('<str:tenantName>/api/', views.api, name='api'),
    path('<str:tenantName>/jsticket/', views.jsticket, name='jsticket')
]