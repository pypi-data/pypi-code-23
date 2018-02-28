import django.db.models.deletion
import oauth2_provider.generators
import oauth2_provider.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
	initial = True
	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name="Application",
			fields=[
				("id", models.BigAutoField(primary_key=True, serialize=False)),
				("client_id", models.CharField(db_index=True, default=oauth2_provider.generators.generate_client_id, max_length=100, unique=True)),
				("redirect_uris", models.TextField(blank=True, help_text="Allowed URIs list, space separated", validators=[oauth2_provider.validators.validate_uris])),
				("client_type", models.CharField(choices=[("confidential", "Confidential"), ("public", "Public")], max_length=32)),
				("authorization_grant_type", models.CharField(choices=[("authorization-code", "Authorization code"), ("implicit", "Implicit"), ("password", "Resource owner password-based"), ("client-credentials", "Client credentials")], max_length=32)),
				("client_secret", models.CharField(blank=True, db_index=True, default=oauth2_provider.generators.generate_client_secret, max_length=255)),
				("name", models.CharField(blank=True, max_length=255)),
				("skip_authorization", models.BooleanField(default=False)),
				("description", models.TextField(blank=True)),
				("homepage", models.URLField()),
				("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="oauth2_application", to=settings.AUTH_USER_MODEL)),
				("allowed_scopes", models.TextField(blank=True, help_text="Which scopes the application is allowed to request (blank = all scopes)")),
				("created", models.DateTimeField(auto_now_add=True)),
				("updated", models.DateTimeField(auto_now=True)),
				("livemode", models.BooleanField(default=False))
			],
			options={
				"abstract": False,
			},
		),
	]
