from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from homepage.models import UserProfile


class SignUpForm(UserCreationForm):
    avatar = forms.ImageField(help_text='Load picture up to 1MB', required=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', False)
        if avatar:
            if avatar.size > 1 * 1024 * 1024:
                raise ValidationError("Avatar picture too big ( > 1mb )")

            width, height = get_image_dimensions(avatar.file)

            if width < 100 or height < 100:
                raise ValidationError("Avatar picture must be at least 100x100 pixels")

            return avatar
        else:
            raise ValidationError("Couldn't read uploaded image")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class AddQuestionForm(forms.Form):
    title = forms.CharField(label='Title', max_length=256, required=True)
    content = forms.CharField(label='Text', max_length=4096, required=True)

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



