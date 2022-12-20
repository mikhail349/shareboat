import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone

from .utils import send_email
from .exceptions import EmailLagError
from config import tokens


class UserEmail(models.Model):

    EMAIL_LAG_MINUTES = 1

    class Type(models.IntegerChoices):
        VERIFICATION = 0, _("Подтверждение почты")
        RESTORE_PASSWORD = 1, _("Восстановление пароля")

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="emails")
    type = models.IntegerField(choices=Type.choices)
    last_email_dt = models.DateTimeField(auto_now=True)

    @classmethod
    def get_next_email_datetime(cls, user, type):
        try:
            user_email = cls.objects.get(user=user, type=type)
        except cls.DoesNotExist:
            user_email = None

        if not user_email:
            return timezone.now()

        next_dt = user_email.last_email_dt + \
            datetime.timedelta(minutes=cls.EMAIL_LAG_MINUTES)
        if next_dt < timezone.now():
            return timezone.now()

        return next_dt

    @classmethod
    def validate_next_email_dt(cls, user, type):
        next_dt = cls.get_next_email_datetime(user, type)
        now = timezone.now()
        if now < next_dt:
            total_seconds = (next_dt - now).total_seconds()
            minutes = total_seconds // 60
            seconds = total_seconds - (minutes * 60)

            raise EmailLagError(
                "Следующая отправка будет доступна через %i мин. %i сек." %
                (minutes, seconds)
            )

    @classmethod
    def send_verification_email(cls, request, user):
        type = cls.Type.VERIFICATION
        cls.validate_next_email_dt(user, type)

        token = tokens.generate_token(user, tokens.VERIFICATION)
        domain = ("https" if request.is_secure() else "http") + \
            "://" + get_current_site(request).domain
        html = render_to_string(
            "emails/verification_email.html",
            context={'token': token, 'domain': domain}
        )
        send_email("Подтверждение почты", html, [user.email])
        cls.objects.update_or_create(user=user, type=type)
        return cls.get_next_email_datetime(user, type)

    @classmethod
    def send_restore_password_email(cls, request, user):
        type = cls.Type.RESTORE_PASSWORD
        cls.validate_next_email_dt(user, type)
        token = tokens.generate_token(user, tokens.RESTORE_PASSWORD)
        domain = ("https" if request.is_secure() else "http") + \
            "://" + get_current_site(request).domain
        html = render_to_string(
            "emails/restore_password_email.html",
            context={'token': token, 'domain': domain}
        )
        send_email("Восстановление пароля", html, [user.email])
        cls.objects.update_or_create(user=user, type=type)
        return cls.get_next_email_datetime(user, type)

    @classmethod
    def send_booking_status(cls, booking, user):
        if user.email_notification:
            status = booking.get_status_display()
            content = f'Статус бронирования изменился на "{status}"'
            send_email("Изменился статус бронирования", content, [user.email])

    @classmethod
    def send_initial_booking_to_owner(cls, booking):
        user = booking.boat.owner
        if user.email_notification:
            content = 'Новый запрос на бронирование'
            send_email("Новый запрос на бронирование", content, [user.email])

    @classmethod
    def send_boat_published_to_owner(cls, boat, request):
        user = boat.owner
        if user.email_notification:
            domain = ("https" if request.is_secure() else "http") + \
                "://" + get_current_site(request).domain
            boat_url = domain + reverse('boat:view', kwargs={'pk': boat.pk})
            profile_url = domain + reverse('user:update')
            content = f"""
                <h2>Лодка опубликована!</h2>
                <p>
                    <b>{boat.get_full_name()}</b> теперь доступна
                    для аренды всем желающим!
                </p>
                <a href="{boat_url}" class="btn btn-primary">
                    Перейти к лодке
                </a>
                <p>
                    <a href="{profile_url}" class="text-muted">
                        Настроить уведомления
                    </a>
                </p>
            """
            send_email("Лодка опубликована", content, [user.email])

    @classmethod
    def send_boat_declined_to_owner(cls, boat, comment, request):
        user = boat.owner
        if user.email_notification:
            domain = ("https" if request.is_secure() else "http") + \
                "://" + get_current_site(request).domain
            boat_url = domain + reverse('boat:view', kwargs={'pk': boat.pk})
            profile_url = domain + reverse('user:update')
            content = f"""
                <h2>Лодка не прошла модерацию</h2>
                <p>
                    <b>{boat.get_full_name()}</b> не соответствует
                    правилам сервиса: {comment}
                </p>
                <a href="{boat_url}" class="btn btn-primary">
                    Перейти к лодке
                </a>
                <p>
                    <a href="{profile_url}" class="text-muted">
                        Настроить уведомления
                    </a>
                </p>
            """
            send_email("Лодка не прошла модерацию", content, [user.email])

    class Meta:
        unique_together = [['user', 'type']]
