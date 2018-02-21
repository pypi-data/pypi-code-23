from django.contrib import admin
from .models import Loan, FixedIncome, InvestmentFund

from .stocks.models import Stock, ListingSegment, CompanySector, CompanySubSector, CompanySegment, Broker, Company, Transaction, StockProfile
# Register your models here.

class FilterUserAdmin(admin.ModelAdmin):

	def save_model(self, request, obj, form, change):
		if obj.user == None:
			obj.user = request.user
		obj.save()

	def get_queryset(self, request):
		#qs = admin.ModelAdmin.queryset(self, request)
		qs = super(FilterUserAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(user=request.user)

	def has_change_permission(self, request, obj=None):
		if not obj:
			return True
		if request.user.is_superuser or obj.user == request.user:
			return True
		else:
			return False

	# Set delete permissions as change permissions. If user can change, can also delete
	has_delete_permission = has_change_permission


class LoanAdmin(admin.ModelAdmin):
	list_display = ('date', 'loan_name', 'person', 'value')
	search_fields = ('loan_name', 'person')


class FixedIncomeAdmin(admin.ModelAdmin):
	list_display = ('product_type', 'signer', 'start_date', 'due_date', 'position')
	search_fields = ('product_type', 'signer')


class InvestmentFundAdmin(admin.ModelAdmin):
	list_display = ('ativo', 'fund_type', 'net_value')
	search_fields = ('ativo', 'fund_type',)


class TransactionAdmin(admin.ModelAdmin):
	list_display = ('stock', 'shares', 'price', 'operation_type', 'operation_date','broker',)
	search_fields = ('stock',)
	list_filter = ('stock','operation_type','profile','broker','user')


class BrokerAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


class CompanyAdmin(admin.ModelAdmin):
	list_display = ( 'symbol', 'name', 'sector','category', 'shareholders', 'ibov', 'next_balance',)
	search_fields = ('name','symbol','category', )
	list_filter = ('symbol','sector','ibov', 'category',)

class CompanySectorAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)

class CompanySubSectorAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)

class CompanySegmentAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)

class ListingSegmentAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


class StockAdmin(admin.ModelAdmin):
	list_display = ('symbol', 'stock_type')
	search_fields = ('symbol',)

class StockProfileAdmin(FilterUserAdmin):
	list_display = ('name', 'user' )
	search_fields = ('name',)
	#list_filter = (('user', admin.BooleanFieldListFilter))





#Investments Registrations
admin.site.register(Loan, LoanAdmin)
admin.site.register(FixedIncome, FixedIncomeAdmin)
admin.site.register(InvestmentFund, InvestmentFundAdmin)

# Stocks Registrations
admin.site.register(Stock, StockAdmin)
admin.site.register(ListingSegment, ListingSegmentAdmin)
admin.site.register(CompanySector, CompanySectorAdmin)
admin.site.register(CompanySubSector, CompanySubSectorAdmin)
admin.site.register(CompanySegment, CompanySegmentAdmin)
admin.site.register(Broker, BrokerAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(StockProfile, StockProfileAdmin)
