# Generated by Django 5.0.3 on 2024-04-07 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_myuser_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='age',
            field=models.SmallIntegerField(blank=True, default=None, null=True),
        ),
    ]
