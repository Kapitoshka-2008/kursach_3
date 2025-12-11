from django import forms
from django.conf import settings

from mailings.models import Mailing, Message, Recipient


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'body')


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ('email', 'full_name', 'comment')


class MailingForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )

    class Meta:
        model = Mailing
        fields = ('start_time', 'end_time', 'status', 'message', 'recipients')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Limit choices to objects owned by user; managers can see all.
            is_manager = user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()
            if not is_manager:
                self.fields['message'].queryset = Message.objects.filter(owner=user)
                self.fields['recipients'].queryset = Recipient.objects.filter(owner=user)
