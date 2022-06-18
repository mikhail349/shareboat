from django.db import models
from django.forms import ValidationError


class CategoryQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published=True)

class Category(models.Model):
    name = models.CharField('Название', max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='categories', verbose_name='Родитель', null=True, blank=True)
    url = models.CharField('Ссылка', max_length=255, null=True, blank=True)
    description = models.TextField('Описание', null=True, blank=True)
    published = models.BooleanField('Опубликована', default=False) 
    full_path = models.CharField('Полный путь', max_length=255, null=True, blank=True, db_index=True)

    objects = models.Manager.from_queryset(CategoryQuerySet)()

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
                raise ValidationError({
                    'parent': ['В качестве родителя нельзя выбирать эту же категорию',]
                })
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        self.full_path = (self.parent.full_path + (self.url or '') if self.parent else '/' + (self.url or '')) + '/'
        
        for item in self.categories.all():
            item.save()

        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = [['url', 'parent']]
        ordering = ['full_path']