from django.db import models
from shop.models import Education_Level, Subject

class Topic(models.Model):
    name = models.CharField(max_length=1000)
    education_level = models.ForeignKey(Education_Level, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    image = models.ImageField(upload_to='questionimages/', null=True, blank=True)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer', null=True, blank=True)
    answer_text = models.TextField()
    image = models.ImageField(upload_to='answerimages/', null=True, blank=True)

    def __str__(self):
        return self.answer_text

class SubQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='sub_questions')
    sub_question_text = models.TextField()
    image = models.ImageField(upload_to='subquestionimages/', null=True, blank=True)

    def __str__(self):
        return self.sub_question_text

    class Meta:
        verbose_name = "Sub Question"
        verbose_name_plural = "Sub Questions"

class SubAnswer(models.Model):
    sub_question = models.OneToOneField(SubQuestion, on_delete=models.CASCADE, related_name='sub_answer', null=True, blank=True)
    sub_answer_text = models.TextField()
    image = models.ImageField(upload_to='subanswerimages/', null=True, blank=True)

    def __str__(self):
        return self.sub_answer_text

class SubSubQuestion(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='sub_sub_questions')
    sub_sub_question_text = models.TextField()
    image = models.ImageField(upload_to='subsubquestionimages/', null=True, blank=True)

    def __str__(self):
        return self.sub_sub_question_text

    class Meta:
        verbose_name = "SubSub Question"
        verbose_name_plural = "SubSub Questions"

class SubSubAnswer(models.Model):
    sub_sub_question = models.OneToOneField(SubSubQuestion, on_delete=models.CASCADE, related_name='sub_sub_answer')
    sub_sub_answer_text = models.TextField()
    image = models.ImageField(upload_to='subsubanswerimages/', null=True, blank=True)

    def __str__(self):
        return self.sub_sub_answer_text
