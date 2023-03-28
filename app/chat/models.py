from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.urls import reverse
from django.utils import timezone

from boat.models import Boat
from booking.models import Booking

User: AbstractBaseUser = get_user_model()


class Message(models.Model):
    """Модель сообщения."""
    text = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.PROTECT,
                               related_name="messages_as_sender",
                               null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(User, on_delete=models.PROTECT,
                                  related_name="messages_as_recipient",
                                  null=True, blank=True)
    read = models.BooleanField(default=False)

    def get_title(self) -> str:
        """Получить заголовок.

        Используется в HTML.

        Returns:
            str

        """
        return ''

    def get_href(self) -> str:
        """Получить ссылку на сообщение.

        Returns:
            str

        """
        return reverse('chat:message')

    def __str__(self):
        sender = self.sender or '[Системное сообщение]'
        return f'{sender}: {self.text}'


class SupportManager(models.Manager):
    """Менеджер сообщений поддержки."""
    def send_greetings(self, recipient: User):  # type: ignore
        """Отправить приветствие.

        Args:
            recipient: пользователь

        """
        text = '<div>Вас приветствует SHAREBOAT.RU!</div>' \
               '<div>Здесь вы можете задать интересующий Вас вопрос.</div>'
        return self.create(recipient=recipient, text=text)


class MessageSupport(Message):
    """Модель сообщения поддержки."""

    objects = SupportManager()

    def get_title(self):
        return 'Поддержка'

    def get_href(self):
        return reverse('chat:message')


class BookingManager(models.Manager):
    """Менеджер сообщений по бронированию."""
    def send_initial_to_owner(self, booking: Booking) -> 'MessageBooking':
        """Отправить начальное сообщение арендодателю.

        Args:
            booking: бронирование

        Returns:
            MessageBooking

        """
        text = "<div>Новый запрос на бронирование</div>"
        return self.create(booking=booking, recipient=booking.boat.owner,
                           text=text)

    def send_status(
        self,
        booking: Booking,
        recipient: User  # type: ignore
    ) -> 'MessageBooking':
        """Отправить сообщение со статусом.

        Args:
            booking: бронирование
            recipient: получатель

        Returns:
            MessageBooking

        """
        status = booking.get_status_display()
        text = f'<div>Статус бронирования изменился на "{status}"</div>'
        return self.create(booking=booking, recipient=recipient, text=text)

    def remind_prepayment_to_renter(
        self,
        booking: Booking
    ) -> 'MessageBooking':
        """Отправить сообщение с напоминанием предоплаты арендатору.

        Args:
            booking: бронирование

        Returns:
            MessageBooking

        """
        date = timezone.localdate(booking.prepayment.until) \
                       .strftime('%d.%m.%Y')
        text = f'<div>Не забудьте внести предоплату до {date}, ' \
               f'иначе бронирование будет <b>отменено</b>.</div>'
        return self.create(booking=booking, recipient=booking.renter,
                           text=text)

    def remind_prepayment_to_owner(self, booking: Booking):
        """Отправить сообщение с напоминанием после
        получения предоплаты арендодателю.

        Args:
            booking: бронирование

        Returns:
            MessageBooking

        """
        date = timezone.localdate(booking.prepayment.until) \
                       .strftime('%d.%m.%Y')
        text = f'<div>Не забудьте сменить статус на "Оплата получена" ' \
               f'до {date}, если Вы получили предоплату. ' \
               f'Иначе бронирование будет <b>отменено</b>.</div>'
        return self.create(booking=booking, recipient=booking.boat.owner,
                           text=text)


class MessageBooking(Message):
    """Модель сообщения по бронированию."""
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="messages")
    objects = BookingManager()

    def get_title(self):
        return self.booking.boat.name

    def get_href(self):
        return reverse('chat:booking', kwargs={'pk': self.booking.pk})


class BoatManager(models.Manager):
    """Менеджер сообщений по лодкам"""
    def send_published_to_owner(self, boat: Boat) -> 'MessageBoat':
        """Отправить сообщение арендодателю, что лодка опубликована.

        Args:
            boat: лодка

        Returns:
            MessageBoat

        """
        text = "<div>Лодка опубликована!</div>"
        return self.create(boat=boat, recipient=boat.owner, text=text)

    def send_declined_to_owner(
        self,
        boat: Boat,
        comment: str
    ) -> 'MessageBoat':
        """Отправить сообщение арендодателю, что лодка отклонена.

        Args:
            boat: лодка
            comment: комментарий отклонения

        Returns:
            MessageBoat

        """
        text = f'<div>Лодка не прошла модерацию.</div>' \
               f'<div>Объявление не соответствует ' \
               f'правилам сервиса: {comment}</div>'
        return self.create(boat=boat, recipient=boat.owner, text=text)


class MessageBoat(Message):
    """Модель сообщения лодки."""
    class RejectionReason(models.IntegerChoices):
        OTHER = 0, "Прочее"

    boat = models.ForeignKey(
        Boat, on_delete=models.PROTECT, related_name="messages")
    objects = BoatManager()

    def get_title(self):
        return self.boat.name

    def get_href(self):
        return reverse('chat:boat', kwargs={'pk': self.boat.pk})

    @classmethod
    def get_rejection_reasons(cls) -> list:
        """Получить отсортированный список причин отклонения.

        Return:
            list

        """
        types = cls.RejectionReason.choices
        return sorted(types, key=lambda tup: tup[1])
