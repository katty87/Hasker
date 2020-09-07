from django.test import TestCase

from homepage.forms import SignUpForm, UserSettings, AddQuestionForm, QuestionDetailForm


class SignUpFormTest(TestCase):
    def test_signup_form_avatar_help_text(self):
        form = SignUpForm()
        self.assertEqual(form.fields['avatar'].help_text, 'Load picture up to 1MB')


class UserSettingsFormTest(TestCase):
    def test_signup_form_avatar_help_text(self):
        form = UserSettings()
        self.assertEqual(form.fields['avatar'].help_text, 'Load picture up to 1MB')


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
