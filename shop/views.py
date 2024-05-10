from django.shortcuts import render, redirect
from shop.models import ShopItem, Category, Subject, Education_Level, Brand, Order, Transaction, Customer_Item
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F
from django.views import View
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from intasend import APIService
import json
import requests
from django.urls import reverse
import base64
from datetime import datetime
from django.contrib.auth import authenticate, login
from accounts.models import CustomUser
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import filetype
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import string
import secrets
from django.utils.safestring import mark_safe
from vendors.models import Vendor_Order, VendorShop, VendorShopItem, VendorCommission
from django.db.models import DecimalField, Sum
from decimal import Decimal
from django.views.decorators.http import require_GET




from django.http import JsonResponse
from django.db.models import Q
from .models import ShopItem

@require_GET
def search_shop_items(request):
    query = request.GET.get('query', '')
    search_terms = [char for char in query.lower() if char.isalnum()]  

    queryset = ShopItem.objects.all()

    for term in search_terms:
        queryset = queryset.filter(
            Q(title__icontains=term) |
            Q(category__name__icontains=term) |
            Q(subject__name__icontains=term) |
            Q(education_level__name__icontains=term)
        )

    # Aggregate shop items with counts
    shop_items = {}
    for item in queryset:
        if item.title not in shop_items:
            shop_items[item.title] = {
                'id': item.id,
                'title': item.title,
                'slug': item.slug,
                'category': item.category.name,
                'subject': item.subject.name,
                'education_level': item.education_level.name,
                'price': str(item.price), 
                'education_level_slug': item.education_level_slug,
                'subject_slug': item.subject_slug,
                'category_slug': item.category_slug,
                'count': 1
            }
        else:
            shop_items[item.title]['count'] += 1

    sorted_items = sorted(shop_items.values(), key=lambda x: x['count'], reverse=True)

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
        if item.views_count != 0:
            conversion_rate = (item.downloads_count / item.views_count) * 100
            popular_downloads.append((item, conversion_rate))

    popular_downloads.sort(key=lambda x: x[1], reverse=True)

    popular_downloads = popular_downloads[:16] 

    popular_items = [item for item, _ in popular_downloads]

    brand = Brand.objects.last()
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

    context = {
        'user': request.user,
        'cart_items': cart_items,
        'num_cart_items': num_cart_items,
        'shop_items': shop_items,
        'popular_items': popular_items,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items
    }
    return render(request, 'home.html', context)






def categories_view(request):
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])
    brand = Brand.objects.last()


    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    context = {'user': request.user, 'cart_items': cart_items, 'num_cart_items': num_cart_items, 'categories_with_items': categories_with_items, 'brand': brand, 'menu_items': menu_items}
    return render(request, 'categories.html', context)






class CategoryShopItemsView(View):
    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        shop_items = ShopItem.objects.filter(category=category)

        categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
        menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

        brand = Brand.objects.last()

        subjects_with_items = Subject.objects.filter(shopitem__category=category).annotate(num_items=Count('shopitem'))

        education_levels_with_items = Education_Level.objects.filter(shopitem__category=category).annotate(num_items=Count('shopitem'))

        cart = request.session.get('cart', [])
        cart_items = ShopItem.objects.filter(id__in=cart)  
        num_cart_items = len(cart_items)

        context = {
            'category': category,
            'shop_items': shop_items,
            'subjects_with_items': subjects_with_items,
            'education_levels_with_items': education_levels_with_items,
            'brand': brand,
            'categories_with_items': categories_with_items,
            'menu_items': menu_items,
            'num_cart_items': num_cart_items,
            'cart_items': cart_items,
            'user': request.user,
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

    shop_items = ShopItem.objects.filter(category=category, subject=subject)

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    context = {
        'category': category,
        'subject': subject,
        'shop_items': shop_items,
        'brand': brand,
        'education_levels': education_levels,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_cart_items': num_cart_items,
        'cart_items': cart_items,
        'user': request.user,
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

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    context = {
        'category': category,
        'subject': subject,
        'education_level': education_level,
        'shop_items': shop_items,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_cart_items': num_cart_items,
        'cart_items': cart_items,
        'user': request.user,
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

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5])

    subjects = (
        Subject.objects
        .annotate(num_shop_items=Count('shopitem', filter=Q(shopitem__category=category, shopitem__education_level=education_level)))
        .filter(num_shop_items__gt=0)  
    )

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    context = {
        'category': category,
        'education_level': education_level,
        'shop_items': shop_items,
        'subjects': subjects,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_cart_items': num_cart_items,
        'cart_items': cart_items,
        'user': request.user,
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

    return render(request, 'checkout.html', {
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





service = APIService(token=settings.INTASEND_TOKEN, publishable_key=settings.INTASEND_PUBLISHABLE_KEY, test=False)


def stk_push_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phonenumber')
        email = request.POST.get('email')
        total_price = request.POST.get('total_price')
        order_id = request.POST.get('order_id')

        print("Phone Number:", phone_number)
        print("Email:", email)
        print("Total Price:", total_price)
        print("Order ID:", order_id)

        if not total_price:
            print("Total price not provided.")
            return JsonResponse({'error': 'Total price not provided.'})

        try:
            total_price = float(total_price)
        except ValueError:
            print("Invalid total price format.")
            return JsonResponse({'error': 'Invalid total price format.'})

        phone_number = normalize_phone_number(phone_number)

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

                next_view_url = request.build_absolute_uri(reverse('login_and_assign'))
                print("Next View URL:", next_view_url)

                payload_next = {
                    'email': email,
                    'phone_number': phone_number,
                    'order_id': order_id
                }

                try:
                    r = requests.post(next_view_url, json=payload_next)
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






@csrf_exempt
def webhook_callback(request):
    if request.method == 'POST':
        try:
            event_data = json.loads(request.body.decode('utf-8'))
            print(event_data)


            invoice_id = event_data.get('invoice_id')
            state = event_data.get('state')

            print(state)

            if invoice_id and state:
                transaction = get_object_or_404(Transaction, transaction_id=invoice_id)
                order = transaction.order

                transaction.status = state
                transaction.save()

                if state == 'COMPLETE':
                    order.is_paid = True
                    order.save()

                

            return JsonResponse({'message': 'Webhook received successfully'}, status=200)

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

            if not email or not phone_number or not order_id:
                return JsonResponse({'error': 'Missing required data'})

            order = get_object_or_404(Order, id=order_id)

            if order.user:
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








from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction

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




#end of intensend configuration




def shop_item_detail(request, education_level_slug, subject_slug, category_slug, slug, pk):
    shop_item = get_object_or_404(ShopItem, education_level_slug=education_level_slug, subject_slug=subject_slug, category_slug=category_slug, slug=slug, pk=pk)
    
    ShopItem.objects.filter(pk=shop_item.pk).update(views_count=F('views_count') + 1)

    brand = Brand.objects.last()
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = (Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]) 

    cart = request.session.get('cart', [])
    cart_items = ShopItem.objects.filter(id__in=cart)  
    num_cart_items = len(cart_items)

    order = create_order_for_item(shop_item)

    request.session['session_order_id'] = order.pk

    return render(request, 'shop_item_detail.html', {'user': request.user, 'order': order, 'cart_items': cart_items, 'num_cart_items': num_cart_items, 'shop_item': shop_item, 'brand': brand, 'categories_with_items': categories_with_items, 'menu_items': menu_items})





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

        for item in items:
            customer_item = Customer_Item(
                title=item.title,
                category=item.category.name,
                education_level=item.education_level.name,
                subject=item.subject.name,
                file=item.file,
                user=order.user,
                order=order
            )
            customer_item.save()
            customer_items.append(customer_item)

            item.downloads_count += 1
            item.save()

        order.customer_items_created = True
        order.save()

    num_shopitems = len(customer_items)
    item_sing_plu = "Item" if num_shopitems == 1 else "Items"

    brand = Brand.objects.last()
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]

    context = {
        'order': order,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'num_shopitems': num_shopitems,
        'item_sing_plu': item_sing_plu,
        'items': items,  
        'customer_items': customer_items,
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





def send_email_with_attachments(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if order.attachments_sent:
        return JsonResponse({'success': True})

    order_items = order.items.all()
    brand = Brand.objects.last()
    attachments = []

    for item in order.items.all():
        attachment_url = f"https://mwalimufocus.nyc3.digitaloceanspaces.com/mwalimufocus/shopitemfiles/{item.file.name}"
        try:
            response = requests.get(attachment_url)
            if response.ok:
                content = response.content
                mime_type = filetype.guess(content)
                if mime_type is not None:
                    content_type = mime_type.mime
                    attachments.append((item.file.name, content, content_type))
                else:
                    print(f"Failed to determine file type for {attachment_url}")
            else:
                print(f"Failed to fetch file from {attachment_url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error attaching file {attachment_url}: {e}")

    subject = 'Your Order Attachments'
    message_lines = []

    message_lines.append(f"Thank you for paying for Order #{order.display_order_number}")

    if order.user and order.user.is_new:
        message_lines.append("If you want to achieve UNLIMITED downloads, login to your account using:")
        message_lines.append(f"Email: {order.user.email}")
        generated_password = order.user.phone_number
        message_lines.append(f"Password: {generated_password}")
        message_lines.append(f"IMPORTANT: Since this password was generated by our system, we encourage you to login to your account and change it. Step 1: Click on My Account and login using the provided password. Step 2: Click on your profile and change the password.")

    message_lines.append(f"\nPlease confirm if all the attachments are available. If any are missing, please contact support. Our email is {brand.email} and our phone number is {brand.phone_number}.")

    plain_message = "\n\n".join(message_lines)

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.user.email

    email = EmailMessage(subject, plain_message, from_email, [to_email])

    for filename, content, content_type in attachments:
        email.attach(filename, content, content_type)

    try:
        email.send()

        order.attachments_sent = True
        order.save()

        order.user.is_new = False
        order.user.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error_message': str(e)})



def robots_txt(request):
    content = "User-agent: *\nDisallow:"
    return HttpResponse(content, content_type="text/plain")





