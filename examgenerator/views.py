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
import random
from datetime import datetime, timedelta


def generate_pdf(request, topic_id):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    try:
        topic = get_object_or_404(Topic, id=topic_id)
    except Http404:
        return FileResponse(buffer, as_attachment=True, filename='error.pdf')

    questions = list(Question.objects.filter(topic=topic))
    random.shuffle(questions)

    # Cover page variables
    subject = "Agriculture"
    time = "90 minutes"  # Placeholder, should be dynamically set based on user input
    term = "Term 1"
    exam_type = "Midterm"
    name_label = "Name: "
    signature_label = "Signature: "
    date_label = "Date: "  # Label for exam date
    school_name = "Nyambaria School"  

    # Function to draw the page number at the top center
    def draw_page_number(page_num):
        p.setFont("Times-Bold", 14)
        page_num_text = f"{page_num}"
        text_width = p.stringWidth(page_num_text, "Times-Bold", 14)
        p.drawString((width - text_width) / 2, height - 0.5 * inch, page_num_text)

    # Create title page
    p.setFont("Times-Bold", 24)
    subject_title = subject.upper()
    text_width = p.stringWidth(subject_title, "Times-Bold", 24)
    x_position = (width - text_width) / 2
    y_position = height - 1.2 * inch  # Adjusted to top margin

    p.drawString(x_position, y_position, subject_title)


    # Draw ducation_Level
    p.setFont("Times-Bold", 18)
    term_type_text = f"Form 1"
    text_width = p.stringWidth(term_type_text, "Times-Bold", 18)
    x_position = (width - text_width) / 2
    y_position -= 0.5 * inch
    p.drawString(x_position, y_position, term_type_text)

    # Draw Term - Type below the title
    p.setFont("Times-Roman", 16)
    term_type_text = f"{term} - {exam_type}"
    text_width = p.stringWidth(term_type_text, "Times-Roman", 16)
    x_position = (width - text_width) / 2
    y_position -= 0.5 * inch
    p.drawString(x_position, y_position, term_type_text)

    # Draw school name
    p.setFont("Times-Bold", 14)
    school_name_text = school_name.upper()
    text_width = p.stringWidth(school_name_text, "Times-Bold", 14)
    x_position = (width - text_width) / 2
    y_position -= 1 * inch
    p.drawString(x_position, y_position, school_name_text)

    # Draw current year and selected time in hours
    current_year = datetime.now().strftime('%Y')
    selected_time_hours = 2.5  # Placeholder, replace with actual user input
    time_text = f"{current_year} - {selected_time_hours} hours"
    text_width = p.stringWidth(time_text, "Times-Roman", 12)
    x_position = (width - text_width) / 2
    y_position -= 0.5 * inch
    p.drawString(x_position, y_position, time_text)


    # Draw Name and Date block
    y_position -= 0.5 * inch
    p.setLineWidth(2)
    p.line(1 * inch, y_position, width - 1 * inch, y_position)  # Top line of block

    y_position -= 0.5 * inch
    p.setFont("Times-Roman", 12)
    p.drawString(1 * inch, y_position, name_label)
    p.drawString(2 * width / 3, y_position, date_label)  # Adjust positioning for date

    # Adjusting the positions for the lines
    name_line_start = 1 * inch + p.stringWidth(name_label, "Times-Roman", 12) + 0.2 * inch
    name_line_end = 2 * width / 3 - 0.2 * inch  # Name line ends at 2/3 of the page
    date_line_start = 2 * width / 3 + p.stringWidth(date_label, "Times-Roman", 12) + 0.2 * inch  # Start after date label
    date_line_end = width - 1 * inch

    p.setDash(1, 2)
    p.line(name_line_start, y_position, name_line_end, y_position)  # Name dotted line
    p.line(date_line_start, y_position, date_line_end, y_position)  # Date dotted line
    p.setDash()

    y_position -= 0.5 * inch
    p.line(1 * inch, y_position, width - 1 * inch, y_position)  # Bottom line of block



    # Add space below the title
    y_position -= 1 * inch

    # Title for instructions (left-aligned)
    p.setFont("Times-Bold", 14)
    title_text = "Instructions"
    p.drawString(1.2 * inch, y_position, title_text)

    # Add space below the title
    y_position -= 0.3 * inch

    # Draw roman numeral instructions
    instructions_list = [
        "Read each question carefully before answering.",
        "Write your answers clearly and legibly.",
        "Answer all questions in the spaces provided.",
    ]

    def draw_instructions(instructions_list, y_position):
        roman_numerals = ['i.', 'ii.', 'iii.', 'iv.', 'v.', 'vi.', 'vii.', 'viii.', 'ix.', 'x.']
        p.setFont("Times-Roman", 12)
        line_spacing = 0.2 * inch  # Adjust line spacing as needed
        for index, instruction in enumerate(instructions_list):
            if y_position - line_spacing < 1 * inch:
                p.showPage()
                draw_page_number(page_num)
                p.setFont("Times-Roman", 12)
                y_position = height - 0.5 * inch

            indent = 1.5 * inch  # Adjust the left margin for instructions
            p.drawString(indent, y_position, f"{roman_numerals[index]} {instruction}")
            y_position -= line_spacing

        return y_position

    y_position = draw_instructions(instructions_list, y_position)



    # Draw FOR EXAMINER'S USE ONLY table
    y_position -= 0.5 * inch  # Add some space before the table

    # Title for the table
    p.setFont("Times-Bold", 14)
    title_text = "FOR EXAMINER'S USE ONLY"
    text_width = p.stringWidth(title_text, "Times-Bold", 14)
    x_position = (width - text_width) / 2
    p.drawString(x_position, y_position, title_text)

    # Table content
    table_start_y = y_position - 0.5 * inch
    table_end_x = width - 1 * inch
    col1_x = 1 * inch
    col2_x = width / 2
    row_height = 0.5 * inch

    # Draw table borders
    p.setLineWidth(1)
    p.rect(col1_x, table_start_y - 2 * row_height, table_end_x - col1_x, 2 * row_height)

    # Draw vertical lines
    p.line(col2_x, table_start_y, col2_x, table_start_y - 2 * row_height)

    # Draw horizontal lines
    p.line(col1_x, table_start_y - row_height, table_end_x, table_start_y - row_height)

    # Fill table content
    p.setFont("Times-Bold", 12)
    p.drawString(col1_x + 0.2 * inch, table_start_y - 0.3 * inch, "Maximum Score")
    p.drawString(col2_x + 0.2 * inch, table_start_y - 0.3 * inch, "Learner's Score")

    # Center the value 80 in the cell and adjust the y-position slightly downwards
    max_score_text = "80"
    max_score_width = p.stringWidth(max_score_text, "Times-Bold", 12)
    max_score_x = col1_x + (col2_x - col1_x - max_score_width) / 2
    max_score_y = table_start_y - row_height + (row_height - 1 * inch) / 2  # Adjust this line
    p.drawString(max_score_x, max_score_y, max_score_text)

    # Leave the Learner's Score cell empty for now
    learner_score_text = ""
    learner_score_width = p.stringWidth(learner_score_text, "Times-Bold", 12)
    learner_score_x = col2_x + (table_end_x - col2_x - learner_score_width) / 2
    learner_score_y = max_score_y  # Use the same y-position adjustment for consistency
    p.drawString(learner_score_x, learner_score_y, learner_score_text)


    p.showPage()

    page_num = 1
    draw_page_number(page_num)

    p.setFont("Times-Roman", 16)
    y_position = height - 1.5 * inch
    lines_per_question = 5

    def draw_text(numbering, text, y_position, indent=0):
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
        nonlocal page_num
        p.setDash(1, 2)
        for _ in range(lines_count):
            if y_position < 1 * inch:
                p.showPage()
                page_num += 1
                draw_page_number(page_num)
                p.setFont("Times-Roman", 16)
                y_position = height - 1.5 * inch  
                p.setDash(1, 2)  
            p.line(1 * inch + indent, y_position, width - 1 * inch, y_position)
            y_position -= 0.3 * inch
        p.setDash()  
        return y_position

    def resize_image(image_url, max_width, max_height):
        try:
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
            return None, 0, 0
        except Exception as e:
            return None, 0, 0

    def draw_image(image_url, width, y_position):
        nonlocal page_num
        img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))

        if img:
            try:
                x = (width - image_width) / 2

                if y_position - image_height - 0.4 * inch < 1 * inch:
                    p.showPage()
                    page_num += 1
                    draw_page_number(page_num)
                    p.setFont("Times-Roman", 16)
                    y_position = height - 1.5 * inch  

                p.drawInlineImage(img, x, y_position - image_height - 0.2 * inch, width=image_width, height=image_height, preserveAspectRatio=True)

                y_position -= image_height + 0.4 * inch

            except Exception as e:
                print(f"Failed to draw resized image: {str(e)}")

    for question_index, question in enumerate(questions, start=1):
        text_height = len(question.question_text.split('\n')) * 12 / 72.0 * inch
        if y_position - text_height < 1 * inch:
            p.showPage()
            page_num += 1
            draw_page_number(page_num)
            p.setFont("Times-Roman", 16)
            y_position = height - 1.5 * inch

        y_position = draw_text(f"{question_index}.", question.question_text, y_position)

        if question.image:
            image_url = question.image.url
            img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
            if img and y_position - image_height - 0.4 * inch < 1 * inch:
                p.showPage()
                page_num += 1
                draw_page_number(page_num)
                p.setFont("Times-Roman", 16)
                y_position = height - 1.5 * inch 

            draw_image(image_url, width, y_position)

            img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
            if img:
                y_position -= image_height + 0.4 * inch

        if question.sub_questions.exists():
            for sub_question_index, sub_question in enumerate(question.sub_questions.all(), start=1):
                roman_index = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'][sub_question_index - 1]

                sub_text_height = len(sub_question.sub_question_text.split('\n')) * 12 / 72.0 * inch
                if y_position - sub_text_height < 1 * inch:
                    p.showPage()
                    page_num += 1
                    draw_page_number(page_num)
                    p.setFont("Times-Roman", 16)
                    y_position = height - 1.5 * inch 

                y_position = draw_text(f"  {roman_index}.", sub_question.sub_question_text, y_position, indent=0.5 * inch)

                if sub_question.image:
                    image_url = sub_question.image.url
                    img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
                    if img and y_position - image_height - 0.4 * inch < 1 * inch:
                        p.showPage()
                        page_num += 1
                        draw_page_number(page_num)
                        p.setFont("Times-Roman", 16)
                        y_position = height - 1.5 * inch 

                    draw_image(image_url, width, y_position)

                    img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
                    if img:
                        y_position -= image_height + 0.4 * inch

                if sub_question.sub_sub_questions.exists():
                    for sub_sub_question_index, sub_sub_question in enumerate(sub_question.sub_sub_questions.all(), start=1):
                        sub_sub_text_height = len(sub_sub_question.sub_sub_question_text.split('\n')) * 12 / 72.0 * inch
                        if y_position - sub_sub_text_height < 1 * inch:
                            p.showPage()
                            page_num += 1
                            draw_page_number(page_num)
                            p.setFont("Times-Roman", 16)
                            y_position = height - 1.5 * inch 

                        y_position = draw_text(f"    {chr(96 + sub_sub_question_index)}.", sub_sub_question.sub_sub_question_text, y_position, indent=1 * inch)

                        if sub_sub_question.image:
                            image_url = sub_sub_question.image.url
                            img, image_width, image_height = resize_image(image_url, int(0.8 * width), int(0.8 * height))
                            if img and y_position - image_height - 0.4 * inch < 1 * inch:
                                p.showPage()
                                page_num += 1
                                draw_page_number(page_num)
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






