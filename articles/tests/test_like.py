from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Article, Like


class LikeTests(TestCase):
    """
    Testy mechanizmu polubień artykułów.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="liker", password="TestPass123!")
        self.article = Article.objects.create(
            title="Artykuł do polubienia",
            content="Treść",
            status="APPROVED",
        )

    def test_anonymous_user_cannot_like_article(self):
        response = self.client.post(f'/api/articles/{self.article.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_like_article(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/articles/{self.article.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
        self.assertTrue(Like.objects.filter(user=self.user, article=self.article).exists())

    def test_liking_twice_toggles_to_unlike(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(f'/api/articles/{self.article.id}/like/')
        response = self.client.post(f'/api/articles/{self.article.id}/like/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertFalse(Like.objects.filter(user=self.user, article=self.article).exists()) 