from django.db import models
from django.forms import ValidationError
from django.db.models.signals import post_save

from file import signals
from user.models import User


class BaseQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published=True)


class Category(models.Model):
    name = models.CharField('Название', max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               related_name='categories',
                               verbose_name='Родитель', null=True, blank=True)
    url = models.CharField('Ссылка', max_length=255, null=True, blank=True)
    description = models.TextField('Описание', null=True, blank=True)
    published = models.BooleanField('Опубликована', default=False)
    full_path = models.CharField(
        'Полный путь', max_length=255, null=True, blank=True, db_index=True)

    objects = models.Manager.from_queryset(BaseQuerySet)()

    def get_list_parent(self):
        def set_parent(item):
            res.append(item)
            if item.parent:
                set_parent(item.parent)
        res = []
        set_parent(self)
        return res

    def __str__(self):
        return self.name

    def clean(self, *args, **kwargs):
        if self.pk and self.parent:
            if self.pk == self.parent.pk:
                msg = 'В качестве родителя нельзя выбирать эту же категорию'
                raise ValidationError({
                    'parent': [msg, ]
                })
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        self.full_path = (self.parent.full_path + (self.url or '')
                          if self.parent else '/' + (self.url or '')) + '/'

        for item in self.categories.all():
            item.save()

        for article in self.articles.all():
            article.save()

        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = [['url', 'parent']]
        ordering = ['full_path']


class Article(models.Model):
    def get_file_path(instance, filename):
        import uuid
        ext = filename.split('.')[-1]
        return "portal/%s.%s" % (uuid.uuid4(), ext)

    name = models.CharField('Название', max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name='articles', verbose_name='Категория')
    url = models.CharField('Ссылка', max_length=255, null=True, blank=True)
    published = models.BooleanField('Опубликована', default=False)
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='articles',
        verbose_name='Создатель')
    created_at = models.DateTimeField(
        'Дата и время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата и время изменения', auto_now=True)
    full_path = models.CharField(
        'Полный путь', max_length=255, null=True, blank=True, db_index=True)
    preview_text = models.TextField('Превью', null=True, blank=True)
    preview_img = models.ImageField(
        'Картинка', upload_to=get_file_path, null=True, blank=True)
    content = models.TextField('Содержимое')

    objects = models.Manager.from_queryset(BaseQuerySet)()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_path = self.category.full_path + self.url + '/'
        super(Article, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        unique_together = [['url', 'category']]


post_save.connect(signals.compress_imagefile, sender=Article)
