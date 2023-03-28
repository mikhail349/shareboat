from booking.models import Booking


def send_status_to_renter(booking: Booking):
    """Отправить арендатору уведомление с текущим статусом.

    Args:
        booking: бронирование

    """
    from chat.models import MessageBooking
    MessageBooking.objects.send_status_to_renter(booking)


def send_initial_to_owner(booking: Booking):
    """Отправить арендодателю начальное уведомление.

    Args:
        booking: бронирование

    """
    from chat.models import MessageBooking
    MessageBooking.objects.send_initial_to_owner(booking)


def autoupdate_statuses():
    """Обновить статусы бронирований."""
    from django.utils import timezone

    from booking.models import Booking

    Booking.objects \
           .filter(status=Booking.Status.PREPAYMENT_REQUIRED,
                   prepayment__until__lte=timezone.now()) \
           .update(status=Booking.Status.DECLINED)
    Booking.objects \
           .filter(status=Booking.Status.ACCEPTED,
                   start_date__lte=timezone.now()) \
           .update(status=Booking.Status.ACTIVE)
    Booking.objects \
           .filter(status=Booking.Status.ACTIVE,
                   end_date__lte=timezone.now()) \
           .update(status=Booking.Status.DONE)


def autoremind_prepayment():
    """Напомнить об предоплате."""
    from datetime import timedelta

    from django.utils import timezone

    from booking.models import Booking
    from notification.utils import (remind_prepayment_to_owner,
                                    remind_prepayment_to_renter)

    deadline = timezone.now() + timedelta(days=3)
    for booking in Booking.objects \
            .filter(status=Booking.Status.PREPAYMENT_REQUIRED,
                    prepayment__until__lte=deadline):
        remind_prepayment_to_renter(booking)
        remind_prepayment_to_owner(booking)