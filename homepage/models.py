from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True)
    # birth_date = models.DateField(null=True, blank=True)


class Question(models.Model):
    header = models.CharField(max_length=256)
    content = models.CharField(max_length=4096)
    # user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='question_user')
    create_date = models.DateTimeField()

    def vote_count(self):
        cnt = QuestionVote.objects.filter(question_id=self.id).aggregate(Sum('value')).get('value__sum')
        return cnt if cnt else 0

    def current_user_vote(self):
        return 1


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=4096)
    # user = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_user')
    is_correct = models.BooleanField()


class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)


class QuestionVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)



