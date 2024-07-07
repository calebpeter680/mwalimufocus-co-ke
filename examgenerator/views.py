from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Topic, Question, Answer, SubQuestion, SubAnswer, SubSubQuestion, SubSubAnswer
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
import io
import os
from django.http import FileResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PIL import Image
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from urllib.parse import urlparse
from django.core.files.base import ContentFile
import urllib
import urllib.error
import urllib.request




def generate_pdf(request, topic_id):
    print(f"Starting PDF generation for topic_id: {topic_id}")
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    try:
        topic = get_object_or_404(Topic, id=topic_id)
        print(f"Fetched topic: {topic.name}")
    except Http404:
        print(f"Topic with id {topic_id} does not exist.")
        return FileResponse(buffer, as_attachment=True, filename='error.pdf')

    questions = Question.objects.filter(topic=topic)
    print(f"Fetched {questions.count()} questions for the topic.")

    p.setFont("Times-Roman", 16)
    p.drawString(1 * inch, height - 1 * inch, f"Exam Paper for Topic: {topic.name}")
    print("Added title to PDF.")

    y_position = height - 1.5 * inch
    lines_per_question = 5

    def draw_text(numbering, text, y_position, indent=0):
        print(f"Drawing text: {text} at y_position: {y_position} with indent: {indent}")
        p.setFont("Times-Bold", 12)
        p.drawString(1 * inch + indent, y_position, numbering)
        p.setFont("Times-Roman", 12)
        max_width = width - 2 * inch - indent - 0.5 * inch

        lines = []
        words = text.split()
        line = ""

        for word in words:
            if p.stringWidth(line + word + " ", "Times-Roman", 12) <= max_width:
                line += word + " "
            else:
                lines.append(line.strip())
                line = word + " "

        if line:
            lines.append(line.strip())

        for line in lines:
            p.drawString(1.5 * inch + indent, y_position, line)
            y_position -= 0.3 * inch

        return y_position


    def draw_lines(y_position, indent=0, lines_count=3):
        print(f"Drawing {lines_count} lines at y_position: {y_position} with indent: {indent}")
        p.setDash(1, 2)
        for _ in range(lines_count):
            if y_position < 1 * inch:
                p.showPage()
                p.setFont("Times-Roman", 16)
                y_position = height - 1.5 * inch  
                p.setDash(1, 2)  
            p.line(1 * inch + indent, y_position, width - 1 * inch, y_position)
            y_position -= 0.3 * inch
        p.setDash()  
        return y_position


    def resize_image(image_url, max_width, max_height):
        try:
            print(f"Trying to insert image from URL: {image_url}")

            img = Image.open(urllib.request.urlopen(image_url))
            original_width, original_height = img.size

            if original_width > max_width:
                ratio = max_width / float(original_width)
                new_width = max_width
                new_height = int(original_height * ratio)
            else:
                new_width = original_width
                new_height = original_height

            img = img.resize((new_width, new_height), Image.LANCZOS)

            return img, new_width, new_height

        except IOError as e:
            print(f"Failed to insert image: IOError - {str(e)}")
            return None, 0, 0
        except Exception as e:
            print(f"Failed to insert image: {str(e)}")
            return None, 0, 0

    def draw_image(image_url, width, y_position):
        img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))

        if img:
            try:
                x = (width - image_width) / 2

                if y_position - image_height - 0.4 * inch < 1 * inch:
                    p.showPage()
                    p.setFont("Times-Roman", 16)
                    y_position = height - 1.5 * inch  

                p.drawInlineImage(img, x, y_position - image_height - 0.2 * inch, width=image_width, height=image_height, preserveAspectRatio=True)

                y_position -= image_height + 0.4 * inch

                print(f"Inserted image at y_position: {y_position}")

            except Exception as e:
                print(f"Failed to draw resized image: {str(e)}")

    for question_index, question in enumerate(questions, start=1):
        print(f"Processing Question {question_index}: {question.question_text}")

        text_height = len(question.question_text.split('\n')) * 12 / 72.0 * inch
        if y_position - text_height < 1 * inch:
            p.showPage()
            p.setFont("Times-Roman", 16)
            y_position = height - 1.5 * inch

        y_position = draw_text(f"{question_index}.", question.question_text, y_position)

        if question.image:
            image_url = question.image.url
            img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
            if img and y_position - image_height - 0.4 * inch < 1 * inch:
                p.showPage()
                p.setFont("Times-Roman", 16)
                y_position = height - 1.5 * inch 

            draw_image(image_url, width, y_position)

            img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
            if img:
                y_position -= image_height + 0.4 * inch

        if question.sub_questions.exists():
            print(f"Question {question_index} has sub-questions.")
            for sub_question_index, sub_question in enumerate(question.sub_questions.all(), start=1):
                roman_index = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'][sub_question_index - 1]
                print(f"Processing Sub-Question {question_index}.{roman_index}: {sub_question.sub_question_text}")

                sub_text_height = len(sub_question.sub_question_text.split('\n')) * 12 / 72.0 * inch
                if y_position - sub_text_height < 1 * inch:
                    p.showPage()
                    p.setFont("Times-Roman", 16)
                    y_position = height - 1.5 * inch 

                y_position = draw_text(f"  {roman_index}.", sub_question.sub_question_text, y_position, indent=0.5 * inch)

                if sub_question.image:
                    image_url = sub_question.image.url
                    # Check if image fits on the current page
                    img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
                    if img and y_position - image_height - 0.4 * inch < 1 * inch:
                        p.showPage()
                        p.setFont("Times-Roman", 16)
                        y_position = height - 1.5 * inch 

                    draw_image(image_url, width, y_position)

                    img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
                    if img:
                        y_position -= image_height + 0.4 * inch

                if sub_question.sub_sub_questions.exists():
                    print(f"Sub-Question {question_index}.{roman_index} has sub-sub-questions.")
                    for sub_sub_question_index, sub_sub_question in enumerate(sub_question.sub_sub_questions.all(), start=1):
                        print(f"Processing Sub-Sub-Question {question_index}.{roman_index}.{sub_sub_question_index}: {sub_sub_question.sub_sub_question_text}")

                        sub_sub_text_height = len(sub_sub_question.sub_sub_question_text.split('\n')) * 12 / 72.0 * inch
                        if y_position - sub_sub_text_height < 1 * inch:
                            p.showPage()
                            p.setFont("Times-Roman", 16)
                            y_position = height - 1.5 * inch 

                        y_position = draw_text(f"    {chr(96 + sub_sub_question_index)}.", sub_sub_question.sub_sub_question_text, y_position, indent=1 * inch)

                        if sub_sub_question.image:
                            image_url = sub_sub_question.image.url
                            img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
                            if img and y_position - image_height - 0.4 * inch < 1 * inch:
                                p.showPage()
                                p.setFont("Times-Roman", 16)
                                y_position = height - 1.5 * inch  

                            draw_image(image_url, width, y_position)

                            img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
                            if img:
                                y_position -= image_height + 0.4 * inch

                        y_position = draw_lines(y_position, indent=1 * inch, lines_count=lines_per_question)

                else:
                    y_position = draw_lines(y_position, indent=0.5 * inch, lines_count=lines_per_question)

        else:
            y_position = draw_lines(y_position, indent=0, lines_count=lines_per_question)

        y_position -= 0.5 * inch

    p.showPage()
    p.save()
    print("Finished PDF generation.")

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'exam_{topic.name}.pdf')









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

            topic = get_object_or_404(Topic, pk=topic_id)

            question_text = request.POST.get('question_text', '').strip()
            question_image = request.FILES.get('question_image')

            if question_text or question_image:
                question = Question.objects.create(
                    topic=topic,
                    question_text=question_text,
                    image=question_image
                )

                answer_text = request.POST.get('answer_text', '').strip()
                answer_image = request.FILES.get('answer_image')

                if answer_text or answer_image:
                    Answer.objects.create(
                        question=question,
                        answer_text=answer_text,
                        image=answer_image
                    )

                sub_question_ids = {key.split('[')[1].split(']')[0] for key in request.POST if key.startswith('sub_questions[')}
                for sub_question_id in sub_question_ids:
                    sub_question_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_question_text]', '').strip()
                    sub_question_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_question_image]')

                    if sub_question_text or sub_question_image:
                        sub_question = SubQuestion.objects.create(
                            question=question,
                            sub_question_text=sub_question_text,
                            image=sub_question_image
                        )

                        sub_answer_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_answer_text]', '').strip()
                        sub_answer_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_answer_image]')

                        if sub_answer_text or sub_answer_image:
                            SubAnswer.objects.create(
                                sub_question=sub_question,
                                sub_answer_text=sub_answer_text,
                                image=sub_answer_image
                            )

                        sub_sub_question_ids = {key.split('[')[3].split(']')[0] for key in request.POST if key.startswith(f'sub_questions[{sub_question_id}][sub_sub_questions][')}
                        for sub_sub_question_id in sub_sub_question_ids:
                            sub_sub_question_text = request.POST.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_question_text]', '').strip()
                            sub_sub_question_image = request.FILES.get(f'sub_questions[{sub_question_id}][sub_sub_questions][{sub_sub_question_id}][sub_sub_question_image]')

                            if sub_sub_question_text or sub_sub_question_image:
                                sub_sub_question = SubSubQuestion.objects.create(
                                    sub_question=sub_question,
                                    sub_sub_question_text=sub_sub_question_text,
                                    image=sub_sub_question_image
                                )

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






