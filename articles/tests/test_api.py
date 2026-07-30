from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Article, Category


class ArticleAPITests(TestCase):
    """
    Testy integracyjne publicznego API artykułów (odczyt).
    """

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Technologia")
        self.approved_article = Article.objects.create(
            title="Zatwierdzony artykuł",
            content="Treść",
            category=self.category,
            status="APPROVED",
        )
        self.pending_article = Article.objects.create(
            title="Oczekujący artykuł",
            content="Treść",
            status="PENDING",
        )

    def test_get_articles_list_returns_200(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_list_shows_only_approved_articles(self):
        """
        Publiczne API powinno pokazywać TYLKO artykuły APPROVED,
        artykuły PENDING nie powinny być widoczne.
        """
        response = self.client.get('/api/articles/')
        data = response.data['results'] if 'results' in response.data else response.data
        titles = [article['title'] for article in data]
        self.assertIn("Zatwierdzony artykuł", titles)
        self.assertNotIn("Oczekujący artykuł", titles)

    def test_get_nonexistent_article_returns_404(self):
        response = self.client.get('/api/articles/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 