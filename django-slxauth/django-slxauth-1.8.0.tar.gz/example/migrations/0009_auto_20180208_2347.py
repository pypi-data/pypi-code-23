import django.contrib.auth.validators
from django.db import migrations, models


def populate_usernames(apps, schema_editor):
    User = apps.get_model('example', 'MyUser')
    for u in User.objects.all().iterator():
        if u.um_id:
            u.username = 'um_%s' % u.um_id
        else:
            u.username = 'user_%s' % u.id
        u.save()


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0008_auto_20180208_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='username',
            field=models.CharField(null=True,
                                   error_messages={'unique': 'A user with that username already exists.'},
                                   help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                   max_length=150, unique=True,
                                   validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                                   verbose_name='username'),
        ),
        migrations.RunPython(populate_usernames),
        migrations.AlterField(
            model_name='myuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                   help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                   max_length=150, unique=True,
                                   validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                                   verbose_name='username'),
        )
    ]
