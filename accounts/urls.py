from django.urls import path
from . import views


from django.contrib.auth import views as auth_views

urlpatterns = [
    path('vendor/sign-up/', views.vendor_sign_up, name='vendor_sign_up'),
    path('customer/sign-up/', views.customer_sign_up, name='customer_sign_up'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('api/create-subscriber/', views.create_subscriber_from_json, name='create_subscriber_from_json'),
]
