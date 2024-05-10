from django.contrib.sitemaps import Sitemap
from .models import ShopItem
from django.urls import reverse


class ShopItemSitemap(Sitemap):
    changefreq = "Daily"
    priority = 1.0

    def items(self):
        return ShopItem.objects.filter(is_search_engine_indexible=True)

    def lastmod(self, obj):
        return obj.date_created



class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home', 'categories']

    def location(self, item):
        return reverse(item)