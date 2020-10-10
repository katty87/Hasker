from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from main.models import Question, Tag
from user.models import UserProfile

from user.tests.fixtures import UserFactory


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_questions = 23

        user = UserFactory()
        for question_num in range(number_of_questions):
            Question.objects.create(
                header='How to do thing #{}?'.format(question_num),
                content='I want to do thing #{} but I am stuck. Can anybody help me?'.format(question_num),
                create_date=datetime.now(),
                user=user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/main/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')

    def test_pagination_is_twenty(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['question_list']) == 20)

    def test_lists_all_questions(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['question_list']) == 3)


class SearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserFactory()
        question_instance = Question.objects.create(
            header='How to create first Django app?',
            content='I am new at programming. Can anybody recommend me Django tutorial?',
            create_date=datetime.now(),
            user=user)

        tag = Tag()
        tag.name = 'django'
        tag.save()
        question_instance.tags.add(tag)
        question_instance.save()

        question_instance = Question.objects.create(
            header='Set up a scheduled job?',
            content="I've been working on a web app using Django, and I'm curious "
                    "if there is a way to schedule a job to run periodically. ",
            create_date=datetime.now(),
            user=user)

        tag = Tag()
        tag.name = 'django'
        tag.save()
        question_instance.tags.add(tag)
        question_instance.save()

        question_instance = Question.objects.create(
            header='How to change the color of any panel in java?',
            content='How I can change the color of JPanel after some time delay like 1 second.',
            create_date=datetime.now(),
            user=user)

        tag = Tag()
        tag.name = 'java'
        tag.save()
        question_instance.tags.add(tag)
        question_instance.save()

        number_of_questions = 20

        for question_num in range(number_of_questions):
            Question.objects.create(
                header='How to do thing #{}?'.format(question_num),
                content='I want to do thing #{} but I am stuck. Can anybody help me?'.format(question_num),
                create_date=datetime.now(),
                user=user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/main/search')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('search_results'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('search_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/search_results.html')

    def test_pagination_is_twenty(self):
        response = self.client.get(reverse('search_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['question_list']) == 20)

    def test_search_all_questions(self):
        response = self.client.get(reverse('search_results') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['question_list']) == 3)

    def test_search_by_text(self):
        response = self.client.get(reverse('search_results') + '?q=django')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['question_list']) == 2)

    def test_search_by_empty_string(self):
        response = self.client.get(reverse('search_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['question_list']) == 20)

    def test_search_no_results(self):
        response = self.client.get(reverse('search_results') + '?q=qweqweqw')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['question_list']) == 0)

    def test_search_by_tag(self):
        response = self.client.get(reverse('search_results') + '?q=tag:django')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['question_list']) == 2)


class AskQuestionViewTest(TestCase):
    def setUp(self):
        user = UserFactory()
        user.avatar = 'default_avatar.png'
        user.save()
        self.client.login(username=user.username, password='12345')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/main/ask')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('ask'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('ask'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/add_question.html')


class QuestionDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_questions = 3

        user = UserFactory()
        user.avatar = 'default_avatar.png'
        user.save()
        for question_num in range(number_of_questions):
            Question.objects.create(
                header='How to do thing #{}?'.format(question_num),
                content='I want to do thing #{} but I am stuck. Can anybody help me?'.format(question_num),
                create_date=datetime.now(),
                user=user)

    def test_view_url_exists_at_desired_location(self):
        question = Question.objects.all().first()
        response = self.client.get('/main/question/{}/'.format(question.id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        question = Question.objects.all().first()
        response = self.client.get(reverse('question_detail', args=(question.id,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        question = Question.objects.all().first()
        response = self.client.get(reverse('question_detail', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/detail_question.html')

    def test_view_incorrect_question_id(self):
        response = self.client.get(reverse('question_detail', args=(10,)))
        self.assertEqual(response.status_code, 404)







