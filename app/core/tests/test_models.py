from django.test import TestCase
from django.contrib.auth import get_user_model


class ModeTests(TestCase):

    def test_create_user_with_email_successsfull(self):
        """ Test creating a new user with an email """
        email = 'test@pythonapp.bla'
        password = '5t0ngP455w0rd!'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
