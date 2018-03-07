import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
	initial = True
	dependencies = []

	operations = [
		migrations.CreateModel(
			name="APIKey",
			fields=[
				("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("api_key", models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
				("full_name", models.CharField(max_length=254)),
				("email", models.EmailField(max_length=254)),
				("website", models.URLField(blank=True)),
				("enabled", models.BooleanField(default=True)),
			],
		),
	]
