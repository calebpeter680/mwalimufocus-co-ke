from django.contrib import admin
from .models import ExamGeneratorPrices, MarkingScheme, InstructionsToExaminees, Topic, Question, Answer, SubQuestion, SubAnswer, SubSubQuestion, SubSubAnswer, GeneratedExam



class GeneratedExamAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'task_id', 'created_at')


    
admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(SubQuestion)
admin.site.register(SubAnswer)
admin.site.register(SubSubQuestion)
admin.site.register(SubSubAnswer)
admin.site.register(GeneratedExam, GeneratedExamAdmin)
admin.site.register(InstructionsToExaminees)
admin.site.register(MarkingScheme)
admin.site.register(ExamGeneratorPrices)