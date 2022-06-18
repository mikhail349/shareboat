from enum import unique
from django.db import models

class PublishedCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True)

class Category(models.Model):
    name = models.CharField('Название', max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='categories', verbose_name='Родитель', null=True, blank=True)
    url = models.CharField('Ссылка', max_length=255, null=True, blank=True)
    description = models.TextField('Описание', null=True, blank=True)
    published = models.BooleanField('Опубликована', default=False) 
    full_path = models.CharField('Полный путь', max_length=255, null=True, blank=True, db_index=True)

    objects = models.Manager()
    m_published = PublishedCategoryManager()

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

    def save(self, *args, **kwargs):
        self.full_path = (self.parent.full_path + (self.url or '') if self.parent else '/' + (self.url or '')) + '/'
        
        for item in self.categories.all():
            item.save()

        return super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = [['url', 'parent']]
        ordering = ['full_path']