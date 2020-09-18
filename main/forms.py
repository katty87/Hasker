from django import forms
from django.core.exceptions import ValidationError


class AddQuestionForm(forms.Form):
    title = forms.CharField(max_length=256, required=True)
    content = forms.CharField(max_length=4096, required=True)

    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(AddQuestionForm, self).__init__(*args, **kwargs)
        self.fields['title'].error_messages = {'required': 'Title is missing.'}
        self.fields['content'].error_messages = {'required': 'Body is missing.'}

    def clean_content(self):
        content = self.cleaned_data['content']

        if len(content) < 100:
            raise ValidationError('Please enter at least 100 characters')

        return content


class QuestionDetailForm(forms.Form):
    answer_text = forms.CharField(max_length=4096, required=True)

    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(QuestionDetailForm, self).__init__(*args, **kwargs)
        self.fields['answer_text'].error_messages = {'required': 'Body is missing.'}



