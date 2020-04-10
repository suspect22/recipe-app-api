from django.test import TestCase
from django.contrib.auth import get_user_model


class ModeTests(TestCase):

    INVALID_PASSWORD = "123"
    VALID_PASSWORD = "5t0ngP455w0rd!"
    VALID_EMAILADDRESS = "test@pythonapp.bla"
    VALID_EMAILADDRESS_UGLY = "test@pythonaPP.Bla"

    def test_create_user_with_email_successsfull(self):
        """ Test creating a new user with an email """
        email = self.VALID_EMAILADDRESS
        password = self.VALID_PASSWORD
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """ Test lowercase saving of emailaddress"""
        email = self.VALID_EMAILADDRESS_UGLY

        user = get_user_model().objects.create_user(email, self.VALID_PASSWORD)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Test creating user with no email raises errror """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, self.VALID_PASSWORD)

    def test_create_new_superuser(self):
        """ Test create a new superuser"""
        user = get_user_model().objects.create_superuser(
            email=self.VALID_EMAILADDRESS,
            password=self.VALID_PASSWORD
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
