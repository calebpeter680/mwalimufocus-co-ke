from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import timedelta
from .models import CustomUser 
from shop.models import Customer_Item, ShopItem, Discount
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist

def get_purchased_subjects(user):
    customer_items = Customer_Item.objects.filter(user=user)
    subjects = set(item.subject for item in customer_items)
    return subjects

def get_new_shop_items(subject_names):
    one_week_ago = timezone.now() - timedelta(days=7)
    new_shop_items = ShopItem.objects.filter(
        subject__name__in=subject_names,
        date_created__gte=one_week_ago
    )
    return new_shop_items

def send_promotional_email(user, new_shop_items):
    subject = "Check Out Our New Items Just for You!"
    current_site = Site.objects.get_current()
    context = {
        'user': user,
        'new_shop_items': new_shop_items,
        'domain': current_site.domain,
        'protocol': 'https' if settings.SECURE_SSL_REDIRECT else 'http',
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
    user = CustomUser.objects.filter(email='calebpeter4@gmail.com').first()
    if user:
        subjects = get_purchased_subjects(user)
        if subjects:
            new_shop_items = get_new_shop_items(subjects)
            if new_shop_items:
                send_promotional_email(user, new_shop_items)




@shared_task
def apply_discount_to_shop_items():
    try:
        latest_discount = Discount.objects.latest('id')
    except ObjectDoesNotExist:
        return "No discounts found. No items updated."

    discount_percentage = latest_discount.amount / 100
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
        discount_percentage = latest_discount.amount / 100

        shop_items = ShopItem.objects.all()

        for item in shop_items:
            original_price = item.price / (1 - discount_percentage)
            item.price = original_price
            item.save()

        return f"Increased prices of {len(shop_items)} ShopItems"
    except Discount.DoesNotExist:
        return "No Discount objects found in the database."
