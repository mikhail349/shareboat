from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import Tariff

class TariffForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TariffForm, self).__init__(*args, **kwargs)

    def clean_boat(self):
        boat = self.cleaned_data.get('boat')
        if boat:
            if boat.owner != self.request.user or not boat.is_active:
                raise ValidationError('Не найдена')
        return boat

    class Meta:
        model = Tariff
        exclude = ('weight', )