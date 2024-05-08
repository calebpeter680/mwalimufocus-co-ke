from django.contrib import admin
from .models import VendorShop, VendorShopItem, Vendor_Order, VendorCommission, WithdrawalRequest, ProductMinPrice

@admin.register(VendorShop)
class VendorShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__email')

@admin.register(VendorShopItem)
class VendorShopItemAdmin(admin.ModelAdmin):
    list_display = ('shop', 'item')
    search_fields = ('shop__name', 'item__title')

@admin.register(Vendor_Order)
class VendorOrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'shop_item')

@admin.register(VendorCommission)
class VendorCommissionAdmin(admin.ModelAdmin):
    list_display = ('percentage',)


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'account', 'transaction_status')


@admin.register(ProductMinPrice)
class ProductMinPriceAdmin(admin.ModelAdmin):
    list_display = ('price',)