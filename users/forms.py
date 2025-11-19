from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

from users.models import CustomUser


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'phone_number', 'country', 'avatar')


class ProfileUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'phone_number', 'country', 'avatar')
        widgets = {'email': forms.EmailInput(attrs={'readonly': True})}

