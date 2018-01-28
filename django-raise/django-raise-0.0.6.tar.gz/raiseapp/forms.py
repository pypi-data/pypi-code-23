from django import forms

from . import models


class ReminderForm(forms.ModelForm):
    class Meta:
        model = models.Reminder
        fields = [
            'email'
        ]


class PledgeForm(forms.ModelForm):
    class Meta:
        model = models.Pledge
        fields = [
            'email',
            'name',
            'amount',
        ]
