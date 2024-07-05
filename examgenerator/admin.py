from django.contrib import admin
from .models import Topic, Question, Answer, SubQuestion, SubAnswer, SubSubQuestion, SubSubAnswer

admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(SubQuestion)
admin.site.register(SubAnswer)
admin.site.register(SubSubQuestion)
admin.site.register(SubSubAnswer)