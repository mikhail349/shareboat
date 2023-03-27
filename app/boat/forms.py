from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Tariff, Term


class TariffForm(ModelForm):
    """Форма тарифа."""

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TariffForm, self).__init__(*args, **kwargs)

    def clean_boat(self):
        """Валидировать лодку.

        Returns:
            Boat: лодка

        Raises:
            ValidationError: лодка не найдена

        """
        boat = self.cleaned_data.get('boat')
        if boat and (boat.owner != self.request.user or not boat.is_active):
            raise ValidationError('Не найдена')
        return boat

    class Meta:
        model = Tariff
        exclude = ('weight',)


class TermForm(ModelForm):
    """Форма шаблона условий."""
    class Meta:
        model = Term
        exclude = ('user',)
