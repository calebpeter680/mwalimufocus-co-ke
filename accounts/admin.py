from django.contrib import admin
from .models import CustomUser, CustomerFAQ, VendorFAQ


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'date_joined', 'is_vendor', 'is_new')

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