from django.forms import ModelForm, PasswordInput 
from django.utils.translation import ugettext_lazy as _
from .models import User

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        labels = {
            'email': _('Эл. почта'),
            'password': 'Пароль'
        }
        widgets = {
            'password': PasswordInput
        }
    #email = forms.EmailField(lab)
    #password = forms.CharField(widget=forms.PasswordInput)