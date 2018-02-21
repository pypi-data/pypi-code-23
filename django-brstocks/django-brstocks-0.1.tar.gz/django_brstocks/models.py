"""Investments Model."""
from django.db import models
from django.contrib.auth import get_user_model


class Loan(models.Model):
    loan_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    value = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=50)
    person = models.CharField(max_length=150)

    def __str__(self):
        return "%s - %s" % (self.person, self.loan_name)


class FixedIncome(models.Model):

    product_type = models.CharField(max_length=50)
    signer = models.CharField(max_length=100)
    start_date = models.DateField()
    due_date = models.DateField()
    validity_date = models.DateField()
    tax = models.CharField(max_length=50)
    available_amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=50)
    guarantee = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=50)
    start_amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=50)
    position = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=50)

    def __str__(self):
        return "%s - %s" % (self.product_type, self.signer)


class InvestmentFund(models.Model):
    FUND_TYPE_CHOICES = (
    ('RF', 'Renda Fixa'),
    ('MM', 'Multimercado'),
    ('FI', 'Fundo Imobiliário'),)

    ativo = models.CharField(max_length=100, unique=True)
    quota_date = models.DateField()
    quota_value = models.DecimalField(blank=True, null=True, decimal_places=8, max_digits=50)
    quote_amount = models.DecimalField(blank=True, null=True, decimal_places=8, max_digits=50)
    position = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=50)
    net_value = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=50)
    fund_type = models.CharField(max_length=2, choices=FUND_TYPE_CHOICES)

    def __str__(self):
        return self.ativo
