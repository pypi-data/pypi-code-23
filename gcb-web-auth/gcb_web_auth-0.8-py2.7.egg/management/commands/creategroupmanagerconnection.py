from django.core.management.base import BaseCommand
from gcb_web_auth.models import GroupManagerConnection


class Command(BaseCommand):
    help = 'Create/Replace GroupManagerConnection record in the database.'

    def add_arguments(self, parser):
        parser.add_argument('account_id', type=str, help='Duke Unique Id used to check grouper')
        parser.add_argument('password', type=str, help='Password used with account_id to access grouper' )

    def handle(self, *args, **options):
        account_id = options['account_id']
        password = options['password']
        gmc = GroupManagerConnection.objects.first()
        if gmc:
            gmc.account_id = account_id
            gmc.password = password
            gmc.save()
        else:
            GroupManagerConnection.objects.create(account_id=account_id, password=password)
