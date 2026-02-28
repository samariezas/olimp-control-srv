from django import forms
from django.forms.widgets import Textarea
from .models import Computer


class NewTaskForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=256,
        required=True
    )
    run_as = forms.CharField(
        label="Execute as",
        initial="root",
        max_length=128,
        required=True
    )
    computers = forms.ModelMultipleChoiceField(
        queryset=Computer.objects.all(),
        widget=forms.SelectMultiple,
        required=True,
    )
    payload = forms.CharField(
        label="Payload",
        widget=Textarea,
        max_length=16*1024,
        required=True
    )
