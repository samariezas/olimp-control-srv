from django import forms
from django.forms.widgets import Textarea
from .models import Computer, Task


class ComputerMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if obj.location:
            location_name = obj.location.name
        else:
            location_name = 'Unknown location'
        return f'{location_name}: {obj.name}'


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
    computers = ComputerMultipleChoiceField(
        queryset=Computer.objects.order_by(
            "location__sequence_num",
            "location__name",
            "sequence_num",
            "name"
        ),
        widget=forms.SelectMultiple,
        required=True,
    )
    payload = forms.CharField(
        label="Payload",
        widget=Textarea,
        required=True
    )

    class Meta:
        model = Task
        fields = ['name', 'run_as', 'computers', 'payload']

