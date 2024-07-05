from django.urls import path
from . import views

urlpatterns = [
    path('save_question/', views.save_question_data, name='save_question'),
    path('get_topics/', views.get_topics, name='get_topics'),
]
