from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    is_new = models.BooleanField(default=False)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    agree_to_terms = models.BooleanField(default=True)

    is_vendor = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email




class BaseFAQ(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='faq_images/', blank=True, null=True)
    description = models.TextField()

    class Meta:
        abstract = True

class CustomerFAQ(BaseFAQ):
    pass

class VendorFAQ(BaseFAQ):
    pass




class Subscriber(models.Model):
    email = models.EmailField(unique=True) 
    joined_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.email
