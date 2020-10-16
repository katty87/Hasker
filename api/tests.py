from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.db.models import Exists, OuterRef

from user.tests.fixtures import UserFactory
from main.tests.fixtures import QuestionFactory, TagFactory, QuestionVoteFactory
from Hasker.settings.base import QUESTIONS_PER_PAGE
from main.models import Question, Tag


class AuthTests(APITestCase):
    def test_correct_credentials(self):
        url = reverse('api:token_obtain_pair')

        user = UserFactory.create()
        data = {
            'username': user.username,
            'password': '12345'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_credentials(self):
        url = reverse('api:token_obtain_pair')

        data = {
            'username': 'new',
            'password': 'test123'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class QuestionListTests(APITestCase):
    HOT_QUESTION_HEADER = "hot question"
    YESTERDAY_QUESTION_HEADER = "yesterday question"

    @classmethod
    def setUpTestData(cls):
        QuestionFactory.create_batch(QUESTIONS_PER_PAGE - 4)

        tag1 = TagFactory.create(name="django")
        tag2 = TagFactory.create(name="java")

        QuestionFactory.create(header='Set up a scheduled job?',
                               content="I've been working on a web app using Django, and I'm curious "
                                       "if there is a way to schedule a job to run periodically. ",
                               tags=(tag1, tag2))

        QuestionFactory.create(header='How to create first Django app?',
                               content='I am new at programming. Can anybody recommend me a tutorial?',
                               tags=(tag1,))
        QuestionFactory.create(tags=(tag2,))

        question = QuestionFactory.create(header=cls.HOT_QUESTION_HEADER)
        QuestionVoteFactory.create(question=question)

        yesterday = datetime.now() - timedelta(days=1)
        QuestionFactory.create(header=cls.YESTERDAY_QUESTION_HEADER, create_date=yesterday)
        QuestionFactory.create(header=cls.YESTERDAY_QUESTION_HEADER, create_date=yesterday)
        QuestionFactory.create(header=cls.YESTERDAY_QUESTION_HEADER, create_date=yesterday)

    def setUp(self):
        user = UserFactory.create()
        self.token = Token.objects.get_or_create(user=user)[0].key

    def test_hot_questions(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = reverse('api:questions-hot')
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), QUESTIONS_PER_PAGE)
        self.assertEqual(response.data['results'][0]['header'], self.HOT_QUESTION_HEADER)

    def test_new_questions(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = reverse('api:questions-new')
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), QUESTIONS_PER_PAGE)

        for item in response.data['results']:
            self.assertNotEqual(response.data['results'][0]['header'], self.YESTERDAY_QUESTION_HEADER)

    def test_trending_questions(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = reverse('api:questions-trending')
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]['header'], self.HOT_QUESTION_HEADER)

    def test_search_by_text(self):
        search_string = 'django'
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = reverse('api:questions')
        response = client.get(url, {'search': search_string}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),
                         len(Question.objects.filter(Q(header__icontains=search_string) |
                                                     Q(content__icontains=search_string))))

    def test_search_by_tag(self):
        search_tag = 'django'
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = reverse('api:questions')
        response = client.get(url, {'tag': search_tag}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),
                         len(Question.objects.filter(
                            Exists(Tag.objects.filter(question=OuterRef('pk'), name=search_tag))
                        )))

    def test_question_detail(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        question = Question.objects.first()

        url = reverse('api:question-detail', args=[question.id])
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['header'], question.header)
        self.assertEqual(response.data['content'], question.content)



