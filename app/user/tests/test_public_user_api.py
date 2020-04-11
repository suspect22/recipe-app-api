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


class PublicUserApiTests(TestCase):
    """Test the API Endpoints which are available without Authentication"""

    VALID_USER_EMAIL = "peterlustig@web.de"
    VALID_PASSWORD = "L03w3nza4n!"
    VALID_USERNAME = "Lustig, Peter"

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successfull"""
        payload = {
            'email': self.VALID_USER_EMAIL,
            'password': self.VALID_PASSWORD,
            'name': self.VALID_USERNAME
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_create_duplicate_user_fails(self):
        """Check if duplicate Accounts are not possible"""
        payload = {
            'email': self.VALID_USER_EMAIL,
            'password': self.VALID_PASSWORD,
            'name': self.VALID_USERNAME
        }
        create_user(
            email=self.VALID_USER_EMAIL,
            password=self.VALID_PASSWORD,
            name=self.VALID_USERNAME
        )
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_too_short_password_fails(self):
        """Check if Passwords with less then 8 Characters are rejected"""
        payload = {
            'email': self.VALID_USER_EMAIL,
            'password': "short",
            'name': self.VALID_USERNAME
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_count = get_user_model().objects.filter(
            email=payload['email']
        ).count()
        self.assertEqual(user_count, 0)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': self.VALID_USER_EMAIL,
            'password': self.VALID_PASSWORD,
            'name': self.VALID_USERNAME
        }
        create_user(email=self.VALID_USER_EMAIL, password=self.VALID_PASSWORD)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_credentials(self):
        """Try if it is possible to get a Token with wrong credentials"""
        payload = {
            'email': self.VALID_USER_EMAIL,
            'password': "wrongPassword",
            'name': self.VALID_USERNAME
        }
        create_user(email=self.VALID_USER_EMAIL, password=self.VALID_PASSWORD)
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_if_user_doesnt_exists(self):
        """Try if it is possible to get a Token with an non existing user"""
        payload = {
            'email': self.VALID_USER_EMAIL,
            'password': self.VALID_PASSWORD,
            'name': self.VALID_USERNAME
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Try if it is possible to create a Token if a Field is Missing"""
        payload = {
            'email': self.VALID_USER_EMAIL,
            'password': self.VALID_PASSWORD,
            'name': self.VALID_USERNAME
        }

        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_management_requires_authentication(self):
        """Test that authentication is required for users"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
