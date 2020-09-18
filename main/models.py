from django.db import models
from django.db.models import Sum


from user.models import User


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


class BaseVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)


class AnswerVote(BaseVote):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)


class QuestionVote(BaseVote):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)





