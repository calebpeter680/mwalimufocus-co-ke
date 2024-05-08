from django.db import models
from accounts.models import CustomUser
from shop.models import ShopItem, Order
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class VendorShop(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='vendor_shop')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True, upload_to='shop_logos/')
    created_at = models.DateTimeField(default=timezone.now)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.name



class VendorShopItem(models.Model):
    shop = models.ForeignKey(VendorShop, on_delete=models.CASCADE, related_name='items')
    item = models.OneToOneField(ShopItem, on_delete=models.CASCADE, related_name='vendor_shop_item')
    created_at = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"{self.shop.name} - {self.item.title}"



class Vendor_Order(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)  
    display_order_number = models.CharField(max_length=100, null=True, blank=True)
    vendor_is_paid = models.BooleanField(default=False)  

    def __str__(self):
        return f"Vendor Order for {self.shop_item.title} by {self.vendor.email}"



class VendorCommission(models.Model):
    percentage = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return str(self.percentage)


 

class WithdrawalRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    account = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_status = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    tracking_id = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"Withdrawal Request for {self.user.email}"





class ProductMinPrice(models.Model):
    price = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return str(self.price)