# Generated by Django 5.0.4 on 2024-06-15 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_order_cart_reminder_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopitem',
            name='discount_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='shopitem',
            name='discount_end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shopitem',
            name='discount_start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shopitem',
            name='is_discounted',
            field=models.BooleanField(default=False),
        ),
    ]
