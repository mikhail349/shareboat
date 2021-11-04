from django.db import models
#from user.models import User
from django.contrib.auth import get_user_model
from django.db.models.fields import TimeField
from django.utils.translation import gettext_lazy as _

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .exceptions import EmailLagError
from shareboat.tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from .utils import send_email
import datetime
from django.utils import timezone

def check_datetime(datetime):
    now = timezone.now()
    if timezone.now() < datetime:
        total_seconds = (datetime - now).total_seconds()
        minutes = total_seconds // 60
        seconds = total_seconds - (minutes * 60)
        raise EmailLagError("Следующая отправка будет доступна через %i мин. %i сек." % (minutes, seconds))

class UserEmail(models.Model):

    VERIFICATION_LAG_MINUTES = 1
    RESTORE_PASSWORD_LAG_MINUTES = 1

    class Type(models.IntegerChoices):
        VERIFICATION        = 0, _("Подтверждение почты")
        RESTORE_PASSWORD    = 1, _("Восстановление пароля")

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="emails")
    type = models.IntegerField(choices=Type.choices)
    last_email_dt = models.DateTimeField(auto_now=True)

    @classmethod
    def get_next_email_datetime(cls, user, type, lag):        
        try:
            user_email = cls.objects.get(user=user, type=type)
        except cls.DoesNotExist:
            user_email = None

        if not user_email:
            return timezone.now()
        
        next_dt = user_email.last_email_dt + datetime.timedelta(minutes=lag)
        if next_dt < timezone.now():
            return timezone.now()

        return next_dt

    @classmethod
    def get_next_verification_email_datetime(cls, user):
        return cls.get_next_email_datetime(user, cls.Type.VERIFICATION, cls.VERIFICATION_LAG_MINUTES)

    @classmethod
    def get_next_restore_password_email_datetime(cls, user):
        return cls.get_next_email_datetime(user, cls.Type.RESTORE_PASSWORD, cls.RESTORE_PASSWORD_LAG_MINUTES)

    @classmethod
    def send_verification_email(cls, request, user):        
        next_dt = cls.get_next_verification_email_datetime(user) 
        check_datetime(next_dt)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        domain = ("https" if request.is_secure() else "http") + "://" + get_current_site(request).domain
        html = render_to_string("emails/verification_email.html", context={'uid': uid, 'token': token, 'domain': domain})
        send_email("Подтверждение почты", html, [user.email])
        user_email, _ = cls.objects.update_or_create(user=user, type=UserEmail.Type.VERIFICATION)
        return user_email.last_email_dt + datetime.timedelta(minutes=cls.VERIFICATION_LAG_MINUTES)

    @classmethod
    def send_restore_password_email(cls, request, user):        
        next_dt = cls.get_next_restore_password_email_datetime(user) 
        check_datetime(next_dt)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        domain = ("https" if request.is_secure() else "http") + "://" + get_current_site(request).domain
        html = render_to_string("emails/restore_password_email.html", context={'uid': uid, 'token': token, 'domain': domain})
        send_email("Восстановление пароля", html, [user.email])
        user_email, _ = cls.objects.update_or_create(user=user, type=UserEmail.Type.RESTORE_PASSWORD)
        return user_email.last_email_dt + datetime.timedelta(minutes=cls.RESTORE_PASSWORD_LAG_MINUTES)

    class Meta:
        unique_together = [['user', 'type']] 
