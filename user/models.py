from django.db import models, transaction
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager 
from django.dispatch.dispatcher import receiver
from PIL import Image

from file import utils, exceptions

MAX_AVATAR_SIZE = 5 * 1024 * 1024

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username and last_name fields."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    
    username = None
    last_name = None

    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to=utils.get_file_path, null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

@receiver(models.signals.pre_save, sender=User)
def pre_save_user(sender, instance, *args, **kwargs):
    
    if instance.avatar:
        if instance.avatar.size > MAX_AVATAR_SIZE:
            raise exceptions.FileSizeException()

        img = Image.open(instance.avatar)
        img.verify()

    if instance.pk:
        cur_avatar = User.objects.get(pk=instance.pk).avatar
        if cur_avatar != instance.avatar:
            if cur_avatar:
                transaction.on_commit(lambda: utils.remove_file(cur_avatar.path))


@receiver(models.signals.post_save, sender=User)
def compress_avatar(sender, instance, created, *args, **kwargs):
    if instance.avatar:
        img = Image.open(instance.avatar.path)
        img = img.resize(utils.limit_size(img.width, img.height), Image.ANTIALIAS)
        img.save(instance.avatar.path, quality=70, optimize=True)        


@receiver(models.signals.post_delete, sender=User)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.avatar:
        transaction.on_commit(lambda: utils.remove_file(instance.avatar.path))