from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # avatar = models.ImageField(required=False)
    birth_date = models.DateField(null=True, blank=True)


class Question(models.Model):
    header = models.CharField(max_length=256)
    content = models.CharField(max_length=4096)
    # user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='question_user')
    create_date = models.DateTimeField()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=4096)
    # user = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_user')
    is_correct = models.BooleanField()

