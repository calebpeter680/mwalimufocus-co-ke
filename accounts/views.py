import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, CustomerFAQ, VendorFAQ, Subscriber
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from shop.models import ShopItem, Category, Subject, Education_Level, Brand, Order, Transaction, Customer_Item
from django.db.models import Count, Q
from vendors.models import VendorShop, VendorShopItem, Vendor_Order, VendorCommission, WithdrawalRequest, ProductMinPrice
from django.db.models import Sum, Subquery, OuterRef, Max, Exists
from decimal import Decimal
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags



def dashboard_view(request):

    if not request.user.is_authenticated:
        return redirect('home')

    brand = Brand.objects.last()
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]

    user_email = request.session.get('user_email')
    print("User Email:", user_email)

    context = {
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
    }

    if user_email:
        try:
            user = CustomUser.objects.get(email=user_email)

            if user.is_superuser:
                now = timezone.now()
                one_day_ago = now - timezone.timedelta(days=1)
                two_days_ago = now - timezone.timedelta(days=2)
                one_week_ago = now - timezone.timedelta(weeks=1)
                two_weeks_ago = now - timezone.timedelta(weeks=2)
                one_month_ago = now - timezone.timedelta(days=30)


                users_today = CustomUser.objects.filter(date_joined__gte=one_day_ago).count()
                users_yesterday = CustomUser.objects.filter(date_joined__gte=two_days_ago, date_joined__lt=one_day_ago).count()

                context['users_today'] = users_today
                context['users_yesterday'] = users_yesterday


                percentage_difference_users = 0
                if users_yesterday != 0:
                    percentage_difference_users = ((users_today - users_yesterday) / users_yesterday) * 100

                percentage_difference_users = round(percentage_difference_users, 2)
                context['percentage_difference_users'] = percentage_difference_users


                def get_total_price(filter_date=None, filter_range=None):
                    transactions = Transaction.objects.filter(status='COMPLETE') 

                    if filter_date:
                        transactions = transactions.filter(created_at__gte=filter_date)
                    if filter_range:
                        transactions = transactions.filter(created_at__range=filter_range)

                    transactions = transactions.exclude(
                        Q(order__user__phone_number='0714477986') |
                        Q(order__user__phone_number='254714477986')
                    )

                    return transactions.aggregate(total=Sum('order__total_price'))['total'] or Decimal('0.00')


                total_today = get_total_price(one_day_ago)
                total_past_48_hours = get_total_price(two_days_ago)
                total_past_week = get_total_price(one_week_ago)
                total_past_two_weeks = get_total_price(two_weeks_ago)
                total_past_month = get_total_price(one_month_ago)
                total_all_time = get_total_price()
                total_one_day_ago_to_two_days_ago = get_total_price(filter_range=[two_days_ago, one_day_ago])

                context['total_today'] = total_today
                context['total_past_48_hours'] = total_past_48_hours
                context['total_past_week'] = total_past_week
                context['total_past_two_weeks'] = total_past_two_weeks
                context['total_past_month'] = total_past_month
                context['total_all_time'] = total_all_time


                percentage_difference = 0
                if total_one_day_ago_to_two_days_ago != 0:
                    percentage_difference = ((total_today - total_one_day_ago_to_two_days_ago) / total_one_day_ago_to_two_days_ago) * 100


                percentage_difference = round(percentage_difference, 2)

                context['percentage_difference'] = percentage_difference


                all_orders_with_latest_transaction = Order.objects.annotate(
                    has_transaction=Exists(
                        Transaction.objects.filter(order_id=OuterRef('pk'))
                    ),
                    latest_transaction_created_at=Subquery(
                        Transaction.objects.filter(order_id=OuterRef('pk')).order_by('-created_at').values('created_at')[:1]
                    )
                ).filter(
                    Q(has_transaction=True) &  
                    Q(user__phone_number__isnull=False) &  
                    Q(user__phone_number__gt='') &  
                    ~Q(user__phone_number__in=['0714477986', '254714477986'])  
                ).prefetch_related('items').order_by('-pk')

                context['all_orders'] = all_orders_with_latest_transaction



                all_transactions = Transaction.objects.all().order_by('-pk')
                context['all_transactions'] = all_transactions



                total_paid_orders_today = Order.objects.filter(is_paid=True, created_at__gte=one_day_ago).count()
                total_orders_today = Order.objects.filter(created_at__gte=one_day_ago).count()
                conversion_rate_today = (total_paid_orders_today / total_orders_today) * 100 if total_orders_today != 0 else 0
                
                conversion_rate_today = round(conversion_rate_today, 2)

                total_paid_orders_yesterday = Order.objects.filter(is_paid=True, created_at__range=[two_days_ago, one_day_ago]).count()
                total_orders_yesterday = Order.objects.filter(created_at__range=[two_days_ago, one_day_ago]).count()
                conversion_rate_yesterday = (total_paid_orders_yesterday / total_orders_yesterday) * 100 if total_orders_yesterday != 0 else 0
                percentage_difference_conversion = ((conversion_rate_today - conversion_rate_yesterday) / conversion_rate_yesterday) * 100 if conversion_rate_yesterday != 0 else 0

                percentage_difference_conversion = round(percentage_difference_conversion, 2)
                
                context['conversion_rate_today'] = conversion_rate_today
                context['percentage_difference_conversion'] = percentage_difference_conversion





            elif user.is_vendor:

                try:

                    min_price_obj = ProductMinPrice.objects.latest('id')
                    min_price = min_price_obj.price

                except ProductMinPrice.DoesNotExist:
                    min_price = 50

                context['min_price'] = min_price

                vendor_faqs = VendorFAQ.objects.all()
                context['vendor_faqs'] = vendor_faqs
                
                vendor_shop = VendorShop.objects.get(user=user)
                context['vendor_shop'] = vendor_shop

                vendor_withdrawal_requests = WithdrawalRequest.objects.filter(user=user).order_by('-created_at')
                context['vendor_withdrawal_requests'] = vendor_withdrawal_requests

                vendor_orders = Vendor_Order.objects.filter(vendor=user).order_by('-created_at')
                context['vendor_orders'] = vendor_orders

                vendor_shop_items = VendorShopItem.objects.filter(shop=vendor_shop).order_by('-created_at')
                context['vendor_shop_items'] = vendor_shop_items

                vendor_shop_items_count = vendor_shop_items.count()
                context['vendor_shop_items_count'] = vendor_shop_items_count

                sing_plu_items = "product" if vendor_shop_items_count == 1 else "products"
                context['sing_plu_items'] = sing_plu_items

                shop_items = [vendor_shop_item.item for vendor_shop_item in vendor_shop_items]

                orders = Order.objects.filter(items__in=shop_items)
                paid_orders = orders.filter(is_paid=True)
                context['total_sales'] = paid_orders.count()

                unpaid_vendor_orders = vendor_orders.filter(vendor_is_paid=False, order__is_paid=True)

                available_balance = sum(order.price for order in unpaid_vendor_orders if order.price is not None)

                vendor_shop.available_balance = Decimal(str(available_balance))

                vendor_shop.save()

                categories = Category.objects.all().order_by('name')
                context['categories'] = categories
                education_levels = Education_Level.objects.all()
                context['education_levels'] = education_levels
                subjects = Subject.objects.all().order_by('name')
                context['subjects'] = subjects
            
            else:

                customer_faqs = CustomerFAQ.objects.all()
                context['customer_faqs'] = customer_faqs

                try:
                    user = CustomUser.objects.get(email=user_email)
                    customer_items = Customer_Item.objects.filter(user=user).order_by('-created_at')
                    context['customer_items'] = customer_items
                except CustomUser.DoesNotExist:
                    pass

        except CustomUser.DoesNotExist:
            pass

    return render(request, 'dashboard.html', context)






def vendor_sign_up(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
        agree_to_terms = data.get('agree_to_terms')

        if email and password and phone_number:
            try:
                existing_user = CustomUser.objects.get(email=email)
                return JsonResponse({'error': 'User with this email exists! Login or reset forgotten password'})
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.create_user(email=email, password=password, phone_number=phone_number, is_vendor=True)
                except ValueError as e:
                    return JsonResponse({'error': str(e)})


                request.session['user_email'] = email


                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)

                    shop_name = email.split('@')[0]
                    try:
                        shop = VendorShop.objects.create(user=user, name=shop_name)
                        return JsonResponse({'success': 'Sign up successful! Shop created and you are logged in successfully!'})
                    except Exception as e:
                        return JsonResponse({'error': f'Failed to create shop: {e}'})

        return JsonResponse({'error': 'Invalid form data'})

    return JsonResponse({'error': 'Invalid request method'})






def customer_sign_up(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
        agree_to_terms = data.get('agree_to_terms')
        is_vendor = data.get('is_vendor', False)

        if email and password:
            try:
                existing_user = CustomUser.objects.get(email=email)
                return JsonResponse({'error': 'User with this email exists! Login or reset forgotten password'})
            except ObjectDoesNotExist:
                try:
                    user = CustomUser.objects.create_user(email=email, password=password, phone_number=phone_number, is_vendor=is_vendor)
                except ValueError as e:
                    return JsonResponse({'error': str(e)})

                request.session['user_email'] = email

                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({'success': 'Sign up successful! You are logged in successfully!'})

        return JsonResponse({'error': 'Invalid form data'})

    return JsonResponse({'error': 'Invalid request method'})





def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            request.session['user_email'] = email

            response_data = {
                'success': 'Login successful! You will be redirected shortly!',
            }
            return JsonResponse(response_data)

        else:
            return JsonResponse({'error': 'Incorrect Email or Password'})

    else:
        return JsonResponse({'error': 'Invalid request method'})





def logout_view(request):
    logout(request)
    return redirect('home')




 

@csrf_exempt
def create_subscriber_from_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            print(f"Received POST request with data: {data}")

            if email:
                existing_subscriber = Subscriber.objects.filter(email=email).exists()

                if existing_subscriber:
                    print(f"Subscriber with email {email} already exists.")
                    return JsonResponse({'message': 'You are already subscribed to our newsletter.'})
                else:
                    print(f"Creating new subscriber with email {email}.")

                    joined_at = datetime.now()
                    subscriber = Subscriber.objects.create(email=email, joined_at=joined_at)

                    return JsonResponse({'message': 'Thank you! You are successfully subscribed to our newsletter.'})

            else:
                print("Email not provided in the POST data.")
                return JsonResponse({'error': 'Email not provided.'})

        except json.JSONDecodeError:
            print("Invalid JSON format in the request body.")
            return JsonResponse({'error': 'Invalid JSON format.'})

    else:
        print(f"Received {request.method} request, but only POST is allowed.")
        return JsonResponse({'error': 'Method not allowed'}, status=405)





def get_purchased_categories(user):
    customer_items = Customer_Item.objects.filter(user=user)
    categories = set(item.category for item in customer_items)
    return categories



def get_new_shop_items(categories):
    one_week_ago = timezone.now() - timedelta(days=7)
    new_shop_items = ShopItem.objects.filter(
        category__name__in=categories,
        date_created__gte=one_week_ago
    )
    return new_shop_items



def send_promotional_email(user, new_shop_items):
    subject = "Check Out Our New Items Just for You!"
    context = {
        'user': user,
        'new_shop_items': new_shop_items,
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



def send_promotional_emails_to_all_users():
    users = CustomUser.objects.all()
    for user in users:
        categories = get_purchased_categories(user)
        if categories:
            new_shop_items = get_new_shop_items(categories)
            if new_shop_items:
                send_promotional_email(user, new_shop_items)

