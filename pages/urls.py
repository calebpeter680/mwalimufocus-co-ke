from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.top_level_page_view, name='top_level_page'),
    path('our-team/member/<int:member_id>/<slug:slug>/', views.team_member_detail, name='team_member_detail'),
    path('team/all-members/', views.all_team_members, name='all_team_members'),
]
