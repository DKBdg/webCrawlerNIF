from django.db import models

# Create your models here.

class CrawledText(models.Model):
    url = models.TextField(null=False)
    original_title = models.TextField(default='')
    original_text = models.TextField(default='')
