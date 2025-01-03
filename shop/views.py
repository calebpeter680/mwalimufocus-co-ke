from django.shortcuts import render, redirect
from shop.models import PaymentOption, ShopItem, Category, Subject, Education_Level, Brand, Order, Transaction, Customer_Item
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F, Value
from django.views import View
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from intasend import APIService
import json
import requests
from django.urls import reverse
import base64
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from accounts.models import CustomUser, SocialMediaLinks
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import filetype
from django.utils.html import strip_tags
import string
import secrets
from django.utils.safestring import mark_safe
from vendors.models import Vendor_Order, VendorShop, VendorShopItem, VendorCommission
from django.db.models import DecimalField, Sum
from decimal import Decimal
from django.views.decorators.http import require_GET
from django.http import HttpResponseNotFound
from storages.backends.s3boto3 import S3Boto3Storage
from .tasks import send_email_with_attachments_task
import logging
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models.functions import Lower
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


scheduler = BackgroundScheduler()
scheduler.start()


logger = logging.getLogger(__name__)

def search_shop_items(request):
    query = request.GET.get('query', '')
    search_words = query.split()

    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'for', 'nor', 'but', 'if', 'then', 'with', 'without',
        'as', 'at', 'by', 'on', 'in', 'to', 'from', 'about', 'above', 'below', 'this', 'that',
        'those', 'these', 'it', 'its', 'you', 'he', 'she', 'we', 'they', 'us', 'them', 'there',
        'where', 'when', 'how', 'why', 'all', 'any', 'some', 'many', 'few', 'more', 'most',
        'other', 'each', 'every', 'no', 'not', 'none', 'only', 'own', 'same', 'such', 'too',
        'very', 'even', 'how', 'in', 'out', 'up', 'down'
    }


    filtered_search_words = [word for word in search_words if word.lower() not in stop_words]

    if not filtered_search_words:
        return JsonResponse({'shop_items': []})

    search_filter = Q()
    for word in filtered_search_words:
        search_filter |= (
            Q(title__icontains=word) |
            Q(category__name__icontains=word) |
            Q(subject__name__icontains=word) |
            Q(education_level__name__icontains=word)
        )

    queryset = ShopItem.objects.filter(search_filter).select_related(
        'category', 'subject', 'education_level'
    )


    shop_items = []
    for item in queryset:
        match_count = sum(
            word.lower() in (item.title or '').lower() or
            word.lower() in (item.category.name or '').lower() or
            word.lower() in (item.subject.name or '').lower() or
            word.lower() in (item.education_level.name or '').lower()
            for word in filtered_search_words
        )
        

        if match_count > 0:
            shop_items.append({
                'id': item.id,
                'title': item.title,
                'slug': item.slug,
                'category': item.category.name,
                'subject': item.subject.name,
                'education_level': item.education_level.name,
                'price': str(item.price),
                'education_level_slug': item.education_level.slug,
                'subject_slug': item.subject.slug,
                'category_slug': item.category.slug,
                'match_count': match_count,
            })

    sorted_items = sorted(shop_items, key=lambda x: x['match_count'], reverse=True)[:20]

    serialized_items = [
        {
            'id': item['id'],
            'slug': item['slug'],
            'title': item['title'],
            'category': item['category'],
            'subject': item['subject'],
            'education_level': item['education_level'],
            'price': item['price'],
            'education_level_slug': item['education_level_slug'],
            'subject_slug': item['subject_slug'],
            'category_slug': item['category_slug'],
        }
        for item in sorted_items
    ]

    return JsonResponse({'shop_items': serialized_items})








def display_order_number(request, number):
    try:
        input_number = int(number)
        result = input_number + 100234
        return result
    except ValueError:
        return None



def home(request):
    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    session_order_id = request.session.get('session_order_id')
    order_id_1 = request.session.get('order_id')
    print('Session ID:', session_order_id)
    print('Deleted Session ID:', order_id_1)

    shop_items = ShopItem.objects.all()

    popular_downloads = []
    for item in shop_items:
        if item.views_count >= 5000:
            conversion_rate = (item.downloads_count / item.views_count) * 100
            popular_downloads.append((item, conversion_rate))

    popular_downloads.sort(key=lambda x: x[1], reverse=True)

    popular_downloads = popular_downloads[:16] 

    popular_items = [item for item, _ in popular_downloads]

    brand = Brand.objects.last()
    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])
    

    categories_names = [category.name for category in categories_with_items]

    if len(categories_names) > 1:
        last_category = categories_names.pop()
        categories_description = ", ".join(categories_names)
        categories_description += f" and {last_category}"
    else:
        categories_description = categories_names[0] if categories_names else ""

    meta_description = f"Download CBC and 8-4-4 materials and resources, including {categories_description}"

    context = {
        'user': request.user,
        'cart_items': cart_items,
        'num_cart_items': num_cart_items,
        'shop_items': shop_items,
        'popular_items': popular_items,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'meta_description': meta_description,
        'latest_link': latest_link,
    }
    return render(request, 'home.html', context)






def categories_view(request):
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])
    brand = Brand.objects.last()


    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)


    categories_names = [category.name for category in categories_with_items]

    if len(categories_names) > 1:
        last_category = categories_names.pop()
        categories_description = ", ".join(categories_names)
        categories_description += f" and {last_category}"
    else:
        categories_description = categories_names[0] if categories_names else ""

    meta_description = f"Browse CBC and 8-4-4 {categories_description}"

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    context = {'latest_link': latest_link, 'meta_description': meta_description, 'user': request.user, 'cart_items': cart_items, 'num_cart_items': num_cart_items, 'categories_with_items': categories_with_items, 'brand': brand, 'menu_items': menu_items}
    return render(request, 'categories.html', context)





class CategoryShopItemsView(View):
    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        shop_items = ShopItem.objects.filter(category=category)

        paginator = Paginator(shop_items, 30)
        page = request.GET.get('page', 1)
        try:
            paginated_shop_items = paginator.page(page)
        except PageNotAnInteger:
            paginated_shop_items = paginator.page(1)
        except EmptyPage:
            paginated_shop_items = paginator.page(paginator.num_pages)

        categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
        menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

        brand = Brand.objects.last()

        subjects_with_items = Subject.objects.filter(shopitem__category=category).annotate(num_items=Count('shopitem'))

        education_levels_with_items = Education_Level.objects.filter(shopitem__category=category).annotate(num_items=Count('shopitem'))

        try:
            latest_link = SocialMediaLinks.objects.latest('pk')
        except SocialMediaLinks.DoesNotExist:
            latest_link = None

        cart = request.session.get('cart', [])
        cart_items = ShopItem.objects.filter(id__in=cart)  
        num_cart_items = len(cart_items)

        context = {
            'category': category,
            'shop_items': paginated_shop_items,
            'subjects_with_items': subjects_with_items,
            'education_levels_with_items': education_levels_with_items,
            'brand': brand,
            'categories_with_items': categories_with_items,
            'menu_items': menu_items,
            'num_cart_items': num_cart_items,
            'cart_items': cart_items,
            'user': request.user,
            'latest_link': latest_link
        }
        return render(request, 'category_shop_items.html', context)






def shop_items_by_subject_category(request, category_slug, subject_slug):
    category = get_object_or_404(Category, slug=category_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    brand = Brand.objects.last()
    education_levels = (
        Education_Level.objects
        .annotate(num_shop_items=Count('shopitem', filter=Q(shopitem__category=category, shopitem__subject=subject)))
        .filter(num_shop_items__gt=0)  
    )

    shop_items_queryset = ShopItem.objects.filter(category=category, subject=subject)

    # Pagination
    paginator = Paginator(shop_items_queryset, 30) 
    page = request.GET.get('page')

    try:
        shop_items = paginator.page(page)
    except PageNotAnInteger:
        shop_items = paginator.page(1)  
    except EmptyPage:
        shop_items = paginator.page(paginator.num_pages) 

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    context = {
        'category': category,
        'subject': subject,
        'shop_items': shop_items,  # Paginated shop items
        'brand': brand,
        'education_levels': education_levels,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_cart_items': num_cart_items,
        'cart_items': cart_items,
        'user': request.user,
        'latest_link': latest_link,
    }

    return render(request, 'shop_items_by_subject_category.html', context)





def shop_items_by_subject_category_education_level(request, education_level_slug, subject_slug, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    education_level = get_object_or_404(Education_Level, slug=education_level_slug)
    brand = Brand.objects.last()

    shop_items = ShopItem.objects.filter(
        category=category,
        subject=subject,
        education_level=education_level
    )

    paginator = Paginator(shop_items, 32)
    page = request.GET.get('page', 1)
    try:
        paginated_shop_items = paginator.page(page)
    except PageNotAnInteger:
        paginated_shop_items = paginator.page(1)
    except EmptyPage:
        paginated_shop_items = paginator.page(paginator.num_pages)

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    context = {
        'category': category,
        'subject': subject,
        'education_level': education_level,
        'shop_items': paginated_shop_items,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_cart_items': num_cart_items,
        'cart_items': cart_items,
        'user': request.user,
        'latest_link': latest_link
    }

    return render(request, 'shop_items_by_subject_category_education_level.html', context)




def shop_items_by_education_level_category(request, education_level_slug, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    education_level = get_object_or_404(Education_Level, slug=education_level_slug)
    brand = Brand.objects.last()

    shop_items = ShopItem.objects.filter(
        category=category,
        education_level=education_level
    )

    paginator = Paginator(shop_items, 30)
    page = request.GET.get('page', 1)
    try:
        paginated_shop_items = paginator.page(page)
    except PageNotAnInteger:
        paginated_shop_items = paginator.page(1)
    except EmptyPage:
        paginated_shop_items = paginator.page(paginator.num_pages)

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

    subjects = (
        Subject.objects
        .annotate(num_shop_items=Count('shopitem', filter=Q(shopitem__category=category, shopitem__education_level=education_level)))
        .filter(num_shop_items__gt=0)  
    )

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    context = {
        'category': category,
        'education_level': education_level,
        'shop_items': paginated_shop_items,
        'subjects': subjects,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_cart_items': num_cart_items,
        'cart_items': cart_items,
        'user': request.user,
        'latest_link': latest_link
    }

    return render(request, 'shop_items_by_education_level_category.html', context)






@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')

        cart = request.session.get('cart', [])
        if item_id in cart:
            message = "This item is already in your cart. Proceed to checkout or add different items."
        else:
            cart.append(item_id)
            request.session['cart'] = cart
            message = "Item added to cart successfully."

        return JsonResponse({'message': message})
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)





def checkout(request):
    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)
    total_price = sum(item.price for item in cart_items)
    num_items = len(cart_items)
    item_sing_plu = "Item" if num_items == 1 else "Items"
    brand = Brand.objects.last()
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]

    total_old_price = sum(item.old_price for item in cart_items) if total_price > 0 else 0
    percentage_saved = ((total_old_price - total_price) / total_old_price) * 100 if total_old_price > 0 else 0
    percentage_saved = round(percentage_saved, 2)

    order_id = request.session.get('order_id')
    order = None  

    if order_id:
        try:
            order = Order.objects.get(pk=order_id)

            if order.is_paid:
                del request.session['order_id']
                order = Order.objects.create(total_price=total_price)
                order.items.set(cart_items)
                request.session['order_id'] = order.pk
                result = display_order_number(request, order.id)
                order.display_order_number = result
                order.save()
                messages.success(request, f"New order created successfully! Order number: {order.display_order_number}")
            else:
                existing_items = order.items.all()
                if set(cart_items) != set(existing_items):
                    order.items.set(cart_items)
                    order.total_price = total_price
                    order.save()
        except Order.DoesNotExist:
            pass  

    else:
        if cart_items:
            try:
                order = Order.objects.create(total_price=total_price)
                order.items.set(cart_items)
                request.session['order_id'] = order.pk
                result = display_order_number(request, order.id)
                order.display_order_number = result
                order.save()
                messages.success(request, f"New order created successfully! Order number: {order.display_order_number}")
            except Exception as e:
                messages.error(request, f"Failed to place order: {e}")



    request.session['session_order_id'] = order.pk

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    return render(request, 'checkout2.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'num_items': num_items,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'total_old_price': total_old_price,
        'item_sing_plu': item_sing_plu,
        'percentage_saved': percentage_saved,
        'order': order, 
        'user': request.user, 
        'latest_link': latest_link
    })






@csrf_exempt
def get_cart_items(request):
    if 'cart' in request.session:
        cart_items = request.session.get('cart', [])
        num_items = len(cart_items)
        return JsonResponse({'num_items': num_items})
    else:
        return JsonResponse({'num_items': 0})



@csrf_exempt
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', [])

        if str(item_id) in cart:
            cart.remove(str(item_id))
            request.session['cart'] = cart
            request.session.modified = True  
            message = f"Item removed from cart successfully."
        else:
            message = f"Item not found in cart."

        return JsonResponse({'message': message})
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)




@csrf_exempt
def remove_from_cart_at_checkout(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            cart = request.session.get('cart', [])
            if item_id in cart:
                cart.remove(item_id)
                request.session['cart'] = cart
                removed_items = request.session.get('removed_items', [])
                
                if item_id not in removed_items:
                    removed_items.append(item_id)
                    request.session['removed_items'] = removed_items
                    request.session.modified = True 
                
                print(f"Removed Items: {request.session.get('removed_items', [])}")  
                
                return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})




#Start of payment integration

service = APIService(token=settings.INTASEND_TOKEN, publishable_key=settings.INTASEND_PUBLISHABLE_KEY, test=False)


@csrf_exempt
def stk_push_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phonenumber')
        email = request.POST.get('email')
        total_price = request.POST.get('total_price')
        order_id = request.POST.get('order_id')

        if not total_price:
            return JsonResponse({'error': 'Total price not provided.'})

        try:
            total_price = float(total_price)
        except ValueError:
            print("Invalid total price format.")
            return JsonResponse({'error': 'Invalid total price format.'})

        phone_number = normalize_phone_number(phone_number)
        total_price = format_total_price(total_price)

        selected_payment_option = PaymentOption.objects.filter(is_selected=True).order_by('-id').first()

        if not selected_payment_option:
            return JsonResponse({'error': 'No payment option selected.'})

        if selected_payment_option.name == 'MPESA':
            try:
                response = initiate_mpesa_payment(phone_number, email, total_price, order_id)

                response_code = response.get('ResponseCode', None)
                checkout_request_id = response.get('CheckoutRequestID', None)
                customer_message = response.get('CustomerMessage', None)
                response_description = response.get('ResponseDescription', None)

                if response_code == '0':
                    order = get_object_or_404(Order, id=order_id)

                    transaction = Transaction.objects.create(
                        transaction_id=checkout_request_id,
                        status="PROCESSING",
                        order=order
                    )

                    stored_invoice_id = request.session.get('invoice_id')

                    if stored_invoice_id is None:
                        request.session['invoice_id'] = checkout_request_id
                        stored_new_invoice_id = request.session.get('invoice_id')

                    elif stored_invoice_id != checkout_request_id:
                        request.session['invoice_id'] = checkout_request_id
                        stored_new_invoice_id = request.session.get('invoice_id')

                    else:
                        print("Invoice ID already set in session.")

                    next_view_url = "https://mwalimufocus.co.ke/login-and-assign/"
                    headers = {'Content-Type': 'application/json'}
                    payload_next = {
                        'email': email,
                        'phone_number': phone_number,
                        'order_id': order_id
                    }

                    try:
                        r = requests.post(next_view_url, json=payload_next, headers=headers)
                    except requests.exceptions.RequestException as e:
                        print('Request failed:', e)

                    return JsonResponse({'success': True, 'message': customer_message})
                else:
                    return JsonResponse({'error': response_description, 'message': customer_message})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        elif selected_payment_option.name == 'INTASEND':
            try:
                response = service.collect.mpesa_stk_push(
                    phone_number=phone_number,
                    email=email,
                    amount=total_price,
                    narrative="Order Payment"
                )
                print("STK Push Response:", response)

                if response:
                    invoice_id = response['invoice']['invoice_id']
                    status = response['invoice']['state']

                    order = get_object_or_404(Order, id=order_id)

                    transaction = Transaction.objects.create(
                        transaction_id=invoice_id,
                        status=status,
                        order=order
                    )

                    print("Transaction:", transaction)

                    stored_invoice_id = request.session.get('invoice_id')
                    print("Current Invoice ID in Session:", stored_invoice_id)

                    if stored_invoice_id is None:
                        request.session['invoice_id'] = invoice_id
                        stored_new_invoice_id = request.session.get('invoice_id')
                        print("New Invoice ID in Session (Initialized):", stored_new_invoice_id)
                    elif stored_invoice_id != invoice_id:
                        request.session['invoice_id'] = invoice_id
                        stored_new_invoice_id = request.session.get('invoice_id')
                        print("New Invoice ID in Session (Updated):", stored_new_invoice_id)
                    else:
                        print("Invoice ID already set in session.")

                    next_view_url = "https://mwalimufocus.co.ke/login-and-assign/"
                    print("Next View URL:", next_view_url)

                    headers = {'Content-Type': 'application/json'}

                    payload_next = {
                        'email': email,
                        'phone_number': phone_number,
                        'order_id': order_id
                    }

                    try:
                        r = requests.post(next_view_url, json=payload_next, headers=headers)
                        print("Post Request Status Code:", r.status_code)
                        print("Post Request Response:", r.text)

                    except requests.exceptions.RequestException as e:
                        print('Request failed:', e)

                    return JsonResponse({'success': True})
                else:
                    print("Failed to trigger M-Pesa STK Push.")
                    return JsonResponse({'error': 'Failed to trigger M-Pesa STK Push.'})

            except Exception as e:
                print("Exception occurred:", e)
                return JsonResponse({'error': str(e)})

    else:
        print("Invalid request method.")
        return JsonResponse({'error': 'Invalid request method.'})




def format_total_price(total_price):
    try:
        total_price = float(total_price)

        formatted_price = round(total_price)
        
        return formatted_price
    except ValueError:
        raise ValueError("Invalid total price format. Please ensure it's a valid number.")



def normalize_phone_number(phone_number):
    phone_number = phone_number.strip()

    if phone_number.startswith('07'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('7'):
        phone_number = '254' + phone_number
    elif phone_number.startswith('1'):
        phone_number = '254' + phone_number
    elif phone_number.startswith('01'):
        phone_number = '254' + phone_number[1:]

    elif phone_number.startswith('+2547'):
        phone_number = phone_number[1:]

    else:
        pass

    if len(phone_number) != 12:
        raise ValueError('Invalid phone number length. Expected length is 12 digits.')

    return phone_number







def get_mpesa_access_token():


    if not settings.DEVELOPMENT_MODE:

        oauth_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    else:

        oauth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

        print(f"URL: {oauth_url}")
    
    consumer_key = settings.MPESA_CONSUMER_KEY


    consumer_secret = settings.MPESA_CONSUMER_SECRET
    
    auth = requests.auth.HTTPBasicAuth(consumer_key, consumer_secret)
    
    response = requests.get(oauth_url, auth=auth)
    
    if response.status_code == 200:
        access_token = response.json().get('access_token')

        print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Failed to retrieve access token: {response.status_code} - {response.text}")
        return None




def initiate_mpesa_payment(phone_number, email, amount, order_id):
    access_token = get_mpesa_access_token()
    if not access_token:
        return {"error": "Unable to fetch M-Pesa access token"}

    daraja_api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    
    data_to_encode = shortcode + passkey + timestamp

    encoded_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

    order = get_object_or_404(Order, id=order_id)

    account_reference = f"Order #{order.display_order_number or order_id}"

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": encoded_password,  
        "Timestamp": timestamp,        
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": "961835",
        "PhoneNumber": phone_number,
        "CallBackURL": "https://mwalimufocus.co.ke/webhook/",
        "AccountReference": account_reference,
        "TransactionDesc": f"Payment for Order #{order.display_order_number or order_id}"
    }

    response = requests.post(daraja_api_url, json=payload, headers=headers)

    return response.json()







@csrf_exempt
def webhook_callback(request):
    
    if request.method == 'POST':
        try:

            selected_payment_option = PaymentOption.objects.filter(is_selected=True).order_by('-id').first()
            if selected_payment_option is None:
                return JsonResponse({'error': 'No payment option selected'}, status=400)

            event_data = json.loads(request.body.decode('utf-8'))

            if selected_payment_option.name == 'INTASEND':

                invoice_id = event_data.get('invoice_id')
                state = event_data.get('state')

                if invoice_id and state:
                    transaction = get_object_or_404(Transaction, transaction_id=invoice_id)
                    order = transaction.order

                    transaction.status = state
                    transaction.save()

                    if state == 'COMPLETE':

                        order.is_paid = True
                        order.save()
                        scheduler.add_job(send_email_with_attachments_task, 'date', run_date=datetime.now() + timedelta(seconds=2), args=[order.id])

                return JsonResponse({'message': 'IntaSend Webhook received successfully'}, status=200)

            elif selected_payment_option.name == 'MPESA':

                stk_callback = event_data.get('Body', {}).get('stkCallback', {})
                result_code = stk_callback.get('ResultCode')
                result_desc = stk_callback.get('ResultDesc')
                checkout_request_id = stk_callback.get('CheckoutRequestID')
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])


                if result_code == 0:
                    amount = next((item['Value'] for item in callback_metadata if item['Name'] == 'Amount'), None)
                    mpesa_receipt_number = next((item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber'), None)
                    transaction_date = next((item['Value'] for item in callback_metadata if item['Name'] == 'TransactionDate'), None)
                    phone_number = next((item['Value'] for item in callback_metadata if item['Name'] == 'PhoneNumber'), None)



                    transaction = get_object_or_404(Transaction, transaction_id=checkout_request_id)
                    order = transaction.order
                    transaction.status = 'COMPLETE'
                    transaction.save()

                    order.is_paid = True
                    order.save()

                    scheduler.add_job(send_email_with_attachments_task, 'date', run_date=datetime.now() + timedelta(seconds=2), args=[order.id])

                    return JsonResponse({'message': 'M-Pesa payment successful'}, status=200)

                else:

                    transaction = get_object_or_404(Transaction, transaction_id=checkout_request_id)
                    transaction.status = 'FAILED'
                    transaction.save()

                    return JsonResponse({'error': result_desc, 'message': 'M-Pesa payment failed'}, status=400)

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)







@csrf_exempt
def login_and_assign_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            phone_number = data.get('phone_number')
            order_id = data.get('order_id')

            print("Data at Login and Assign User:", data)

            if not email:
                latest_user = CustomUser.objects.order_by('-pk').first()
                if latest_user:
                    unique_suffix = latest_user.pk + 1
                else:
                    unique_suffix = 1
                email = f"usernoemail{unique_suffix}@mwalimufocus.co.ke"

            if not phone_number or not order_id:
                return JsonResponse({'error': 'Missing required data'})

            order = get_object_or_404(Order, id=order_id)
            

            if order.user:
                try:
                    existing_user = CustomUser.objects.get(email=email)
                    order.user = existing_user
                    order.save()
                    
                    return JsonResponse({'success': 'Existing user assigned to order successfully!'})

                except CustomUser.DoesNotExist:
                    if order.user.email != email:
                        order.user.email = email
                        order.user.save()

                    return JsonResponse({'success': 'Order already has a user assigned.'})

            else:
                try:
                    user = CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
                    password = phone_number
                    user = CustomUser.objects.create_user(email=email, phone_number=phone_number, password=password, is_new=True, is_vendor=False)
                    print(f"New user created: {user}")

                order.user = user
                order.save()

                vendor_prices = {}

                for item in order.items.all():
                    
                    vendor_shop_item = VendorShopItem.objects.get(item=item)

                    vendor_shop = vendor_shop_item.shop

                    vendor = vendor_shop.user

                    print("The Vendor Is:", vendor)

                    price = item.price

                    commission = VendorCommission.objects.last()

                    if commission:

                        percentage = commission.percentage

                        final_price = price * (percentage / 100)

                    else:

                        final_price = price * Decimal('0.65')

                    if vendor in vendor_prices:
                        vendor_prices[vendor] += final_price
                    else:
                        vendor_prices[vendor] = final_price

                    vendor_order = Vendor_Order.objects.create(order=order, shop_item=item, vendor=vendor, price=final_price)
                    display_order_number = str(order.display_order_number + vendor_order.id)
                    vendor_order.display_order_number = display_order_number
                    vendor_order.save()

                for vendor, total_price in vendor_prices.items():
                    vendor_shop = VendorShop.objects.get(user=vendor)
                    vendor_shop.available_balance += total_price
                    vendor_shop.save()

                return JsonResponse({'success': 'User assigned to order successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)






@csrf_exempt
def payment_status(request):
    print("Received request:", request.method)

    if request.method == 'GET':
        try:
            invoice_id = request.session.get('invoice_id')
            print("Invoice ID stored in session:", invoice_id)

            if not invoice_id:
                print("Invoice ID not found in session")
                return JsonResponse({'error': 'Invoice ID not found in session'}, status=400)

            transaction = Transaction.objects.filter(transaction_id=invoice_id).order_by('-created_at').first()
            print("Transaction found in database:", transaction)

            if transaction:
                state = transaction.status
                print("Transaction status:", state)

                if state == 'COMPLETE':
                    if 'cart' in request.session:
                        del request.session['cart']
                        print("Removed 'cart' from session")

                return JsonResponse({'state': state}, status=200)
                
            else:
                print("Transaction not found for invoice ID")
                return JsonResponse({'error': 'Transaction not found for invoice ID'}, status=404)

        except Exception as e:
            print("Error occurred:", e)
            return JsonResponse({'error': str(e)}, status=400)

    else:
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request method'}, status=405)




#end of Payment configuration




def shop_item_detail(request, category_slug, pk, slug):
    shop_item = get_object_or_404(ShopItem, category__slug=category_slug, pk=pk, slug=slug)

    if shop_item.old_price > 0:
        percentage_saved = ((shop_item.old_price - shop_item.price) / shop_item.old_price) * 100
    else:
        percentage_saved = 0

    percentage_saved = round(percentage_saved, 2)

    category = Category.objects.filter(slug=category_slug).first()
    
    ShopItem.objects.filter(pk=shop_item.pk).update(views_count=F('views_count') + 1)

    brand = Brand.objects.last()
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]) 

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    order = create_order_for_item(shop_item)

    request.session['session_order_id'] = order.pk

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    if shop_item.category.name == "Exams":

        related_items = ShopItem.objects.filter(
            is_search_engine_indexible=True, 
            category=shop_item.category,
            education_level=shop_item.education_level,
            year=shop_item.year,
            term=shop_item.term,
            term_level=shop_item.term_level
        ).exclude(pk=shop_item.pk)

    elif shop_item.category.name == "Set Book Guides":

        related_items = ShopItem.objects.filter(
            is_search_engine_indexible=True, 
            category=shop_item.category,
            subject=shop_item.subject,
        ).exclude(pk=shop_item.pk)

    elif shop_item.category.name == "Schemes of Work":

        related_items = ShopItem.objects.filter(
            is_search_engine_indexible=True, 
            category=shop_item.category,
            term=shop_item.term,
            education_level=shop_item.education_level,
        ).exclude(pk=shop_item.pk)

    else:

        related_items = ShopItem.objects.filter(
            is_search_engine_indexible=True, 
            category=shop_item.category,
            education_level=shop_item.education_level
        ).exclude(pk=shop_item.pk)



    subject = None
    if 'Kiswahili' in shop_item.subject.name or 'Fasihi' in shop_item.subject.name:
        subject = 'Kiswahili'
    elif 'English' in shop_item.subject.name or 'Literature' in shop_item.subject.name:
        subject = 'English'


    return render(request, 'product_detail.html', {'subject': subject, 'related_items': related_items, 'latest_link': latest_link, 'percentage_saved': percentage_saved,'category': category, 'user': request.user, 'order': order, 'cart_items': cart_items, 'num_cart_items': num_cart_items, 'shop_item': shop_item, 'brand': brand, 'categories_with_items': categories_with_items, 'menu_items': menu_items})





def create_order_for_item(shop_item):
    try:
        order = Order.objects.create(
            total_price=shop_item.price,  
            is_paid=False  
        )


        order.items.add(shop_item)

        order.display_order_number = display_order_number(None, order.pk)
        order.save()

        return order
    except Exception as e:
        print(f"Failed to create order: {e}")
        return None






def session_order_detail_view(request):
    session_order_id = request.session.get('session_order_id')

    if not session_order_id:
        return redirect('home')

    order = get_object_or_404(Order, pk=session_order_id)

    items = None  

    if order.customer_items_created:
        customer_items = order.customer_item_set.all()  
    else:
        items = order.items.all()
        
        customer_items = []

        if order.user:
            for item in items:
                customer_item = Customer_Item.objects.create(
                    title=item.title,
                    category=item.category.name,
                    education_level=item.education_level.name,
                    subject=item.subject.name,
                    file=item.file,
                    user=order.user,
                    order=order
                )

                customer_items.append(customer_item)

                item.downloads_count += 1
                item.save()

            order.customer_items_created = True
            order.save()
        else:
            customer_items = list(order.items.all())

    num_shopitems = len(customer_items)
    item_sing_plu = "Item" if num_shopitems == 1 else "Items"

    brand = Brand.objects.last()
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    context = {
        'order': order,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_shopitems': num_shopitems,
        'item_sing_plu': item_sing_plu,
        'items': items,  
        'customer_items': customer_items,
        'latest_link': latest_link
    }

    return render(request, 'session_order_detail.html', context)








def download_file(request, shop_item_id):
    shop_item = get_object_or_404(ShopItem, id=shop_item_id)
    file = shop_item.file
    response = FileResponse(file)
    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response



def download_customer_item_file(request, item_id):
    customer_item = get_object_or_404(Customer_Item, id=item_id)
    file = customer_item.file
    response = FileResponse(file)
    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response





# def send_email_with_attachments(request, order_id):
#     order = get_object_or_404(Order, pk=order_id)

#     if order.attachments_sent:
#         return JsonResponse({'success': True})

#     order_items = order.items.all()
#     brand = Brand.objects.last()
#     attachments = []

#     for item in order.items.all():
#         attachment_url = f"https://mwalimufocus.nyc3.digitaloceanspaces.com/mwalimufocus/shopitemfiles/{item.file.name}"
#         try:
#             response = requests.get(attachment_url)
#             if response.ok:
#                 content = response.content
#                 mime_type = filetype.guess(content)
#                 if mime_type is not None:
#                     content_type = mime_type.mime
#                     attachments.append((item.file.name, content, content_type))
#                 else:
#                     print(f"Failed to determine file type for {attachment_url}")
#             else:
#                 print(f"Failed to fetch file from {attachment_url}: HTTP {response.status_code}")
#         except Exception as e:
#             print(f"Error attaching file {attachment_url}: {e}")

#     subject = 'Your Order Attachments'
#     message_lines = []

#     message_lines.append(f"Thank you for paying for Order #{order.display_order_number}")

#     if order.user and order.user.is_new:
#         message_lines.append("If you want to achieve UNLIMITED downloads, login to your account using:")
#         message_lines.append(f"Email: {order.user.email}")
#         generated_password = order.user.phone_number
#         message_lines.append(f"Password: {generated_password}")
#         message_lines.append(f"IMPORTANT: Since this password was generated by our system, we encourage you to login to your account and change it. Step 1: Click on My Account and login using the provided password. Step 2: Click on your profile and change the password.")

#     message_lines.append(f"\nPlease confirm if all the attachments are available. If any are missing, please contact support. Our email is {brand.email} and our phone number is {brand.phone_number}.")

#     plain_message = "\n\n".join(message_lines)

#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = order.user.email

#     email = EmailMessage(subject, plain_message, from_email, [to_email])

#     for filename, content, content_type in attachments:
#         email.attach(filename, content, content_type)

#     try:
#         email.send()

#         order.attachments_sent = True
#         order.save()

#         order.user.is_new = False
#         order.user.save()

#         return JsonResponse({'success': True})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error_message': str(e)})



def robots_txt(request):
    content = "User-agent: *\nDisallow: /checkout/\n"
    return HttpResponse(content, content_type="text/plain")




def custom_404_view(request, exception):
    return render(request, '404.html', status=404)





