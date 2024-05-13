from django.shortcuts import render, get_object_or_404
from .models import TopLevelPage, TeamMember
from shop.models import Brand, Category, ShopItem  
from django.db.models import Count



def team_member_detail(request, member_id):
    team_member = get_object_or_404(TeamMember, pk=member_id)
    brand = Brand.objects.last()

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)

    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]
    

    context = {
        'brand': brand,
        'categories_with_items': categories_with_items,
        'team_member': team_member,
        'menu_items': menu_items

    }
    return render(request, 'team_member_detail.html', context)




def top_level_page_view(request, slug):
    top_level_page = get_object_or_404(TopLevelPage, slug=slug)

    brand = Brand.objects.last()

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)

    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]

    context = {
        'top_level_page': top_level_page,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items
    }

    return render(request, 'top_level_page.html', context)

