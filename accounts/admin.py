from django.contrib import admin
from .models import EmailSchedule, EmailPerHourLimit, PromotionEmailLog, CustomUser, CustomerFAQ, VendorFAQ, Subscriber, SocialMediaLinks




class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'date_joined', 'is_vendor', 'send_promotional_emails_to_all_users_is_sent', 'is_new')

    list_filter = ('is_active', 'is_staff', 'is_vendor')

    search_fields = ('email', 'phone_number')

    fieldsets = (
        ('User Info', {
            'fields': ('email', 'password', 'phone_number', 'agree_to_terms')
        }),
        ('Permissions', {
            'fields': ('is_new', 'is_active', 'is_staff', 'is_superuser', 'is_vendor', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['email'].label = 'Email'  
        form.base_fields[self.model.USERNAME_FIELD].label = 'Email'  
        return form

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(CustomerFAQ)
class CustomerFAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

@admin.register(VendorFAQ)
class VendorFAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'joined_at')

@admin.register(SocialMediaLinks)
class SocialMediaLinksAdmin(admin.ModelAdmin):
    list_display = ('facebook_url', 'telegram_url', 'whatsapp_url')

@admin.register(EmailPerHourLimit)
class EmailPerHourLimitAdmin(admin.ModelAdmin):
    list_display = ('limit',)

@admin.register(PromotionEmailLog)
class PromotionEmailLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_created', 'status')
    list_filter = ('status', 'date_created')


@admin.register(EmailSchedule)
class EmailScheduleAdmin(admin.ModelAdmin):
    list_display = ('subject', 'start_time', 'is_active')
    list_filter = ('is_active', 'start_time')