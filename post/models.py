from django.db import models

from asset.models import Asset

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Заготовка"
        APPROVING = "approving", "На проверке"
        PUBLISHED = "published", "Опубликовано"


    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="posts")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices,default=Status.DRAFT)
    text = models.TextField()
    publication_datetime = models.DateTimeField(null=True, blank=True)
