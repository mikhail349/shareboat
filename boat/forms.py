from django.forms import ModelForm
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from .models import Tariff

class TariffForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TariffForm, self).__init__(*args, **kwargs)

    def clean_boat(self):
        boat = self.cleaned_data.get('boat')
        if boat and boat.owner != self.request.user:
            raise ValidationError('Лодка не найдена')
        return boat

    class Meta:
        model = Tariff
        exclude = ('weight', )