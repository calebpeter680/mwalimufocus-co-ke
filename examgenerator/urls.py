from django.urls import path
from . import views

urlpatterns = [
    path('save_question/', views.save_question_data, name='save_question'),
    path('get_topics/', views.get_topics, name='get_topics'),
    path('fetch-topics/', views.fetch_topics, name='fetch_topics'),
    path('generate/', views.exam_generator_form, name='exam_generator_form'),
    path('task_status/<task_id>/', views.task_status, name='task_status'),
    path('exam-data-preparation/', views.exam_data_preparation, name='exam_data_preparation'),
    path('generated-exam-preview/', views.generated_exam_preview, name='generated_exam_preview'),

]
