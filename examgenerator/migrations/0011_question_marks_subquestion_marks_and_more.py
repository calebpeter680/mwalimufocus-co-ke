# Generated by Django 5.0.4 on 2024-07-16 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('examgenerator', '0010_markingscheme'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='marks',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='subquestion',
            name='marks',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='subsubquestion',
            name='marks',
            field=models.IntegerField(default=1),
        ),
    ]
