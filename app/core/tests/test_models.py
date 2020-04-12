from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Tag, Ingredient


def sample_user(email='testkarl@karlo.com', password='L0tt0K!ngKar1!'):
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
    )
    return user


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

    def test_tag_str(self):
        """Test the Tag string representation"""
        tag = Tag.objects.create(
            user=sample_user(),
            name="Vegan"
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """Test the Ingredients string representation"""
        ingredients = Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )

        self.assertEqual(str(ingredients), ingredients.name)
