from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Topic, Question, Answer, SubQuestion, SubAnswer, SubSubQuestion, SubSubAnswer



def get_topics(request):
    education_level_id = request.GET.get('education_level_id')
    subject_id = request.GET.get('subject_id')
    topics = Topic.objects.filter(education_level_id=education_level_id, subject_id=subject_id).values('id', 'name')
    topics_list = list(topics)
    return JsonResponse(topics_list, safe=False)



@csrf_exempt
def save_question_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        topic_id = data.get('topic_id')
        question_text = data.get('question_text')
        answer_text = data.get('answer_text')
        sub_questions = data.get('sub_questions', [])
        
        try:
            topic = Topic.objects.get(id=topic_id)
            question = Question.objects.create(topic=topic, question_text=question_text)
            answer = Answer.objects.create(question=question, answer_text=answer_text)
            
            for sub_question_data in sub_questions:
                sub_question_text = sub_question_data.get('sub_question_text')
                sub_answer_text = sub_question_data.get('sub_answer_text')
                sub_question = SubQuestion.objects.create(question=question, sub_question_text=sub_question_text)
                sub_answer = SubAnswer.objects.create(sub_question=sub_question, sub_answer_text=sub_answer_text)
                
                sub_sub_questions = sub_question_data.get('sub_sub_questions', [])
                for sub_sub_question_data in sub_sub_questions:
                    sub_sub_question_text = sub_sub_question_data.get('sub_sub_question_text')
                    sub_sub_answer_text = sub_sub_question_data.get('sub_sub_answer_text')
                    sub_sub_question = SubSubQuestion.objects.create(sub_question=sub_question, sub_sub_question_text=sub_sub_question_text)
                    sub_sub_answer = SubSubAnswer.objects.create(sub_sub_question=sub_sub_question, sub_sub_answer_text=sub_sub_answer_text)
            
            response_data = {
                'status': 'success',
                'message': 'Question and associated data saved successfully.'
            }
            
            return JsonResponse(response_data)
        
        except Topic.DoesNotExist:
            response_data = {
                'status': 'error',
                'message': 'Topic with ID {} does not exist.'.format(topic_id)
            }
            return JsonResponse(response_data, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)


