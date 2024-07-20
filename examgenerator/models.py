from django.db import models
from shop.models import Education_Level, Subject
from accounts.models import CustomUser
from django.db.models import Sum

class Topic(models.Model):
    name = models.CharField(max_length=1000)
    education_level = models.ForeignKey(Education_Level, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Question(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    image = models.ImageField(upload_to='questionimages/', null=True, blank=True)
    marks = models.IntegerField(default=1, null=True, blank=True)


    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs)
        if self.sub_questions.exists():
            total_marks = self.sub_questions.aggregate(Sum('marks'))['marks__sum'] or 0
            if self.marks != total_marks:
                self.marks = total_marks
                super(Question, self).save(*args, **kwargs)

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
    marks = models.IntegerField(default=1, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(SubQuestion, self).save(*args, **kwargs)  
        if self.sub_sub_questions.exists():
            total_marks = self.sub_sub_questions.aggregate(Sum('marks'))['marks__sum'] or 0
            if self.marks != total_marks:
                self.marks = total_marks
                super(SubQuestion, self).save(*args, **kwargs)  
        self.question.save() 


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
    marks = models.IntegerField(default=1, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(SubSubQuestion, self).save(*args, **kwargs)
        self.sub_question.save()

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



class GeneratedExam(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    file = models.FileField(upload_to='generated_exams/', null=True, blank=True)
    task_id = models.CharField(max_length=300, null=True, blank=True)
    assessment_type = models.CharField(max_length=300, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.title



class ExamGeneratorPrices(models.Model):
    exam_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    assignment_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Exam Price: {self.exam_price}, Assignment Price: {self.assignment_price}"



class MarkingScheme(models.Model):
    generated_exam = models.OneToOneField(GeneratedExam, on_delete=models.CASCADE, related_name='marking_scheme')
    file = models.FileField(upload_to='marking_schemes/', null=True, blank=True)

    def __str__(self):
        return f"Marking Scheme for {self.generated_exam.title}"


class InstructionsToExaminees(models.Model):
    text = models.CharField(max_length=250)

    def __str__(self):
        return self.text[:100]
