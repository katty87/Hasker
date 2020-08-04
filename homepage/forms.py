from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from homepage.models import UserProfile


class SignUpForm(UserCreationForm):
    # birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    avatar = forms.ImageField(help_text='Load picture', required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',)

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