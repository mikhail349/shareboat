from booking.models import Booking


def nav_counters(request):
    bookings_on_pending_count = 0
    new_messages_count = 0

    if request.user.is_authenticated:
        bookings_on_pending_count = Booking.objects.filter(
            boat__owner=request.user, status=Booking.Status.PENDING).count()
        from chat.models import Message
        new_messages_count = Message.objects.filter(
            recipient=request.user, read=False).count()

    return {
        'nav_counters': {
            'bookings_on_pending_count': bookings_on_pending_count,
            'new_messages_count': new_messages_count,
        }
    }
