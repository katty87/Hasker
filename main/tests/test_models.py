from django.test import TestCase
from datetime import datetime

from main.models import Question, QuestionVote, Answer, AnswerVote
from user.models import UserProfile


class QuestionModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserProfile.objects.create_user('user1', 'test@test.com', '12345')
        Question.objects.create(header='How to ...?', content='Some text', create_date=datetime.now(),
                                user=user)

        UserProfile.objects.create_user('user2', 'test2@test.com', '12345')
        UserProfile.objects.create_user('user3', 'test3@test.com', '12345')
        UserProfile.objects.create_user('user4', 'test4@test.com', '12345')

    def test_no_votes_sum(self):
        user1 = UserProfile.objects.get(username='user1')
        question = Question.objects.filter(user=user1).first()
        self.assertEqual(question.vote_sum(), 0)

    def test_cancel_vote_sum(self):
        user1 = UserProfile.objects.get(username='user1')
        question = Question.objects.filter(user=user1).first()
        user = UserProfile.objects.get(username='user2')

        question_vote = QuestionVote()
        question_vote.question = question
        question_vote.user = user
        question_vote.value = 1
        question_vote.save()

        question_vote.value = 0
        question_vote.save()

        self.assertEqual(question.vote_sum(), 0)

    def test_below_zero_vote_sum(self):
        user1 = UserProfile.objects.get(username='user1')
        question = Question.objects.filter(user=user1).first()
        user2 = UserProfile.objects.get(username='user2')
        user3 = UserProfile.objects.get(username='user3')
        user4 = UserProfile.objects.get(username='user4')

        vote_question(question, user2, -1)
        vote_question(question, user3, -1)
        vote_question(question, user4, 1)

        self.assertEqual(question.vote_sum(), -1)

    def test_above_zero_vote_sum(self):
        user1 = UserProfile.objects.get(username='user1')
        question = Question.objects.filter(user=user1).first()
        user2 = UserProfile.objects.get(username='user2')
        user3 = UserProfile.objects.get(username='user3')
        user4 = UserProfile.objects.get(username='user4')

        vote_question(question, user2, 1)
        vote_question(question, user3, -1)
        vote_question(question, user4, 1)

        self.assertEqual(question.vote_sum(), 1)

    def test_current_user_vote(self):
        user1 = UserProfile.objects.get(username='user1')
        question = Question.objects.filter(user=user1).first()
        user = UserProfile.objects.get(username='user2')

        vote_question(question, user, 1)
        self.assertEqual(question.current_user_vote(user.id), 1)


def vote_question(question, user, value):
    question_vote = QuestionVote()
    question_vote.question = question
    question_vote.user = user
    question_vote.value = value
    question_vote.save()


class AnswerModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserProfile.objects.create_user('user1', 'test@test.com', '12345')
        question = Question.objects.create(header='How to install Django?',
                                           content="I'm trying to setup a Django project...",
                                           create_date=datetime.now(),
                                           user=user)

        Answer.objects.create(content="Use pip install Django.", question=question, user=user,
                              create_date=datetime.now(), is_correct=0)
        UserProfile.objects.create_user('user2', 'test2@test.com', '12345')
        UserProfile.objects.create_user('user3', 'test3@test.com', '12345')
        UserProfile.objects.create_user('user4', 'test4@test.com', '12345')

    def test_no_votes_sum(self):
        answer = Answer.objects.get(id=1)
        self.assertEqual(answer.vote_sum(), 0)

    def test_cancel_vote_sum(self):
        answer = Answer.objects.get(id=1)
        user = UserProfile.objects.get(username='user2')

        answer_vote = AnswerVote()
        answer_vote.answer = answer
        answer_vote.user = user
        answer_vote.value = 1
        answer_vote.save()

        answer_vote.value = 0
        answer_vote.save()

        self.assertEqual(answer.vote_sum(), 0)

    def test_below_zero_vote_sum(self):
        answer = Answer.objects.get(id=1)
        user2 = UserProfile.objects.get(username='user2')
        user3 = UserProfile.objects.get(username='user3')
        user4 = UserProfile.objects.get(username='user4')

        vote_answer(answer, user2, -1)
        vote_answer(answer, user3, -1)
        vote_answer(answer, user4, 1)

        self.assertEqual(answer.vote_sum(), -1)

    def test_above_zero_vote_sum(self):
        answer = Answer.objects.get(id=1)
        user2 = UserProfile.objects.get(username='user2')
        user3 = UserProfile.objects.get(username='user3')
        user4 = UserProfile.objects.get(username='user4')

        vote_answer(answer, user2, 1)
        vote_answer(answer, user3, -1)
        vote_answer(answer, user4, 1)

        self.assertEqual(answer.vote_sum(), 1)

    def test_current_user_vote(self):
        answer = Answer.objects.get(id=1)
        user = UserProfile.objects.get(username='user2')

        vote_answer(answer, user, 1)
        self.assertEqual(answer.current_user_vote(user.id), 1)


def vote_answer(answer, user, value):
    answer_vote = AnswerVote()
    answer_vote.answer = answer
    answer_vote.user = user
    answer_vote.value = value
    answer_vote.save()
