# Generated by Django 5.0.4 on 2024-05-10 17:08

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_shopitem_is_search_engine_indexible'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopitem',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
