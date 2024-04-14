"""Tests  for the tags API"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe
)

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@examp.com', password='testpass'):
    """Create and return a User"""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """Test the publicly/Unauthenticated available tags API"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authenticated available tags API"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test the list of tags is limited to authenticated user"""
        user2 = create_user(email='bard@me.com', password='testpass2')
        Tag.objects.create(user=user2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertIn(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Apple Pie',
            time_minutes=10,
            price=Decimal('4.50')
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list"""
        tag = Tag.objects.create(user=self.user, name='Eggs')
        Tag.objects.create(user=self.user, name='Milk')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Apple Pie',
            time_minutes=10,
            price=Decimal('3.50')
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Apple cider',
            time_minutes=5,
            price=Decimal('5.50')
        )
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
