# coding: utf-8
from django.conf.urls import patterns, url
from .views import (
    home_fonte_externa,
    criar_fonte_externa,
    detalhe_fonte_externa,
    editar_fonte_externa,
    excluir_fonte_externa,
    sincronizar_fonte_externa,
)

urlpatterns = patterns(
    "",
    url(r"^$", home_fonte_externa, name="home_fonte_externa"),
    url(r"^criar/$", criar_fonte_externa, name="criar_fonte_externa"),
    url(r"^detalhe/(?P<id>\d+)/$", detalhe_fonte_externa, name="detalhe_fonte_externa"),
    url(r"^editar/(?P<id>\d+)/$", editar_fonte_externa, name="editar_fonte_externa"),
    url(r"^excluir/(?P<id>\d+)/$", excluir_fonte_externa, name="excluir_fonte_externa"),
    url(r"^sincronizar/(?P<id>\d+)/$", sincronizar_fonte_externa, name="sincronizar_fonte_externa"),
)
