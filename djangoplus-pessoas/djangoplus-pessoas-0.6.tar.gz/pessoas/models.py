# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from djangoplus.db import models
from enderecos.models import Endereco


class Pessoa(models.Model):

    nome = models.CharField('Nome', search=True, example='Juca da Silva')
    tipo = models.CharField('Tipo', choices=[['Física', 'Física'], ['Jurídica', 'Jurídica']], exclude=True, display=None, example='Física')
    documento = models.CharField('Documento', exclude=True, search=True, display=None, example='000.000.000-00')

    endereco = models.OneToOneField(Endereco, verbose_name='Endereço', null=True, blank=True)

    telefone = models.PhoneField(verbose_name='Telefone', blank=True, null=True, example='(84) 3232-3232')
    email = models.EmailField(verbose_name='E-mail', blank=True, null=True, example='juca.silva@djangoplus.net')

    fieldsets = (
        ('Dados Gerais', {'fields': ('nome',)}),
        ('Endereço', {'fields': ('endereco',)}),
        ('Telefone/E-mail', {'fields': (('telefone', 'email'),)})
    )

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        verbose_female = True
        select_display = 'nome', 'documento'

    def __unicode__(self):
        return self.nome

    def can_add(self):
        return not self.pk


class PessoaFisicaAbstrata(Pessoa):

    cpf = models.CpfField(verbose_name='CPF', search=True, example='000.000.000-00')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento', null=True, blank=True, example='27/08/1984')

    fieldsets = (
        ('Dados Gerais', {'fields': ('nome', ('cpf', 'data_nascimento'))}),
        ('Endereço', {'fields': ('endereco',)}),
        ('Contatos', {'fields': (('telefone', 'email'),)})
    )

    class Meta:
        verbose_name = 'Pessoa Física'
        verbose_name_plural = 'Pessoas Físicas'
        icon = 'fa-user'
        abstract = True

    def save(self, *args, **kwargs):
        self.tipo = 'Física'
        self.documento = self.cpf
        super(PessoaFisicaAbstrata, self).save(*args, **kwargs)


class PessoaJuridicaAbstrata(Pessoa):

    cnpj = models.CnpjField(verbose_name='CNPJ', search=True, example='00.000.000/0001-00')
    inscricao_estadual = models.CharField(verbose_name='Inscrição Estadual', null=True, blank=True)

    fieldsets = (
        ('Dados Gerais', {'fields': ('nome', ('cnpj', 'inscricao_estadual'))}),
        ('Endereço', {'fields': ('endereco',)}),
        ('Contatos', {'fields': (('telefone', 'email'),)})
    )

    class Meta:
        verbose_name = 'Pessoa Jurídica'
        verbose_name_plural = 'Pessoas Jurídicas'
        icon = 'fa-building'
        abstract = True

    def save(self, *args, **kwargs):
        self.tipo = 'Jurídica'
        self.documento = self.cnpj
        super(PessoaJuridicaAbstrata, self).save(*args, **kwargs)
