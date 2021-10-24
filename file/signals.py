from django.db import models, transaction
from PIL import Image

from . import utils, exceptions

def verify_imagefile(sender, instance, *args, **kwargs):
    MAX_FILE_SIZE = 7 * 1024 * 1024
    for field in sender._meta.fields:
        if isinstance(field, models.ImageField):
            image_file = getattr(instance, field.name)
            if image_file:
                if image_file.size > MAX_FILE_SIZE:
                    raise exceptions.FileSizeException()

                img = Image.open(image_file)
                img.verify()


def mark_changing_file_to_delete(sender, instance, *args, **kwargs):
    if instance.pk:    
        files_to_delete = []
        cur_instance = sender.objects.get(pk=instance.pk)
        for field in sender._meta.fields:
            if isinstance(field, models.FileField):
                cur_file = getattr(cur_instance, field.name) 
                if cur_file:
                    if cur_file != getattr(instance, field.name):  
                        files_to_delete.append(cur_file.path) 
        if files_to_delete:
            setattr(instance, '__files_to_delete', files_to_delete)                                
        
def delete_marked_file(sender, instance, created, *args, **kwargs):
    def f():
        for path in instance.__files_to_delete:
            utils.remove_file(path)
    if hasattr(instance, '__files_to_delete'):
        transaction.on_commit(f)

def compress_imagefile(sender, instance, created, *args, **kwargs):
    try: 
        for field in sender._meta.fields:
            if isinstance(field, models.ImageField):
                image_file = getattr(instance, field.name)
                if image_file:
                    img = Image.open(image_file.path)
                    img = img.resize(utils.limit_size(img.width, img.height), Image.ANTIALIAS)
                    img.save(image_file.path, quality=70, optimize=True) 
    except:
        pass


def delete_file(sender, instance, *args, **kwargs):
    def f():
        for field in sender._meta.fields:
            if isinstance(field, models.FileField):
                image_file = getattr(instance, field.name)
                if image_file:
                    utils.remove_file(image_file.path)
    transaction.on_commit(f)
                

    
