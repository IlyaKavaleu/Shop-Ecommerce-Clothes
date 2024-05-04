# Generated by Django 5.0.3 on 2024-04-24 20:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_remove_stateuserintelegrambot_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='stateuserintelegrambot',
            name='user',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
