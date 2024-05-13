from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from tinymce.models import HTMLField
from django.utils import timezone

class TopLevelPage(models.Model):
    heading = models.CharField(max_length=200)
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField()
    body = HTMLField()
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.heading)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('top_level_page', kwargs={'slug': self.slug})





class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team_images/')
    description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True) 
    is_founder = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) 
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('team_member_detail', args=[self.id, self.slug])

