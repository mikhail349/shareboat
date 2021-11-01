from django.db import models
from boat.models import Boat
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime

class Post(models.Model):
    class Status(models.IntegerChoices):
        DRAFT       = 0, _("Заготовка")
        APPROVING   = 1, _("На проверке")
        PUBLISHED   = 2, _("Опубликовано")

    boat = models.ForeignKey(Boat, on_delete=models.PROTECT, related_name="posts")
    status = models.IntegerField(choices=Status.choices, default=Status.DRAFT)
    text = models.TextField()
    pub_datetime = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.text

@receiver(pre_save, sender=Post)
def set_pub_datetime(sender, instance, *args, **kwargs):
    now = datetime.now()
    published = Post.Status.PUBLISHED

    if instance.status == published:
        if not instance.pk or Post.objects.filter(pk=instance.pk).exclude(status=published).exists():
            instance.pub_datetime = now
    else:
        instance.pub_datetime = None

class PostPrice(models.Model):
    class Type(models.IntegerChoices):
        DAYLY               = 0, _("Посуточно")
        DAYLY_PER_PERSON    = 1, _("Человеко-сутки")

    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name="prices")
    type = models.IntegerField(choices=Type.choices, default=Type.DAYLY)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)