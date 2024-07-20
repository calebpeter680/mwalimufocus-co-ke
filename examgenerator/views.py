from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import GeneratedExam, MarkingScheme, InstructionsToExaminees, Topic, Question, Answer, SubQuestion, SubAnswer, SubSubQuestion, SubSubAnswer
from shop.models import Category, Subject, Education_Level, Brand, Order
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.urls import reverse
from .tasks import generate_pdf_task
from celery.result import AsyncResult
from django.conf import settings
from django.db.models import Count
from accounts.models import SocialMediaLinks
from django.shortcuts import redirect, reverse
from django.shortcuts import get_object_or_404, render


def generated_exam_preview(request):
    task_id = request.session.get('task_id')
    print("Task ID:", task_id)

    if task_id:
        generated_exam = GeneratedExam.objects.filter(task_id=task_id).first()

        marking_scheme = getattr(generated_exam, 'marking_scheme', None)
    else:
        generated_exam = None
        marking_scheme = None
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]
    brand = Brand.objects.last()
    subjects_with_items = Subject.objects.annotate(num_items=Count('shopitem'))
    education_levels_with_items = Education_Level.objects.annotate(num_items=Count('shopitem'))

    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None

    context = {
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'brand': brand,
        'subjects_with_items': subjects_with_items,
        'education_levels_with_items': education_levels_with_items,
        'latest_link': latest_link,
        'generated_exam': generated_exam,
        'marking_scheme': marking_scheme,
    }

    return render(request, 'generated_exam_preview.html', context)






def fetch_topics(request):
    education_level_ids = request.GET.getlist('education_level_ids[]')
    subject_id = request.GET.get('subject_id')

    if education_level_ids and subject_id:
        topics = Topic.objects.filter(
            education_level__name__in=education_level_ids,
            subject_id=subject_id,
            question__isnull=False  # Ensure there is at least one associated question
        ).distinct()  

        topics_data = [
            {
                'id': topic.id,
                'name': topic.name,
                'education_level': topic.education_level.name
            }
            for topic in topics
        ]
        return JsonResponse({'topics': topics_data})
    
    return JsonResponse({'topics': []})







def exam_data_preparation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            school_name = data.get('school_name')
            academic_term = data.get('academic_term')
            assessment_type = data.get('assessment_type')
            education_level = data.get('education_level')
            exam_type = data.get('exam_type')
            subjects = data.get('subjects')
            month = data.get('month')
            year = data.get('year')
            exam_duration = data.get('exam_duration')
            max_score = data.get('max_score')
            instructions = data.get('instructions', [])
            topics = data.get('topics', [])

            task = generate_pdf_task.delay(school_name, academic_term, assessment_type, education_level,
                                           exam_type, subjects, month, year, exam_duration, max_score,
                                           instructions, topics)


            if 'task_id' in request.session:
                if request.session['task_id'] != task.id:
                    del request.session['task_id']  
                    request.session['task_id'] = task.id  
            else:
                request.session['task_id'] = task.id  

            return JsonResponse({'status': 'success', 'task_id': request.session.get('task_id')})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



#return redirect(reverse('task_status', args=[task.id]))

def exam_generator_form(request):
    categories_with_items = Category.objects.annotate(num_items=Count('shopitem')).filter(num_items__gt=0)
    menu_items = Category.objects.annotate(num_shopitems=Count('shopitem')).filter(num_shopitems__gt=0).order_by('-num_shopitems')[:5]
    brand = Brand.objects.last()
    subjects_with_items = Subject.objects.annotate(num_items=Count('shopitem'))
    education_levels_with_items = Education_Level.objects.annotate(num_items=Count('shopitem'))
    instructions_to_examinees = InstructionsToExaminees.objects.all()
    subjects = Subject.objects.exclude(name="ALL SUBJECTS").order_by('name')
    education_levels = Education_Level.objects.all().order_by('name')
    try:
        latest_link = SocialMediaLinks.objects.latest('pk')
    except SocialMediaLinks.DoesNotExist:
        latest_link = None
    context = {
        'categories_with_items': categories_with_items,
        'menu_items': menu_items,
        'brand': brand,
        'subjects_with_items': subjects_with_items,
        'education_levels_with_items': education_levels_with_items,
        'latest_link': latest_link,
        'instructions_to_examinees': instructions_to_examinees,
        'subjects': subjects,
        'education_levels': education_levels,
    }

    return render(request, 'exam_generator_form.html', context)





def task_status(request, task_id):
    task = AsyncResult(task_id)
    if task.state == 'SUCCESS':
        result = task.result
        return JsonResponse({'status': 'SUCCESS', 'result': result})
    elif task.state == 'FAILURE':
        return JsonResponse({'status': 'FAILURE', 'error': str(task.info)})
    else:
        return JsonResponse({'status': task.state})



def get_topics(request):
    education_level_id = request.GET.get('education_level_id')
    subject_id = request.GET.get('subject_id')
    topics = Topic.objects.filter(education_level_id=education_level_id, subject_id=subject_id).values('id', 'name')
    topics_list = list(topics)
    return JsonResponse(topics_list, safe=False)





def save_question_data(request):
    if request.method == 'POST':
        try:
            print("Incoming POST data:", request.POST)

            topic_id = request.POST.get('topic_id')
            if not topic_id:
                return JsonResponse({'status': 'error', 'message': 'Topic ID not provided'})

            topic = get_object_or_404(Topic, pk=topic_id)

            question_text = request.POST.get('question_text', '').strip()
            question_image = request.FILES.get('question_image')
            question_marks = request.POST.get('question_marks')
            question_marks = int(question_marks) if question_marks else 0

            if question_text or question_image:
                question = Question.objects.create(
                    topic=topic,
                    question_text=question_text,
                    image=question_image,
                    marks=question_marks
                )

                question.save()

                answer_text = request.POST.get('answer_text', '').strip()
                answer_image = request.FILES.get('answer_image')

                if answer_text or answer_image:
                    answer = Answer.objects.create(
                        question=question,
                        answer_text=answer_text,
                        image=answer_image
                    )

                sub_question_ids = sorted({int(key.split('[')[1].split(']')[0]) for key in request.POST if key.startswith('sub_questions[')})
                for sub_question_id in sub_question_ids:
                    sub_question_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_question_text]', '').strip()
                    sub_question_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_question_image]')
                    sub_question_marks = request.POST.get(f'sub_questions[{sub_question_id}][sub_question_marks]')
                    sub_question_marks = int(sub_question_marks) if sub_question_marks else 0

                    print(f"sub_question_marks (processed): {sub_question_marks}")

                    if sub_question_text or sub_question_image:
                        sub_question = SubQuestion.objects.create(
                            question=question,
                            sub_question_text=sub_question_text,
                            image=sub_question_image,
                            marks=sub_question_marks
                        )

                        sub_question.save()

                        sub_answer_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_answer_text]', '').strip()
                        sub_answer_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_answer_image]')

                        if sub_answer_text or sub_answer_image:
                            SubAnswer.objects.create(
                                sub_question=sub_question,
                                sub_answer_text=sub_answer_text,
                                image=sub_answer_image
                            )

                        sub_sub_question_ids = sorted({int(key.split('[')[3].split(']')[0]) for key in request.POST if key.startswith(f'sub_questions[{sub_question_id}][sub_sub_questions][')})
                        for sub_sub_question_id in sub_sub_question_ids:
                            sub_sub_question_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_question_text]', '').strip()
                            sub_sub_question_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_question_image]')
                            sub_sub_question_marks = request.POST.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_question_marks]')
                            sub_sub_question_marks = int(sub_sub_question_marks) if sub_sub_question_marks else 0

                            if sub_sub_question_text or sub_sub_question_image:
                                sub_sub_question = SubSubQuestion.objects.create(
                                    sub_question=sub_question,
                                    sub_sub_question_text=sub_sub_question_text,
                                    image=sub_sub_question_image,
                                    marks=sub_sub_question_marks
                                )

                                sub_sub_question.save()

                                sub_sub_answer_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_answer_text]', '').strip()
                                sub_sub_answer_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_answer_image]')

                                if sub_sub_answer_text or sub_sub_answer_image:
                                    SubSubAnswer.objects.create(
                                        sub_sub_question=sub_sub_question,
                                        sub_sub_answer_text=sub_sub_answer_text,
                                        image=sub_sub_answer_image
                                    )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})






