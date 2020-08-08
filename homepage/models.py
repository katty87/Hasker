from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Sum
import os


def get_image_path(instance, filename):
    return os.path.join('profile_images', "{}".format(instance.id), filename)


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, upload_to=get_image_path, storage=OverwriteStorage())


class Tag(models.Model):
    name = models.CharField(max_length=32)


class Question(models.Model):
    header = models.CharField(max_length=256)
    content = models.CharField(max_length=4096)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_author')
    create_date = models.DateTimeField()
    tags = models.ManyToManyField(Tag)

    def vote_count(self):
        cnt = QuestionVote.objects.filter(question_id=self.id).aggregate(Sum('value')).get('value__sum')
        return cnt if cnt else 0

    def current_user_vote(self, user_id):
        try:
            question_vote = QuestionVote.objects.get(question_id=self.id, user_id=user_id)
        except QuestionVote.DoesNotExist:
            return 0

        return question_vote.value


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=4096)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_author')
    create_date = models.DateTimeField()
    is_correct = models.BooleanField()

    def current_user_vote(self, user_id):
        try:
            answer_vote = AnswerVote.objects.get(answer_id=self.id, user_id=user_id)
        except AnswerVote.DoesNotExist:
            return 0

        return answer_vote.value


class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)


class QuestionVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)





