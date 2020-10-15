from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user.tests.fixtures import UserFactory


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
