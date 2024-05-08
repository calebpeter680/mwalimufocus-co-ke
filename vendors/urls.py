from django.urls import path
from .views import VendorShopEditView, AddShopItemView
from . import views

urlpatterns = [
    path('edit-shop/', VendorShopEditView.as_view(), name='edit_vendor_shop'),
    path('add-shop-item/', AddShopItemView.as_view(), name='add_shop_item'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('update-shop-item/', views.update_shop_item, name='update_item'),
    path('api/get-product-details/<int:product_id>/', views.get_product_details, name='get_product_details'),
    path('initiate_mpesa_b2c/', views.initiate_mpesa_b2c, name='initiate_mpesa_b2c'),
    path('withdrawal/webhook/', views.withdrawal_webhook, name='withdrawal_webhook'),
    path('update_phone_number/', views.update_phone_number, name='update_phone_number'),
     path('change-password/', views.change_password_view, name='change_password'),
]
