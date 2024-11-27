from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from validate_email_address import validate_email
from decimal import Decimal



def send_payment_reminders():
    print("send_payment_reminders Job Initiated")
    from shop.models import Discount, Order, PaymentReminderLog
    try:
        latest_discount = Discount.objects.latest('id')
    except ObjectDoesNotExist:
        latest_discount = Discount.objects.create(amount=20)
    discount_decimal = Decimal(latest_discount.amount) / 100
    unpaid_orders = Order.objects.select_related('user').filter(is_paid=False, cart_reminder_sent=False, user__isnull=False)

    for order in unpaid_orders:
        user = order.user
        if not user:
            continue

        if not order.items.exists():
            continue

        if not validate_email(user.email):
            continue

        user_orders = Order.objects.filter(user=user)
        if user_orders.filter(items__in=order.items.all(), is_paid=True).exists():
            continue

        if user_orders.filter(items__in=order.items.all(), cart_reminder_sent=True).exists():
            continue

        for item in order.items.all():
            if item.is_discounted and item.discount_amount is not None:
                remaining_discount_time = item.discount_end_time - timezone.now()
                if remaining_discount_time.total_seconds() < 1200: 
                    item.discount_end_time += timezone.timedelta(minutes=20) - remaining_discount_time
                    item.save()
            else:
                item.price = item.price * (1 - discount_decimal)
                item.is_discounted = True
                item.discount_amount = latest_discount.amount
                item.discount_start_time = timezone.now()
                item.discount_end_time = item.discount_start_time + timezone.timedelta(minutes=20)
                item.save()


        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        html_message = render_to_string('payment_reminder_email.html', {
            'user': user,
            'order': order,
            'domain': current_site.domain,
            'protocol': 'https' if settings.SECURE_SSL_REDIRECT else 'http',
            'discount_amount': latest_discount.amount,
            'items': order.items.all()
        })

        plain_message = strip_tags(html_message)
        subject = f"🔔 Payment Reminder: {latest_discount.amount}% Discount on Your Order! 🏷️"

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True
        )

        PaymentReminderLog.objects.create(user=user, order=order)

        order.cart_reminder_sent = True
        order.save()



def restore_item_prices():
    print("restore_item_prices Job Initiated")
    from shop.models import ShopItem
    now = timezone.now()
    discounted_items = ShopItem.objects.filter(is_discounted=True)

    for item in discounted_items:
        if item.discount_end_time and item.discount_end_time <= now:
            discount_amount = item.discount_amount
            if discount_amount is None:
                try:
                    latest_discount = Discount.objects.latest('id')
                    discount_amount = latest_discount.amount
                except Discount.DoesNotExist:
                    discount_amount = 30

            discount_decimal = Decimal(discount_amount) / 100
            original_price = item.price / (1 - discount_decimal)
            item.price = original_price
            item.is_discounted = False
            item.discount_amount = None
            item.discount_start_time = None
            item.discount_end_time = None
            item.save()