from django.contrib import admin
from shop.models import Order, Transaction, Category, Education_Level, Subject, ShopItem, Brand, Customer_Item

admin.site.register(Category)
admin.site.register(Education_Level)
admin.site.register(Subject)
admin.site.register(ShopItem)
admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(Transaction)
admin.site.register(Customer_Item)
