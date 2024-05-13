from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.top_level_page_view, name='top_level_page'),
    path('team-members/<int:member_id>/', views.team_member_detail, name='team_member_detail'),
]
