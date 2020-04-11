from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PrivateUserApiTests(TestCase):
    """Tests for Authenticated Requests to the API"""

    VALID_USER_EMAIL = "peterlustig@web.de"
    VALID_PASSWORD = "L03w3nza4n!"
    VALID_USERNAME = "Lustig, Peter"
    VALID_PAYLOAD = {
        'email': VALID_USER_EMAIL,
        'password': VALID_PASSWORD,
        'name': VALID_USERNAME,
    }

    def setUp(self):
        self.user = create_user(
            email=self.VALID_USER_EMAIL,
            password=self.VALID_PASSWORD,
            name=self.VALID_USERNAME,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_soccess(self):
        """Test retrieving provile for logged in user"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed_on_me_url(self):
        """Test that Post Endpoint is not allowed on Me Url"""
        response = self.client.post(ME_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def test_updated_user_profile(self):
        """Test updateing the user profile for authenticated user"""
        payload = self.VALID_PAYLOAD
        payload["password"] = "NewSecurePassword123!"
        response = self.client.put(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
