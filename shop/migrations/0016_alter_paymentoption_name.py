# Generated by Django 5.0.4 on 2024-09-10 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_paymentoption'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentoption',
            name='name',
            field=models.CharField(choices=[('MPESA', 'M-Pesa Express'), ('INTASEND', 'IntaSend')], max_length=20, unique=True),
        ),
    ]
