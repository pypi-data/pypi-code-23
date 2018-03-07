from django.contrib import admin
from django.utils.translation import ugettext as _

from sberbank.models import Payment, BankLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'bank_id', 'amount', 'status', 'created', 'updated',
    )
    list_filter = ('status',)
    search_fields = (
        'uid', 'bank_id', 'amount'
    )

    readonly_fields = ('created', 'updated', 'uid')

    fieldsets = (
        (
            None,
            {
                'fields': [
                    ('uid', 'bank_id'),
                    'status',
                    ('amount',),
                ]
            }
        ),
        (
            _('Дополнительно'),
            {
                'classes': ('collapse',),
                'fields': ['details', 'error_code', 'error_message']
            }
        ),
    )


@admin.register(BankLog)
class BankLogAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'payment_id', 'bank_id', 'request_type', 'created',
    )
    list_filter = ('request_type',)
    search_fields = (
        'uid', 'bank_id', 'payment_id'
    )

    readonly_fields = ('created', 'uid', 'payment_id', 'bank_id')

    fieldsets = (
        (
            None,
            {
                'fields': [
                    ('uid', 'payment_id', 'bank_id'),
                    'request_type',
                    'response_json',
                    'response_text',
                ]
            }
        ),
    )
