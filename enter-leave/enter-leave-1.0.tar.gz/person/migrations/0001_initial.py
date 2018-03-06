from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []
    operations = [
        HStoreExtension(),
    ]
