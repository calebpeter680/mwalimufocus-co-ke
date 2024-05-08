from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser
from decimal import Decimal
import json

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:  
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


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
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    education_level = models.ForeignKey(Education_Level, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    file = models.FileField(null=True, blank=True, upload_to='shopitemfiles/')
    slug = models.SlugField(blank=True)
    education_level_slug = models.SlugField(blank=True)
    subject_slug = models.SlugField(blank=True)
    category_slug = models.SlugField(blank=True)
    downloads_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)

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







class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    items = models.ManyToManyField(ShopItem, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    is_paid = models.BooleanField(default=False)
    display_order_number = models.IntegerField(null=True, blank=True)
    attachments_sent = models.BooleanField(default=False)
    customer_items_created = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"Order {self.pk} - Total: Ksh {self.total_price}"





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



