from django.forms import ModelForm
from .models import Tariff

class TariffForm(ModelForm):
    class Meta:
        model = Tariff
        exclude = ('weight', )