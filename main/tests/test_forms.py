from django.test import TestCase

from main.forms import *


class AddQuestionFormTest(TestCase):
    def test_empty_content(self):
        form = AddQuestionForm(data={'content': ''})
        self.assertFalse(form.is_valid())

    def test_too_small_content(self):
        form = AddQuestionForm(data={'content': 'my question'})
        self.assertFalse(form.is_valid())


class QuestionDetailFormTest(TestCase):
    def test_empty_content(self):
        form = QuestionDetailForm(data={'answer_text': ''})
        self.assertFalse(form.is_valid())
