from django import forms
from django.forms.widgets import Textarea
from .models import Computer, Task


class NewTaskForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        required=True
    )
    run_as = forms.CharField(
        label="Execute as",
        initial="root",
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

    class Meta:
        model = Task
        fields = ['name', 'run_as', 'computers', 'payload']

