# Generated by Django 5.0.4 on 2024-05-13 11:44

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_teammember'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='description',
            field=tinymce.models.HTMLField(),
        ),
    ]