from django.contrib.sitemaps import Sitemap
from .models import ShopItem, Category
from pages.models import TopLevelPage, TeamMember
from django.urls import reverse
from django.db.models import Count


class ShopItemSitemap(Sitemap):
    changefreq = "Daily"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ShopItem.objects.filter(is_search_engine_indexible=True).order_by('id')

    def lastmod(self, obj):
        return obj.date_created


class TopLevelPageSitemap(Sitemap):
    changefreq = "Weekly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return TopLevelPage.objects.all().order_by('id')

    def lastmod(self, obj):
        return obj.created_at


class TeamMemberSitemap(Sitemap):
    changefreq = "Weekly"
    priority = 0.2
    protocol = "https"

    def items(self):
        return TeamMember.objects.all().order_by('id')

    def lastmod(self, obj):
        return obj.created_at



class CategorySitemap(Sitemap):
    changefreq = "Daily"
    priority = 1.0
    protocol = "https"

    def items(self):
        return Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0).order_by('id')

    def lastmod(self, obj):
        return obj.created_at


class StaticViewSitemap(Sitemap):
    priority = 0.4
    changefreq = 'Weekly'
    protocol = "https"

    def items(self):
        return ['home', 'categories', 'all_team_members']

    def location(self, item):
        return reverse(item)