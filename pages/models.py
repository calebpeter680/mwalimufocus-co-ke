from django.db import models
from tinymce.models import HTMLField

class TopLevelPage(models.Model):
    heading = models.CharField(max_length=200)
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField()
    body = HTMLField()

    def __str__(self):
        return self.heading
