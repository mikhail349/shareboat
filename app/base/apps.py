from django.apps import AppConfig


class BaseConfig(AppConfig):
    """Настройки приложения Базы."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
