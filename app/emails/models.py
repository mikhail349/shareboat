import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from boat.models import Boat
from booking.models import Booking
from config import tokens

from .exceptions import EmailLagError
from .utils import send_email

User: AbstractBaseUser = get_user_model()


class UserEmail(models.Model):
    """Модель отправки эл. почты пользователю."""
    class Type(models.IntegerChoices):
        """Типы отправок."""
        VERIFICATION = 0, _("Подтверждение почты")
        RESTORE_PASSWORD = 1, _("Восстановление пароля")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="emails")
    type = models.IntegerField(choices=Type.choices)
    last_email_dt = models.DateTimeField(auto_now=True)

    @classmethod
    def get_next_email_datetime(
        cls,
        user: User,  # type: ignore
        type: Type,  # type: ignore
    ) -> datetime.datetime:
        """Получить время, когда письмо можно отправить повторно.

        Args:
            user: пользователь
            type: тип отправки

        Returns:
            datetime: датавремя следующей отправки

        """
        try:
            user_email = cls.objects.get(user=user, type=type)
        except cls.DoesNotExist:
            user_email = None

        if not user_email:
            return timezone.now()

        next_dt = user_email.last_email_dt + \
            datetime.timedelta(minutes=settings.EMAIL_LAG_MINUTES)
        if next_dt < timezone.now():
            return timezone.now()

        return next_dt

    @classmethod
    def validate_next_email_dt(cls, user: User, type: Type):  # type: ignore
        """Проверить, наступило ли время,
        когда письмо можно отправить повторно.

        Args:
            user: пользователь
            type: тип отправки

        Raises:
            EmailLagError

        """
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
    def send_verification_email(
        cls,
        request: HttpRequest,
        user: User  # type: ignore
    ) -> datetime.datetime:
        """Отправить письмо для подтверждения почты и
        получить датувремя следующей отправки.

        Args:
            request: http-запрос
            user: пользователь-получатель

        Returns:
            datetime: датавремя следующей отправки
        """
        type = cls.Type.VERIFICATION
        cls.validate_next_email_dt(user, type)  # type: ignore

        token = tokens.generate_token(user, tokens.VERIFICATION)
        domain = ("https" if request.is_secure() else "http") + \
            "://" + get_current_site(request).domain
        html = render_to_string(
            "emails/verification_email.html",
            context={'token': token, 'domain': domain}
        )
        send_email("Подтверждение почты", html, [user.email])
        cls.objects.update_or_create(user=user, type=type)
        return cls.get_next_email_datetime(user, type)  # type: ignore

    @classmethod
    def send_restore_password_email(
        cls,
        request: HttpRequest,
        user: User  # type: ignore
    ) -> datetime.datetime:
        """Отправить письмо для восстановления пароля и
        получить датувремя следующей отправки.

        Args:
            request: http-запрос
            user: пользователь-получатель

        Returns:
            datetime: датавремя следующей отправки
        """
        type = cls.Type.RESTORE_PASSWORD
        cls.validate_next_email_dt(user, type)  # type: ignore
        token = tokens.generate_token(user, tokens.RESTORE_PASSWORD)
        domain = ("https" if request.is_secure() else "http") + \
            "://" + get_current_site(request).domain
        html = render_to_string(
            "emails/restore_password_email.html",
            context={'token': token, 'domain': domain}
        )
        send_email("Восстановление пароля", html, [user.email])
        cls.objects.update_or_create(user=user, type=type)
        return cls.get_next_email_datetime(user, type)  # type: ignore

    @classmethod
    def send_booking_status(cls, booking: Booking, user: User):  # type: ignore
        """Отправить письмо об изменении статуса бронирования.

        Args:
            booking: бронирование
            user: пользователь-получатель

        """
        if user.email_notification:
            status = booking.get_status_display()
            content = f'Статус бронирования изменился на "{status}"'
            send_email("Изменился статус бронирования", content, [user.email])

    @classmethod
    def send_initial_booking_to_owner(cls, booking: Booking):
        """Отправить начальное письмо арендодателю о бронировании.

        Args:
            booking: бронирование

        """
        user = booking.boat.owner
        if user.email_notification:
            content = 'Новый запрос на бронирование'
            send_email("Новый запрос на бронирование", content, [user.email])

    @classmethod
    def send_boat_published_to_owner(cls, boat: Boat, request: HttpRequest):
        """Отправить письмо арендодателю об успешной модерации.

        Args:
            boat: лодка
            request: http-запрос

        """
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
    def send_boat_declined_to_owner(
        cls,
        boat: Boat,
        comment: str,
        request: HttpRequest
    ):
        """Отправить письмо арендодателю о неуспешной модерации.

        Args:
            boat: лодка
            comment: комментарий отклонения
            request: http-запрос

        """
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
