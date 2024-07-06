from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ShopItemSitemap, StaticViewSitemap, TopLevelPageSitemap, CategorySitemap, TeamMemberSitemap

sitemaps = {
    'shop_items': ShopItemSitemap,
    'static': StaticViewSitemap,
    'top_level_page': TopLevelPageSitemap,
    'categories': CategorySitemap,
    'team': TeamMemberSitemap,
}

urlpatterns = [
    path('', views.home, name='home'), 
    path('categories/', views.categories_view, name='categories'), 
    path('categories/<slug:category_slug>/', views.CategoryShopItemsView.as_view(), name='category_shop_items'),

    path('<slug:education_level_slug>/category/<slug:category_slug>/', views.shop_items_by_education_level_category, name='shop_items_by_education_level_category'),
    path('subject/<slug:subject_slug>/<slug:category_slug>/', views.shop_items_by_subject_category, name='shop_items_by_subject_category'),

    path('level/<slug:education_level_slug>/<slug:subject_slug>/<slug:category_slug>/', views.shop_items_by_subject_category_education_level, name='shop_items_by_subject_category_education_level'),
    
    path('<slug:category_slug>/<int:pk>/<slug:slug>/', views.shop_item_detail, name='shop_item_detail'),

    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),

    path('checkout/', views.checkout, name='checkout'),

    path('get_cart_items/', views.get_cart_items, name='get_cart_items'),

    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('remove_from_cart_at_checkout/', views.remove_from_cart_at_checkout, name='remove_from_cart_at_checkout'),

    path('trigger_stk_push/', views.stk_push_view, name='trigger_stk_push'),

    path('webhook/v1/', views.webhook_callback, name='webhook_callback'),

    path('payment-status/', views.payment_status, name='payment_status'),

    path('login-and-assign/', views.login_and_assign_user, name='login_and_assign'),

    path('session-order-detail/', views.session_order_detail_view, name='session_order_detail'),

    path('download/<int:shop_item_id>/', views.download_file, name='download_file'),

    path('download_item/<int:item_id>/', views.download_customer_item_file, name='download_customer_item_file'),

    #path('send_attachment_via_email/<int:order_id>/', views.send_email_with_attachments, name='send_email_with_attachments'),

    path('search/', views.search_shop_items, name='search_shop_items'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    path('robots.txt', views.robots_txt, name='robots_txt'),
]

handler404 = 'shop.views.custom_404_view'
