import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Aggregate, CharField
from django.db.models import Sum


class GroupConcat(Aggregate):
    function = 'STRING_AGG'
    # template = '%(function)s(%(distinct)s%(expressions)s%(ordering)s)'
    allow_distinct = True

    def __init__(self, expression, distinct=False, ordering=None, **extra):
        super(GroupConcat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            ordering=' ORDER BY %s' % ordering if ordering is not None else '',
            output_field=CharField(),
            **extra
        )

    def as_sql(self, compiler, connection, **extra_context):
        sql, params = super().as_sql(
            compiler, connection,  **extra_context
        )
        sql_len = len(sql)
        return sql[:sql_len-1] + ',\',\')', params


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

    def vote_sum(self):
        cnt = QuestionVote.objects.filter(question_id=self.id).aggregate(Sum('value')).get('value__sum')
        return cnt if cnt else 0

    def current_user_vote(self, user_id):
        try:
            return QuestionVote.objects.get(question_id=self.id, user_id=user_id)
        except QuestionVote.DoesNotExist:
            return 0


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=4096)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_author')
    create_date = models.DateTimeField()
    is_correct = models.BooleanField()

    def vote_sum(self):
        cnt = AnswerVote.objects.filter(answer_id=self.id).aggregate(Sum('value')).get('value__sum')
        return cnt if cnt else 0

    def current_user_vote(self, user_id):
        try:
            return AnswerVote.objects.get(answer_id=self.id, user_id=user_id)
        except AnswerVote.DoesNotExist:
            return 0


class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)


class QuestionVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)





