from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import timedelta
from .models import CustomUser, EmailPerHourLimit, WeeklyPromotionEmail
from shop.models import Customer_Item, ShopItem, Discount, Order, Subject
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from validate_email_address import validate_email


def get_purchased_subjects(user):
  subject_ids = Order.objects.filter(user=user).values_list('items__subject', flat=True)
  subjects = Subject.objects.filter(pk__in=subject_ids)
  return set(subjects) 


def get_new_shop_items(subject_names):
    one_week_ago = timezone.now() - timedelta(days=7)
    new_shop_items = ShopItem.objects.filter(
        subject__name__in=subject_names,
        date_created__gte=one_week_ago
    )
    return new_shop_items



def send_promotional_email(user, new_shop_items):
    latest_discount = Discount.objects.latest('id')
    subject = f"🎉 {latest_discount} Offer! Check Out Our New Resources 📚"

    current_site = Site.objects.get_current()
    context = {
        'user': user,
        'new_shop_items': new_shop_items,
        'domain': current_site.domain,
        'protocol': 'https' if settings.SECURE_SSL_REDIRECT else 'http',
        'latest_discount': latest_discount,

    }
    html_message = render_to_string('promotional_email.html', context)
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )


@shared_task
def send_promotional_emails_to_all_users():
    email_limit_obj = EmailPerHourLimit.objects.first()
    email_limit = email_limit_obj.limit if email_limit_obj else 50

    users = CustomUser.objects.filter(send_promotional_emails_to_all_users_is_sent=False)[:email_limit]
    sent_emails_count = 0

    for user in users:
        if not validate_email(user.email):
            WeeklyPromotionEmail.objects.create(user=user, status='FAILED')
            user.send_promotional_emails_to_all_users_is_sent = True
            user.save(update_fields=['send_promotional_emails_to_all_users_is_sent'])
            continue
        
        subjects = get_purchased_subjects(user)
        if subjects:
            new_shop_items = get_new_shop_items(subjects)
            if new_shop_items:
                try:
                    send_promotional_email(user, new_shop_items)
                    WeeklyPromotionEmail.objects.create(user=user, status='SENT')
                    user.send_promotional_emails_to_all_users_is_sent = True
                    user.save(update_fields=['send_promotional_emails_to_all_users_is_sent'])
                    sent_emails_count += 1
                except Exception as e:
                    WeeklyPromotionEmail.objects.create(user=user, status='FAILED')
    
    return f"Sent promotional emails to {sent_emails_count} users."




@shared_task
def reset_promotional_emails_status():
    try:
        users = CustomUser.objects.all()
        for user in users:
            user.send_promotional_emails_to_all_users_is_sent = False
            user.save(update_fields=['send_promotional_emails_to_all_users_is_sent'])
        
        return f"Reset send_promotional_emails_to_all_users_is_sent for {users.count()} users."
    except Exception as e:
        return f"Failed to reset promotional emails status: {str(e)}"




@shared_task
def apply_discount_to_shop_items():
    try:
        latest_discount = Discount.objects.latest('id')
    except ObjectDoesNotExist:
        return "No discounts found. No items updated."

    discount_percentage = Decimal(latest_discount.amount) / Decimal('100')
    shop_items = ShopItem.objects.all()

    for item in shop_items:
        discounted_price = item.price - (item.price * discount_percentage)
        item.price = discounted_price
        item.save()

    return f"Discount applied to {len(shop_items)} ShopItems"



@shared_task
def remove_discount_from_shop_items():
    try:
        latest_discount = Discount.objects.latest('id')
        discount_percentage = Decimal(latest_discount.amount) / Decimal('100')

        shop_items = ShopItem.objects.all()

        for item in shop_items:
            original_price = item.price / (Decimal('1') - discount_percentage)
            item.price = original_price
            item.save()

        return f"Increased prices of {len(shop_items)} ShopItems"
    except Discount.DoesNotExist:
        return "No Discount objects found in the database."

