from django.db import models
from django.contrib.auth import get_user_model


class CompanySector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CompanySubSector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CompanySegment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ListingSegment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Stock(models.Model):

    STOCK_TYPE_CHOICES = (
    ('ON', 'Ordinary'),
    ('PN', 'Preffered'),
        )

    symbol = models.CharField(max_length=8)
    stock_type = models.CharField(max_length=2, choices=STOCK_TYPE_CHOICES)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.symbol


class Company(models.Model):


    CATEGORY_CHOICES = (
    ('AL', 'Alerta'),
    ('NC', 'Não Classificada'),
    ('EQ', 'Equilibrada'),
    ('CL', 'Cíclica'),
        )


    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=4)
    stocks = models.ManyToManyField(Stock)
    cnpj = models.CharField(max_length=19)
    activity = models.CharField(max_length=300)
    sector = models.ForeignKey(CompanySector, on_delete=models.CASCADE)
    subsector = models.ForeignKey(CompanySubSector, on_delete=models.CASCADE)
    market_segment = models.ForeignKey(CompanySegment, on_delete=models.CASCADE)
    listing_segment = models.ForeignKey(ListingSegment, on_delete=models.CASCADE)
    market_value = models.CharField(max_length=100, null=True, blank=True)
    ev = models.CharField(max_length=100, null=True, blank=True)
    bookkeeper = models.CharField(max_length=100)
    majority_shareholder = models.CharField(max_length=100)
    site = models.URLField()
    headquarters= models.CharField(max_length=150)
    bovespa_page = models.URLField()
    shareholders = models.PositiveIntegerField()
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    ibov = models.BooleanField(default=False)
    next_balance = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class Broker(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StockProfile(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


    def __str__(self):
        return self.name


class Transaction(models.Model):
    OPERATION_TYPE = (
        ('BUY', 'Buy'),
        ('SEL', 'Sell'),
        ('DIV', 'Dividends'),
        ('SPL', 'Split'),
        ('AGR', 'Aggregation'),)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    profile = models.ForeignKey(StockProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    operation_type = models.CharField(null=True,blank=True,max_length=3, choices=OPERATION_TYPE)
    operation_date = models.DateField()
    shares = models.PositiveIntegerField()
    price = models.DecimalField(decimal_places=9,max_digits=15)
    commission = models.DecimalField(decimal_places=2,max_digits=6)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    notes = models.TextField(null=True,blank=True)

    def __str__(self):
        return '%s' % (str(self.id))

class Balance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
