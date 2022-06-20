def send_status_to_renter(booking):
    from chat.models import MessageBooking
    MessageBooking.objects.send_status_to_renter(booking)

def send_initial_to_owner(booking):
    from chat.models import MessageBooking
    MessageBooking.objects.send_initial_to_owner(booking)