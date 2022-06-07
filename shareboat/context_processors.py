from boat.models import Boat
from booking.models import Booking

def nav_counters(request):
    
    boats_on_moderation_count = Boat.objects.filter(status=Boat.Status.ON_MODERATION).count()
    bookings_on_pending_count = 0
    new_messages_count = 0 
    
    if request.user.is_authenticated:
        bookings_on_pending_count = Booking.objects.filter(boat__owner=request.user, status=Booking.Status.PENDING).count()
        from chat.models import Message
        new_messages_count = Message.objects.filter(recipient=request.user, read=False).count()
    
    return {
        'nav_counters': {
            'boats_on_moderation_count': boats_on_moderation_count,
            'bookings_on_pending_count': bookings_on_pending_count,
            'new_messages_count': new_messages_count,
            'total': boats_on_moderation_count + bookings_on_pending_count + new_messages_count
        }
    } 
    
def notifications(request):
    boats = Boat.objects.none() 
    #if request.user.is_authenticated:
    #    boats = Boat.objects.all()
    return {
        'notifications': {
            'chat': {
                'boats': boats
            }
        }
    }