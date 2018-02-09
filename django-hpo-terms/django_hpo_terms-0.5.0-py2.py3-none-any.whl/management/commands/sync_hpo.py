from django.core.management import BaseCommand

from hpo_terms import utils


class Command(BaseCommand):
    help = 'Sync HPO from online resource'

    def handle(self, *args, **options):
        utils.sync_from_hpo()
