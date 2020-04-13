from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPIES_URL = reverse('recipe:recipe-list')


def create_sample_recipe(user, **params):
    """create and return a sample recipe"""
    defaults = {
        "title": 'Sample recipe',
        "time_minutes": 10,
        "price": 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Tests of publicly available """

    def setUp(self):
        client = APIClient()

    def test_recipe_requires_authentication(self):
        response = self.client.get(RECIPIES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Tests of Recipe Api which are allowed to authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@abc.bla",
            password="Password123!"
        )
        self.client.force_authenticate(self.user)

    def test_list_recipes_successfull(self):
        """Test if Recipe List is available for authenticated Users"""
        Recipe.objects.create(
            title="Jambalaya",
            user=self.user,
            price=10.4,
            time_minutes=5
        )
        Recipe.objects.create(
            title="Gumbo",
            user=self.user,
            price=5.2,
            time_minutes=7*60+10
        )

        response = self.client.get(RECIPIES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that created recipes are only visible for the user which created"""
        user2 = get_user_model().objects.create_user(
            email="other@testuser.bla",
            password="Password123!",
        )
        Recipe.objects.create(
            user=user2,
            title="Dirty Rice",
            price=4.10,
            time_minutes=1*60
        )
        Recipe.objects.create(
            user=self.user,
            title="Cajun Rub",
            price=5.0,
            time_minutes=4*10
        )

        response = self.client.get(RECIPIES_URL)

        all_recipes_from_database = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(all_recipes_from_database, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)
