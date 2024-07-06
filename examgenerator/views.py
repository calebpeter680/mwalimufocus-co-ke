from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Topic, Question, Answer, SubQuestion, SubAnswer, SubSubQuestion, SubSubAnswer
from django.core.exceptions import ObjectDoesNotExist



def get_topics(request):
    education_level_id = request.GET.get('education_level_id')
    subject_id = request.GET.get('subject_id')
    topics = Topic.objects.filter(education_level_id=education_level_id, subject_id=subject_id).values('id', 'name')
    topics_list = list(topics)
    return JsonResponse(topics_list, safe=False)





def save_question_data(request):
    if request.method == 'POST':
        try:
            topic_id = request.POST.get('topic_id')
            if not topic_id:
                return JsonResponse({'status': 'error', 'message': 'Topic ID not provided'})

            topic = Topic.objects.get(pk=topic_id)
            question_text = request.POST.get('question_text')
            question_image = request.FILES.get('question_image')

            question = Question.objects.create(
                topic=topic,
                question_text=question_text,
                image=question_image
            )

            answer_text = request.POST.get('answer_text')
            answer_image = request.FILES.get('answer_image')
            if answer_text or answer_image:
                Answer.objects.create(
                    question=question,
                    answer_text=answer_text,
                    image=answer_image
                )

            sub_question_ids = {key.split('[')[1].split(']')[0] for key in request.POST if key.startswith('sub_questions[')}
            for sub_question_id in sub_question_ids:
                sub_question_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_question_text]')
                sub_question_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_question_image]')
                sub_answer_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_answer_text]')
                sub_answer_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_answer_image]')

                sub_question = SubQuestion.objects.create(
                    question=question,
                    sub_question_text=sub_question_text,
                    image=sub_question_image
                )

                if sub_answer_text or sub_answer_image:
                    SubAnswer.objects.create(
                        sub_question=sub_question,
                        sub_answer_text=sub_answer_text,
                        image=sub_answer_image
                    )

                sub_sub_question_ids = {key.split('[')[3].split(']')[0] for key in request.POST if key.startswith(f'sub_questions[{sub_question_id}][sub_sub_questions][')}
                for sub_sub_question_id in sub_sub_question_ids:
                    sub_sub_question_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_question_text]')
                    sub_sub_question_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_question_image]')
                    sub_sub_answer_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_answer_text]')
                    sub_sub_answer_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_answer_image]')

                    sub_sub_question = SubSubQuestion.objects.create(
                        sub_question=sub_question,
                        sub_sub_question_text=sub_sub_question_text,
                        image=sub_sub_question_image
                    )

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






