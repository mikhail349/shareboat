from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager 
from django.db.models.signals import pre_save, post_save, post_delete

from file import utils, signals
from PIL import Image

import uuid

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
        extra_fields.setdefault('email_confirmed', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
       

class User(AbstractUser):   
    username = None
    last_name = None

    first_name = models.CharField(_('first name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    email_confirmed = models.BooleanField("Эл. почта подтверждена", default=False)
    avatar = models.ImageField(upload_to=lambda instance, filename: utils.get_file_path(instance, filename, 'avatar/'), null=True, blank=True)
    avatar_sm = models.ImageField(upload_to=lambda instance, filename: utils.get_file_path(instance, filename, 'avatar/sm/'), null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    def get_telegram_id(self):
        if hasattr(self, 'telegramuser'):
            return self.telegramuser.chat_id
        return None

    def save(self, *args, **kwargs):  
        super(User, self).save(*args, **kwargs)
        
        try: 
            if self.avatar_sm:
                img = Image.open(self.avatar_sm.path)
                img = img.resize(utils.limit_size(img.width, img.height, 64, 64), Image.ANTIALIAS)
                img.save(self.avatar_sm.path, format="webp") 
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(str(e))


class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    verification_code = models.CharField("Код верификации", max_length=6)
    chat_id = models.IntegerField("Telegram ИД", null=True, blank=True)

    @classmethod
    def get_user(cls, update):
        try:
            chat_id = update.message.from_user.id
            return cls.objects.get(chat_id=chat_id).user
        except cls.DoesNotExist:
            return None

    class Meta:
        verbose_name = 'Учетная запись в Telegram'


pre_save.connect(signals.verify_imagefile, sender=User)
pre_save.connect(signals.delete_old_file, sender=User)
post_save.connect(signals.compress_imagefile, sender=User)
post_delete.connect(signals.delete_file, sender=User)

