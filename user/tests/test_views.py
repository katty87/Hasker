from django.test import TestCase
from django.urls import reverse

from user.models import UserProfile


class SignUpViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/user/signup')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/signup.html')


class SettingsViewTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user('user1', 'test@test.com', '12345')
        self.user.avatar = 'default_avatar.png'
        self.user.save()
        self.client.login(username='user1', password='12345')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/user/settings/{}/'.format(self.user.id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('settings', args=(self.user.id,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('settings', args=(self.user.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/user_settings.html')
