from django.apps import AppConfig


class BookingConfig(AppConfig):
    """Приложение бронирований."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'
