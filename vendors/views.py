from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import VendorShop, VendorShopItem, WithdrawalRequest, Vendor_Order, ProductMinPrice
from shop.models import ShopItem, Category, Education_Level, Subject
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from shop.models import ShopItem
from django.conf import settings
from intasend import APIService
from django.views.decorators.http import require_POST
from shop.views import normalize_phone_number
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.views.decorators.http import require_POST



class VendorShopEditView(View):
    def post(self, request):
        user = request.user
        data = request.POST
        files = request.FILES


        vendor_shop = get_object_or_404(VendorShop, user=user)

        name = data.get('name')
        description = data.get('description')
        logo = files.get('logo')

        if name:
            vendor_shop.name = name
        if description:
            vendor_shop.description = description
        if logo:
            vendor_shop.logo = logo

        vendor_shop.save()

        response_data = {
            'status': 'success',
            'message': 'Shop details updated successfully.'
        }

        return JsonResponse(response_data)







class AddShopItemView(View):
    def post(self, request):
        data = request.POST

        # Print received data for debugging
        print("Received data:", data)

        title = data.get('title')
        category_id = data.get('category')
        education_level_id = data.get('education_level')
        subject_id = data.get('subject')
        description = data.get('description')
        new_price = data.get('new_price')
        old_price = data.get('old_price')
        file = request.FILES.get('file')

        # Print extracted data for debugging
        print("Extracted data - Title:", title)
        print("Extracted data - Category ID:", category_id)
        print("Extracted data - Education Level ID:", education_level_id)
        print("Extracted data - Subject ID:", subject_id)
        print("Extracted data - Description:", description)
        print("Extracted data - New Price:", new_price)
        print("Extracted data - Old Price:", old_price)
        print("Extracted data - File:", file)

        if not all([title, description, new_price, old_price, file]):
            missing_fields = []
            if not title:
                missing_fields.append('title')
            if not description:
                missing_fields.append('description')
            if not new_price:
                missing_fields.append('new_price')
            if not old_price:
                missing_fields.append('old_price')
            if not file:
                missing_fields.append('file')

            error_message = f"Please provide the following fields: {', '.join(missing_fields)}"
            return JsonResponse({'status': 'success', 'message': error_message})

        try:
            min_price_obj = ProductMinPrice.objects.latest('id')
            min_price = min_price_obj.price
        except ProductMinPrice.DoesNotExist:
            min_price = 50

        print("Minimum price:", min_price)

        if float(new_price) < min_price:
            return JsonResponse({'status': 'error', 'message': f'The required minimum new price is Ksh {min_price}.'})

        category = get_object_or_404(Category, id=category_id)
        education_level = get_object_or_404(Education_Level, id=education_level_id)
        subject = get_object_or_404(Subject, id=subject_id)

        shop_item = ShopItem.objects.create(
            title=title,
            category=category,
            education_level=education_level,
            subject=subject,
            description=description,
            price=new_price,
            old_price=old_price,
            file=file
        )

        vendor_shop = get_object_or_404(VendorShop, user=request.user)

        vendor_shop_item = VendorShopItem.objects.create(
            shop=vendor_shop,
            item=shop_item,
            created_at=timezone.now()
        )

        # Print success message for debugging
        print("Product added successfully.")

        response_data = {
            'status': 'success',
            'message': 'Product added successfully.'
        }

        return JsonResponse(response_data)








@csrf_exempt
def delete_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')

            vendor_shop_item = get_object_or_404(ShopItem, id=item_id)

            vendor_shop_item.delete()

            return JsonResponse({'status': 'success', 'message': 'Product deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Failed to delete product.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)





@csrf_exempt
def update_shop_item(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        item_id = data.get('item_id')

        try:
            vendor_shop_item = get_object_or_404(ShopItem, id=item_id)
            print(f"Found ShopItem with ID: {item_id}")

            title = data.get('title')
            category_id = data.get('category')
            education_level_id = data.get('education_level')
            subject_id = data.get('subject')
            description = data.get('description')
            old_price = data.get('old_price')
            new_price = data.get('new_price')


            vendor_shop_item.title = title
            vendor_shop_item.category_id = category_id
            vendor_shop_item.education_level_id = education_level_id
            vendor_shop_item.subject_id = subject_id
            vendor_shop_item.description = description
            vendor_shop_item.old_price = old_price
            vendor_shop_item.price = new_price
            vendor_shop_item.save()


            return JsonResponse({'status': 'success', 'message': 'Product updated successfully.'})
        except ShopItem.DoesNotExist:

            return JsonResponse({'status': 'error', 'message': 'ShopItem does not exist.'})
        except Exception as e:

            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'})




def get_product_details(request, product_id):
    product = get_object_or_404(ShopItem, id=product_id)
    data = {
        'title': product.title,
        'category_id': product.category_id,
        'education_level_id': product.education_level_id,
        'subject_id': product.subject_id,
        'description': product.description,
        'old_price': str(product.old_price),
        'new_price': str(product.price),
    }
    print(data)
    return JsonResponse(data)






@require_POST
def initiate_mpesa_b2c(request):
    try:
        print("Initiating M-Pesa B2C transaction...")

        service = APIService(token=settings.INTASEND_TOKEN)

        mpesa_name = request.POST.get('mpesa_name')
        mpesa_phone_number = request.POST.get('mpesa_phone_number')
        amount = request.POST.get('amount')
        shop_vendor_id = request.POST.get('shop_vendor_id')

        normalized_phone_number = normalize_phone_number(mpesa_phone_number)
        amount = float(amount)

        vendor_shop = get_object_or_404(VendorShop, pk=shop_vendor_id)



        if request.user != vendor_shop.user:
            return JsonResponse({'status': 'Your request couldn\'t be validated.'})

        available_balance = vendor_shop.available_balance

        available_balance = float(available_balance)

        if amount != available_balance:
            return JsonResponse({'status': 'This request couldn\'t be completed. Please refresh the browser and try again.'})

        if available_balance < 500:
            return JsonResponse({'status': 'Your available balance is insufficient. You must have at least Ksh 500 to make a withdrawal request.'})

        if available_balance < amount:
            return JsonResponse({'status': 'Your available balance is insufficient. You must have at least Ksh 500 to make a withdrawal request.'})

        vendor_shop.available_balance = 0
        vendor_shop.save()

        transactions = [
            {'name': mpesa_name, 'account': normalized_phone_number, 'amount': amount, 'narrative': 'Vendor Payment'}
        ]


        response = service.transfer.mpesa(currency='KES', transactions=transactions)
        print("INITIAL RESPONSE:", response)

        tracking_id = response.get('tracking_id')

        print("Tracking ID:", tracking_id)


        withdrawal_request = WithdrawalRequest.objects.create(
            user=request.user,
            name=mpesa_name,
            account=normalized_phone_number,
            amount=amount,
            transaction_status='PENDING',
            tracking_id=tracking_id  
        )

        approved_response = service.transfer.approve(response)

        return JsonResponse({'status': 'M-Pesa transaction initiated and approved successfully. You should receive your funds within minutes.'})

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return JsonResponse({'status': f'Failed to initiate M-Pesa transaction: {str(e)}'})







@csrf_exempt
def withdrawal_webhook(request):
    try:
        print("Withdrawal Webhook: Start")

        webhook_data = json.loads(request.body)
        tracking_id = webhook_data.get('tracking_id')

        if not tracking_id:
            return JsonResponse({'status': 'Tracking ID not found. Try again.'})

        withdrawal_request = WithdrawalRequest.objects.get(tracking_id=tracking_id)

        user = withdrawal_request.user

        vendor_shop = VendorShop.objects.get(user=user)

        transaction_status = None
        transactions = webhook_data.get('transactions', [])
        if transactions:
            transaction_status = transactions[0].get('status')

        if transaction_status == 'Successful':
            with transaction.atomic():
                withdrawal_request.transaction_status = 'SUCCESSFUL'
                withdrawal_request.save()

                vendor_shop.available_balance = 0
                vendor_shop.save()

                vendor_shop.total_earnings += withdrawal_request.amount
                vendor_shop.save()


                vendor_orders = Vendor_Order.objects.filter(vendor=user, order__is_paid=True)
                vendor_orders.update(vendor_is_paid=True)

            return JsonResponse({'status': 'WithdrawalRequest and associated records updated successfully.'})
        else:
            withdrawal_request.transaction_status = 'PENDING'
            withdrawal_request.save()

            return JsonResponse({'status': 'WithdrawalRequest status updated to PENDING.'})

    except WithdrawalRequest.DoesNotExist:
        return JsonResponse({'status': 'WithdrawalRequest not found.'}, status=404)

    except VendorShop.DoesNotExist:
        return JsonResponse({'status': 'VendorShop not found.'}, status=404)

    except Exception as e:
        print(f"Exception in withdrawal_webhook: {e}")
        return JsonResponse({'status': f'Error in withdrawal_webhook: {str(e)}'}, status=500)






@login_required
@csrf_exempt
def update_phone_number(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_phone_number = data.get('phone_number')
            user = request.user
            user.phone_number = new_phone_number
            user.save()

            return JsonResponse({'status': 'Phone number updated successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'Invalid JSON data.'}, status=400)
    return JsonResponse({'status': 'Invalid request method.'}, status=405)





@login_required
@require_POST
def change_password_view(request):
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        user = request.user

        if not authenticate(request, email=user.email, password=current_password):
            return JsonResponse({'message': 'Your current password is incorrect.'})

        user.set_password(new_password)
        user.save()

        return JsonResponse({'message': 'Password changed successfully. You must login again.'})
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON data'})

