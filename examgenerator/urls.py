from django.urls import path
from . import views

urlpatterns = [
    path('save_question/', views.save_question_data, name='save_question'),
    path('get_topics/', views.get_topics, name='get_topics'),
    path('generate_pdf/<int:topic_id>/', views.generate_pdf, name='generate_pdf'),
]
