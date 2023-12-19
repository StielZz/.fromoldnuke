from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Statuses

class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ChangeProjectInfoForm(forms.Form):
    new_status = forms.ModelChoiceField(
        queryset=Statuses.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    new_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=False,
    )