from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('vendors/', include('vendors.urls')),
    #path('', include('pages.urls')),
    path('tinymce/', include('tinymce.urls')),

]


