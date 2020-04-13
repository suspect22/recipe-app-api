from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPIES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_recipe(user, **params):
    """create and return a sample recipe"""
    defaults = {
        "title": 'Sample recipe',
        "time_minutes": 10,
        "price": 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_sample_ingredient(user, name="Cajun Rub"):
    """create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)

def create_sample_tag(user, name="creolic"):
    """create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing Recipe Detail"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a basic Recipe"""
        payload = {
            'title': 'Chocolate Cookies',
            'time_minutes': 30,
            'price': 5.00
        }

        response = self.client.post(RECIPIES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tag(self):
        """Test create a Recipe with Tags"""
        tag1 = create_sample_tag(user=self.user, name="Vegetarian")
        tag2 = create_sample_tag(user=self.user, name="Vegan")
        payload = {
            'title': 'Lynchburg Lemonade',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 10,
            'price': 4.20
        }
        response = self.client.post(RECIPIES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test create recipe with Ingredients"""
        ingredient1 = create_sample_ingredient(user=self.user, name="Ginger")
        ingredient2 = create_sample_ingredient(user=self.user, name="Beer")
        payload = {
            'title': 'Ginger Beer',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 1,
            'price': 2.4
        }
        response = self.client.post(RECIPIES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
