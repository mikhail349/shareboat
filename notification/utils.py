from chat.models import MessageBoat, MessageBooking, MessageSupport


def send_greetings_to_user(user):
    MessageSupport.objects.send_greetings(user)

def send_initial_booking_to_owner(booking):
    MessageBooking.objects.send_initial_to_owner(booking)

def send_booking_status(booking, recipient):
    MessageBooking.objects.send_status(booking, recipient)

def send_boat_published_to_owner(boat):
    MessageBoat.objects.send_published_to_owner(boat)

def send_boat_declined_to_owner(boat, comment):
    MessageBoat.objects.send_declined_to_owner(boat, comment)