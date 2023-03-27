from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import BooleanField, ModelForm, PasswordInput
from django.utils.translation import ugettext_lazy as _

from boat.models import Boat

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


class UpdateForm(ModelForm):
    is_boat_owner = BooleanField(label="Являюсь арендодателем",
                                 required=False)

    def clean_is_boat_owner(self):
        is_boat_owner = self.cleaned_data.get('is_boat_owner')
        if not is_boat_owner:
            if self.instance.boats.exclude(status=Boat.Status.DELETED) \
                                  .exists():
                raise ValidationError(
                    '- Для того чтобы перестать быть арендодателем, ' +
                    'необходимо удалить свой флот')
        return is_boat_owner

    def save(self, commit=True):
        m = super(UpdateForm, self).save(commit=False)

        boat_owner_group, _ = Group.objects.get_or_create(name='boat_owner')
        if self.cleaned_data.get('is_boat_owner', False):
            self.instance.groups.add(boat_owner_group)
        else:
            self.instance.groups.remove(boat_owner_group)

        if commit:
            m.save()
        return m

    class Meta:
        model = User
        fields = ('first_name', 'email_notification',
                  'is_boat_owner', 'use_dark_theme')
