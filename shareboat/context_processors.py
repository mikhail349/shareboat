from boat.models import Boat
from booking.models import Booking

def nav_counters(request):
    boats_on_moderation_count = Boat.objects.filter(status=Boat.Status.ON_MODERATION).count()
    bookings_on_pending_count = 0
    if request.user.is_authenticated:
        bookings_on_pending_count = Booking.objects.filter(boat__owner=request.user, status=Booking.Status.PENDING).count()
    return {
        'nav_counters': {
            'boats_on_moderation_count': boats_on_moderation_count,
            'bookings_on_pending_count': bookings_on_pending_count,
            'total': boats_on_moderation_count + bookings_on_pending_count
        }
    } 
    