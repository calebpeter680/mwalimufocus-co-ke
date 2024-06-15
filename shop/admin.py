from django.contrib import admin
from shop.models import PaymentReminderLog, Discount, Order, Transaction, Category, Education_Level, Subject, ShopItem, Brand, Customer_Item

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_search_engine_indexible')


@admin.register(PaymentReminderLog)
class PaymentReminderLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'reminder_sent_at')
    list_filter = ('user', 'reminder_sent_at')
    search_fields = ('user__email', 'order__id')

    def user(self, obj):
        return obj.user.email

    def order(self, obj):
        return obj.order.display_order_number

    user.admin_order_field = 'user__email'
    order.admin_order_field = 'order__display_order_number'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'display_order_number', 
        'user',
        'is_paid', 
        'total_price', 
        'attachments_sent', 
        'created_at', 
        'cart_reminder_sent'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(user__isnull=True)


admin.site.register(Category)
admin.site.register(Education_Level)
admin.site.register(Subject)
admin.site.register(Brand)
admin.site.register(Transaction)
admin.site.register(Customer_Item)
admin.site.register(Discount)
