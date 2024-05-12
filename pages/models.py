from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField


class TopLevelPage(models.Model):
    heading = models.CharField(max_length=200)
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField()
    body = HTMLField()
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.heading)
        super().save(*args, **kwargs)
