from datetime import datetime

from django.test import TestCase

from main.models import Question, QuestionVote, Answer, AnswerVote
from user.models import UserProfile
from user.tests.fixtures import UserFactory


class QuestionModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserFactory()
        Question.objects.create(header='How to ...?', content='Some text', create_date=datetime.now(),
                                user=user)
        UserFactory.create_batch(3)

    def test_no_votes_sum(self):
        user1 = UserProfile.objects.all()[0]
        question = Question.objects.filter(user=user1).first()
        self.assertEqual(question.vote_sum(), 0)

    def test_cancel_vote_sum(self):
        users = UserProfile.objects.all()
        question = Question.objects.filter(user=users[0]).first()

        question_vote = QuestionVote()
        question_vote.question = question
        question_vote.user = users[1]
        question_vote.value = 1
        question_vote.save()

        question_vote.value = 0
        question_vote.save()

        self.assertEqual(question.vote_sum(), 0)

    def test_below_zero_vote_sum(self):
        users = UserProfile.objects.all()
        question = Question.objects.filter(user=users[0]).first()

        vote_question(question, users[1], -1)
        vote_question(question, users[2], -1)
        vote_question(question, users[3], 1)

        self.assertEqual(question.vote_sum(), -1)

    def test_above_zero_vote_sum(self):
        users = UserProfile.objects.all()
        question = Question.objects.filter(user=users[0]).first()

        vote_question(question, users[1], 1)
        vote_question(question, users[2], -1)
        vote_question(question, users[3], 1)

        self.assertEqual(question.vote_sum(), 1)

    def test_current_user_vote(self):
        users = UserProfile.objects.all()
        question = Question.objects.filter(user=users[0]).first()

        vote_question(question, users[1], 1)
        self.assertEqual(question.current_user_vote(users[1].id), 1)


def vote_question(question, user, value):
    question_vote = QuestionVote()
    question_vote.question = question
    question_vote.user = user
    question_vote.value = value
    question_vote.save()


class AnswerModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserFactory()
        question = Question.objects.create(header='How to install Django?',
                                           content="I'm trying to setup a Django project...",
                                           create_date=datetime.now(),
                                           user=user)

        Answer.objects.create(content="Use pip install Django.", question=question, user=user,
                              create_date=datetime.now(), is_correct=0)
        UserFactory.create_batch(3)

    def test_no_votes_sum(self):
        answer = Answer.objects.get(id=1)
        self.assertEqual(answer.vote_sum(), 0)

    def test_cancel_vote_sum(self):
        answer = Answer.objects.get(id=1)

        answer_vote = AnswerVote()
        answer_vote.answer = answer
        answer_vote.user = UserProfile.objects.exclude(id=answer.user.id)[0]
        answer_vote.value = 1
        answer_vote.save()

        answer_vote.value = 0
        answer_vote.save()

        self.assertEqual(answer.vote_sum(), 0)

    def test_below_zero_vote_sum(self):
        answer = Answer.objects.get(id=1)
        users = UserProfile.objects.exclude(id=answer.user.id)

        vote_answer(answer, users[0], -1)
        vote_answer(answer, users[1], -1)
        vote_answer(answer, users[2], 1)

        self.assertEqual(answer.vote_sum(), -1)

    def test_above_zero_vote_sum(self):
        answer = Answer.objects.get(id=1)
        users = UserProfile.objects.exclude(id=answer.user.id)

        vote_answer(answer, users[0], 1)
        vote_answer(answer, users[1], -1)
        vote_answer(answer, users[2], 1)

        self.assertEqual(answer.vote_sum(), 1)

    def test_current_user_vote(self):
        answer = Answer.objects.get(id=1)
        user = UserProfile.objects.exclude(id=answer.user.id)[0]

        vote_answer(answer, user, 1)
        self.assertEqual(answer.current_user_vote(user.id), 1)


def vote_answer(answer, user, value):
    answer_vote = AnswerVote()
    answer_vote.answer = answer
    answer_vote.user = user
    answer_vote.value = value
    answer_vote.save()
