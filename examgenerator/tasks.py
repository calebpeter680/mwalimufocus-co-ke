# examgenerator/tasks.py
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ExamGeneratorPrices, MarkingScheme, InstructionsToExaminees, Topic, Question, Answer, SubQuestion, SubAnswer, SubSubQuestion, SubSubAnswer, GeneratedExam
from shop.models import Subject, Education_Level, Order
from accounts.models import CustomUser
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
from django.urls import reverse
from celery.result import AsyncResult
from django.conf import settings
from django.db.models import Case, When
from django.utils import timezone


def display_order_number(number):
    try:
        input_number = int(number)
        result = input_number + 100234
        return result
    except ValueError:
        return None



@shared_task(bind=True)
def generate_pdf_task(self, school_name, academic_term, assessment_type, education_level,
                      exam_type, subjects, month, year, exam_duration, max_score,
                      instructions, topics):

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter


    try:
        questions_by_topic = {}
        total_available_marks = 0


        
        for topic_id in topics:
            topic = get_object_or_404(Topic, id=topic_id)
            topic_questions = list(Question.objects.filter(topic=topic))
            random.shuffle(topic_questions)
            questions_by_topic[topic_id] = topic_questions
            total_available_marks += sum(q.marks for q in topic_questions)

        if total_available_marks <= int(max_score):
            questions = []
            for topic_id in topics:
                questions.extend(questions_by_topic[topic_id])
        else:
            questions = []
            current_score = 0

            while current_score < int(max_score) and any(questions_by_topic.values()):
                for topic_id in topics:
                    if questions_by_topic[topic_id]:
                        question = questions_by_topic[topic_id].pop(0)
                        if current_score + question.marks <= int(max_score):
                            questions.append(question)
                            current_score += question.marks

                            # If we hit exactly the max score, we can stop early
                            if current_score == int(max_score):
                                break

            # If there is any remaining score to fill, try to fill it with small mark questions
            if current_score < int(max_score):
                remaining_score = int(max_score) - current_score
                small_questions = []
                for topic_id in topics:
                    small_questions.extend([q for q in questions_by_topic[topic_id] if q.marks <= remaining_score])

                # Sort small questions by marks ascending to try and fit the remaining score
                small_questions.sort(key=lambda q: q.marks)
                for question in small_questions:
                    if current_score + question.marks <= int(max_score):
                        questions.append(question)
                        current_score += question.marks

                        if current_score == int(max_score):
                            break

        question_ids_in_order = [question.id for question in questions]
        total_marks = sum(question.marks for question in questions)


        # Cover page variables
        subject = Subject.objects.get(id=subjects).name
        education_level = Education_Level.objects.get(id=education_level).name
        time = exam_duration
        term = academic_term
        exam_type = exam_type
        name_label = "Name: "
        signature_label = "Signature: "
        date_label = "Date: " 
        school_name = school_name 
        assessment_type = assessment_type
        year = year 
        max_score = max_score


        # Function to draw the page number at the top center
        def draw_page_number(page_num):
            p.setFont("Times-Bold", 14)
            page_num_text = f"{page_num}"
            text_width = p.stringWidth(page_num_text, "Times-Bold", 14)
            p.drawString((width - text_width) / 2, height - 0.5 * inch, page_num_text)


        def draw_end_text():
            p.setFont("Times-Bold", 16)
            text_width = p.stringWidth("END", "Times-Bold", 16)
            p.drawString((width - text_width) / 2, inch, "END")

        # Create title page
        p.setFont("Times-Bold", 24)
        subject_title = subject.upper()
        text_width = p.stringWidth(subject_title, "Times-Bold", 24)
        x_position = (width - text_width) / 2
        y_position = height - 1.2 * inch  # Adjusted to top margin

        p.drawString(x_position, y_position, subject_title)


        # Draw ducation_Level
        p.setFont("Times-Bold", 18)
        term_type_text = education_level
        text_width = p.stringWidth(term_type_text, "Times-Bold", 18)
        x_position = (width - text_width) / 2
        y_position -= 0.5 * inch
        p.drawString(x_position, y_position, term_type_text)

        # Draw Term - Type below the title
        p.setFont("Times-Roman", 14)
        if assessment_type == "Exam":
            term_type_text = f"{term} - {exam_type} {assessment_type}"
        else: 
            term_type_text = f"{term} - {assessment_type}"
        text_width = p.stringWidth(term_type_text, "Times-Roman", 16)
        x_position = (width - text_width) / 2
        y_position -= 0.5 * inch
        p.drawString(x_position, y_position, term_type_text)

        # Draw school name
        p.setFont("Times-Bold", 16)
        school_name_text = school_name.upper()
        text_width = p.stringWidth(school_name_text, "Times-Bold", 16)
        x_position = (width - text_width) / 2
        y_position -= 1 * inch
        p.drawString(x_position, y_position, school_name_text)

        # Draw current year and selected time in hours
        current_year = year
        selected_time_hours = time
        time_text = f"{current_year} - {selected_time_hours}"
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
        instructions_list = InstructionsToExaminees.objects.filter(id__in=instructions).values_list('text', flat=True)

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
        max_score_text = str(total_marks)
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
            img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))

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

        def draw_marks(p, y_position, obj, width, indent=0):
            marks_text = "(1 Mark)" if obj.marks == 1 else f"({obj.marks} Marks)"
            text_width = p.stringWidth(marks_text, "Times-Bold", 12)
            p.setFont("Times-Bold", 12)

            max_width = width - 2 * inch - indent - 0.5 * inch
            x_position = width - 1 * inch - text_width 

            p.drawString(x_position, y_position, marks_text)
            return y_position - 12 / 72.0 * inch 



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
                img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))
                if img and y_position - image_height - 0.4 * inch < 1 * inch:
                    p.showPage()
                    page_num += 1
                    draw_page_number(page_num)
                    p.setFont("Times-Roman", 16)
                    y_position = height - 1.5 * inch 

                draw_image(image_url, width, y_position)

                img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))
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
                        img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))
                        if img and y_position - image_height - 0.4 * inch < 1 * inch:
                            p.showPage()
                            page_num += 1
                            draw_page_number(page_num)
                            p.setFont("Times-Roman", 16)
                            y_position = height - 1.5 * inch 

                        draw_image(image_url, width, y_position)

                        img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))
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
                                img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))
                                if img and y_position - image_height - 0.4 * inch < 1 * inch:
                                    p.showPage()
                                    page_num += 1
                                    draw_page_number(page_num)
                                    p.setFont("Times-Roman", 16)
                                    y_position = height - 1.5 * inch  

                                draw_image(image_url, width, y_position)

                                img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))
                                if img:
                                    y_position -= image_height + 0.4 * inch

                            y_position = draw_marks(p, y_position, sub_sub_question, width)
                            y_position = draw_lines(y_position, indent=1 * inch, lines_count=sub_sub_question.marks * 2)

                    else:
                        y_position = draw_marks(p, y_position, sub_question, width)
                        y_position = draw_lines(y_position, indent=0.5 * inch, lines_count=sub_question.marks * 2)

            else:
                y_position = draw_marks(p, y_position, question, width)
                y_position = draw_lines(y_position, indent=0, lines_count=question.marks * 2)

            y_position -= 0.5 * inch

        p.showPage()
        p.save()


        buffer.seek(0)


        # Create a ContentFile from the PDF buffer

        if assessment_type == "Assignment":
            pdf_file_name = f"{education_level}_{subject}_{assessment_type}_{year}_{self.request.id}.pdf"
        else:
            pdf_file_name = f"{education_level}_{subject}_{exam_type}_{assessment_type}_{year}_{self.request.id}.pdf"
        pdf_file = ContentFile(buffer.getvalue(), pdf_file_name)

        # Get or create the default user
        current_time = timezone.now()

        formatted_time = current_time.strftime('%Y%m%d%H%M%S')
        
        unique_email = f"default{formatted_time}@gmail.com"

        default_user, created = CustomUser.objects.get_or_create(email=unique_email)
        if created:
            default_user.set_password(unique_email.split('@')[0])
            default_user.save()

        # Create the GeneratedExam object

        if assessment_type == "Assignment":
            generated_exam_title=f"{education_level}_{subject}_{assessment_type}_{term}_{year}",
        else:
            generated_exam_title=f"{education_level}_{subject}_{exam_type}_{assessment_type}_{term}_{year}",

        try:
            latest_prices = ExamGeneratorPrices.objects.latest('pk')

            if assessment_type == 'Exam':
                generated_exam_price = latest_prices.exam_price
            else:
                generated_exam_price = latest_prices.assignment_price

        except ExamGeneratorPrices.DoesNotExist:
            if assessment_type == 'Exam':
                generated_exam_price = 100
            else:
                generated_exam_price = 50

        generated_exam = GeneratedExam.objects.create(
            user=default_user,
            title=generated_exam_title,
            file=pdf_file,
            task_id=self.request.id,
            assessment_type=assessment_type,
            price=generated_exam_price
        )


        order = Order.objects.create(
            user=generated_exam.user,
            total_price=generated_exam.price,
            generated_exam=generated_exam,
        )

        result = display_order_number(order.id)
        order.display_order_number = result
        order.save()


        questions_with_answers = question_ids_in_order

        def generate_marking_scheme(questions_with_answers=questions_with_answers, exam_id=generated_exam.id):

            def to_roman(num):
                roman_numerals = {
                    1: "I", 2: "II", 3: "III", 4: "IV",
                    5: "V", 6: "VI", 7: "VII", 8: "VIII",
                    9: "IX", 10: "X", 11: "XI", 12: "XII",
                    13: "XIII", 14: "XIV", 15: "XV", 16: "XVI",
                    17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX"
                }
                return roman_numerals.get(num, str(num))

            def to_alphabet_lower(num):
                alphabet_numerals = {
                    1: "a", 2: "b", 3: "c", 4: "d",
                    5: "e", 6: "f", 7: "g", 8: "h",
                    9: "i", 10: "j", 11: "k", 12: "l",
                    13: "n", 14: "o", 15: "p", 16: "q",
                    17: "r", 18: "s", 19: "t", 20: "u"
                }
                return alphabet_numerals.get(num, str(num))
            
            question_ids = questions_with_answers
            generated_exam_id = exam_id

            case = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(question_ids)])
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            try:

                questions = Question.objects.filter(id__in=question_ids).annotate(order=case).order_by('order')

                generated_exam = get_object_or_404(GeneratedExam, id=generated_exam_id)

                def draw_page_number(page_num):
                    p.setFont("Times-Bold", 14)
                    page_num_text = f"{page_num}"
                    text_width = p.stringWidth(page_num_text, "Times-Bold", 14)
                    p.drawString((width - text_width) / 2, height - 0.5 * inch, page_num_text)

                def draw_text(text, y_position, indent=0):
                    nonlocal page_num
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

                    if not lines: 
                        lines.append("No answer")

                    for line in lines:
                        if y_position < 1 * inch:
                            p.showPage()
                            page_num += 1
                            draw_page_number(page_num)
                            p.setFont("Times-Roman", 12)
                            y_position = height - 1.5 * inch

                        p.drawString(1 * inch + indent, y_position, line)
                        y_position -= 0.3 * inch

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

                def draw_image(image_url, y_position):
                    nonlocal page_num
                    img, image_width, image_height = resize_image(image_url, int(0.7 * width), int(0.7 * height))

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

                    return y_position



                def draw_numbering(number, y_position, indent=0, bold=True):
                    p.setFont("Times-Bold" if bold else "Times-Roman", 12)
                    p.drawString(0.8 * inch + indent, y_position, number)
                    return y_position



                def draw_title(title, y_position):
                    nonlocal page_num
                    p.setFont("Times-Bold", 18)
                    max_width = width - 2 * inch 
                    line_height = 24 
                    lines = []

                    current_line = ""
                    for word in title.split():
                        if p.stringWidth(current_line + " " + word, "Times-Bold", 18) <= max_width:
                            current_line += " " + word if current_line else word
                        else:
                            lines.append(current_line.strip())
                            current_line = word

                    if current_line:
                        lines.append(current_line.strip())

                    title_height = len(lines) * line_height 

                    if y_position - title_height < 1 * inch:
                        p.showPage()
                        page_num += 1
                        draw_page_number(page_num)
                        p.setFont("Times-Roman", 16)
                        y_position = height - 1.5 * inch

                    for line in lines:
                        text_width = p.stringWidth(line, "Times-Bold", 18)
                        p.drawString((width - text_width) / 2, y_position, line)
                        y_position -= line_height  

                    return y_position - 0.5 * inch




                page_num = 1
                draw_page_number(page_num)
                p.setFont("Times-Roman", 16)
                y_position = height - 1.5 * inch


                exam_title = generated_exam.title  
                exam_title_clean = exam_title.replace('(', '').replace(')', '').replace('_', ' ').replace("'", "").replace(',', "")
                title = f"Marking Scheme for {exam_title_clean}"
                y_position = draw_title(title, y_position)

                for i, question in enumerate(questions, start=1):
                    y_position = draw_numbering(f"{i}.", y_position)

                    if hasattr(question, 'answer') and question.answer:
                        y_position = draw_text(question.answer.answer_text, y_position, indent=0.2 * inch)

                        if question.answer.image:
                            y_position = draw_image(question.answer.image.url, y_position)
                    else:
                        if question.sub_questions.exists():
                            pass
                        else:
                            y_position = draw_text("No answer", y_position, indent=0.5 * inch)

                    if question.sub_questions.exists():
                        for j, sub_question in enumerate(question.sub_questions.all(), start=1):
                            sub_number = to_roman(j)
                            y_position = draw_numbering(f"{sub_number}.", y_position, indent=0.5 * inch)

                            if hasattr(sub_question, 'sub_answer') and sub_question.sub_answer:
                                y_position = draw_text(sub_question.sub_answer.sub_answer_text, y_position, indent=1 * inch)

                                if sub_question.sub_answer.image:
                                    y_position = draw_image(sub_question.sub_answer.image.url, y_position)
                            else:
                                if sub_question.sub_sub_questions.exists():
                                    pass
                                else:
                                    y_position = draw_text("No answer", y_position, indent=0.5 * inch)

                            if sub_question.sub_sub_questions.exists():
                                for k, sub_sub_question in enumerate(sub_question.sub_sub_questions.all(), start=1):
                                    sub_sub_number = to_alphabet_lower(k)
                                    y_position = draw_numbering(f"{sub_sub_number}.", y_position, indent=1 * inch)

                                    if hasattr(sub_sub_question, 'sub_sub_answer') and sub_sub_question.sub_sub_answer:
                                        y_position = draw_text(sub_sub_question.sub_sub_answer.sub_sub_answer_text, y_position, indent=1.5 * inch)

                                        if sub_sub_question.sub_sub_answer.image:
                                            y_position = draw_image(sub_sub_question.sub_sub_answer.image.url, y_position)
                                    else:
                                        y_position = draw_text("No answer", y_position, indent=1.5 * inch)

                p.showPage()
                draw_end_text()

                p.save()

                buffer.seek(0)
                marking_scheme_pdf = buffer.getvalue()
                buffer.close()

                marking_scheme = MarkingScheme.objects.create(generated_exam=generated_exam)
                marking_scheme.file.save(f"marking_scheme_{generated_exam.id}.pdf", ContentFile(marking_scheme_pdf))

            except Exception as e:
                self.retry(exc=e, countdown=60)

            return f"Marking scheme generated for GeneratedExam ID {generated_exam_id}"




        generate_marking_scheme()

        return {'message': 'GeneratedExam object created successfully'}
    
    except Exception as e:
        return {'error': str(e)}