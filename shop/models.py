from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser
from decimal import Decimal
import json
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField
from django.core.exceptions import ValidationError




class PromotionalEmails(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_delivered_to_all = models.BooleanField(default=False)

    def __str__(self):
        return self.subject




class PaymentOption(models.Model):
    PAYMENT_CHOICES = [
        ('MPESA', 'M-Pesa Express'),
        ('INTASEND', 'IntaSend'),
    ]

    name = models.CharField(max_length=20, choices=PAYMENT_CHOICES, unique=True)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return self.get_name_display()

    def save(self, *args, **kwargs):
        if self.is_selected:
            PaymentOption.objects.filter(is_selected=True).exclude(id=self.id).update(is_selected=False)
        
        super().save(*args, **kwargs)

    @classmethod
    def ensure_at_least_one_selected(cls):
        if not cls.objects.filter(is_selected=True).exists():
            raise ValidationError("At least one payment option must be selected.")






class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_shop_items', kwargs={'category_slug': self.slug})



class Education_Level(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:  
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:  
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class ShopItem(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    education_level = models.ForeignKey(Education_Level, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = HTMLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    file = models.FileField(null=True, blank=True, upload_to='shopitemfiles/')
    slug = models.SlugField(blank=True, max_length=300)
    education_level_slug = models.SlugField(blank=True)
    subject_slug = models.SlugField(blank=True)
    category_slug = models.SlugField(blank=True)
    downloads_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    is_search_engine_indexible = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    Aggregate_Rating_Value = models.IntegerField(default=0)
    Worst_Rating_Value = models.IntegerField(default=0)
    Best_Rating_Value = models.IntegerField(default=0)
    Rating_Count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='shopitemimages/', null=True, blank=True)
    is_discounted = models.BooleanField(default=False)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_start_time = models.DateTimeField(null=True, blank=True)
    discount_end_time = models.DateTimeField(null=True, blank=True)

    YEAR_CHOICES = [(r, str(r)) for r in range(1980, timezone.now().year + 1)]
    year = models.IntegerField(choices=YEAR_CHOICES, default=timezone.now().year, null=True, blank=True)

    TERM_CHOICES = [
        ('Term 1', 'Term 1'),
        ('Term 2', 'Term 2'),
        ('Term 3', 'Term 3'),
    ]
    term = models.CharField(max_length=10, choices=TERM_CHOICES, null=True, blank=True)

    TERM_LEVEL_CHOICES = [
        ('Opener', 'Opener'),
        ('Mid', 'Mid'),
        ('End', 'End'),
    ]
    term_level = models.CharField(max_length=6, choices=TERM_LEVEL_CHOICES, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}")
        if not self.education_level_slug:
        	self.education_level_slug = slugify(f"{self.education_level.name}")
        if not self.subject_slug:
        	self.subject_slug = slugify(f"{self.subject.name}")
       	if not self.category_slug:
       		self.category_slug = slugify(f"{self.category.name}")

        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.title} (ID: {self.pk})'


    def get_absolute_url(self):
        return reverse('shop_item_detail', kwargs={
            'category_slug': self.category.slug,
            'pk': self.pk,
            'slug': self.slug
        })



class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    items = models.ManyToManyField(ShopItem, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    is_paid = models.BooleanField(default=False)
    display_order_number = models.IntegerField(null=True, blank=True)
    attachments_sent = models.BooleanField(default=False)
    customer_items_created = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    cart_reminder_sent = models.BooleanField(default=False)
    generated_exam = models.OneToOneField('examgenerator.GeneratedExam', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"Order {self.display_order_number} - Total: Ksh {self.total_price}"

    class Meta:
        indexes = [
            models.Index(fields=['is_paid', 'cart_reminder_sent']),
            models.Index(fields=['user']),
        ]





class Customer_Item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=250)
    category = models.CharField(max_length=200)
    education_level = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    file = models.FileField(upload_to='customer_items/')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'{self.title} (ID: {self.pk})'





class Brand(models.Model):
    logo = models.ImageField(blank=True, upload_to='brand_logos/')
    favicon = models.ImageField(blank=True, upload_to='brand_favicons/')
    phone_number = models.CharField(max_length=20, blank=True)  
    email = models.EmailField(blank=True)  
    primary_color = models.CharField(max_length=7, default='#000000') 

    def __str__(self):
        return f"Brand: {self.id}"




class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id




class Discount(models.Model):
    amount = models.IntegerField()

    def __str__(self):
        return f"Discount of {self.amount}%"



class PaymentReminderLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reminder_sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reminder sent for Order {self.order.id} to {self.user.email} at {self.reminder_sent_at}"
