# Generated by Django 4.2.6 on 2023-10-16 22:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('help_request', '0007_alter_helprequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='declinedrequest',
            name='declined_request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='declined_request', to='help_request.helprequest'),
        ),
        migrations.AlterField(
            model_name='helprequest',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
