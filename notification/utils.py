from chat.models import MessageBoat, MessageBooking, MessageSupport
from emails.models import UserEmail


def send_greetings_to_user(user):
    MessageSupport.objects.send_greetings(user)


def send_initial_booking_to_owner(booking):
    MessageBooking.objects.send_initial_to_owner(booking)
    UserEmail.send_initial_booking_to_owner(booking)


def send_booking_status(booking, recipient):
    MessageBooking.objects.send_status(booking, recipient)
    UserEmail.send_booking_status(booking, recipient)


def send_boat_published_to_owner(boat, request=None):
    MessageBoat.objects.send_published_to_owner(boat)
    UserEmail.send_boat_published_to_owner(boat, request)


def send_boat_declined_to_owner(boat, comment, request):
    MessageBoat.objects.send_declined_to_owner(boat, comment)
    UserEmail.send_boat_declined_to_owner(boat, comment, request)


def remind_prepayment_to_renter(booking):
    MessageBooking.objects.remind_prepayment_to_renter(booking)


def remind_prepayment_to_owner(booking):
    MessageBooking.objects.remind_prepayment_to_owner(booking)
