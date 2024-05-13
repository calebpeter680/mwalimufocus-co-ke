from django.shortcuts import render, get_object_or_404
from .models import TopLevelPage, TeamMember
from shop.models import Brand, Category, ShopItem  
from django.db.models import Count


def team_member_detail(request, member_id, slug):
    team_member = get_object_or_404(TeamMember, id=member_id, slug=slug)
    brand = Brand.objects.last()

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]

    image_url = team_member.image.url.split('?')[0]

    context = {
        'brand': brand,
        'categories_with_items': categories_with_items,
        'team_member': team_member,
        'menu_items': menu_items,
        'image_url': image_url,
    }
    return render(request, 'team_member_detail.html', context)


def all_team_members(request):
    team_members = TeamMember.objects.all().order_by('id')

    brand = Brand.objects.last()

    latest_founder = TeamMember.objects.filter(is_founder=True).latest('created_at') if TeamMember.objects.filter(is_founder=True).exists() else None
    latest_founder_image_url = latest_founder.image.url.split('?')[0] if latest_founder else None


    non_founders = TeamMember.objects.filter(is_founder=False)

    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]

    context = {
        'team_members': team_members,
        'brand': brand,
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'latest_founder': latest_founder,
        'latest_founder_image_url': latest_founder_image_url,
        'non_founders': non_founders,
    }
    return render(request, 'all_team_members.html', context)


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

