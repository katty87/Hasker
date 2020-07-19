from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Question


class SignUpForm(UserCreationForm):
    # birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    # avatar = forms.ImageField(help_text='Load picture')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',)


class AddQuestionForm(forms.Form):
    header = forms.CharField(label='Title', max_length=256, required=True)
    content = forms.CharField(label='Text', max_length=4096, required=True)
