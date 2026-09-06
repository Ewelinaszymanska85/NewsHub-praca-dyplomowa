from django.test import TestCase
from rest_framework.test import APIClient

from ..models import Article, Category


class ArticleAPITests(TestCase):
    """
    Testy integracyjne własnej logiki publicznego API artykułów.
    """

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="Technologia"
        )

        Article.objects.create(
            title="Zatwierdzony artykuł",
            content="Treść",
            category=self.category,
            status="APPROVED",
        )

        Article.objects.create(
            title="Oczekujący artykuł",
            content="Treść",
            status="PENDING",
        )

    def test_public_list_shows_only_approved_articles(self):
        response = self.client.get("/api/articles/")

        data = response.data["results"]

        titles = [
            article["title"]
            for article in data
        ]

        self.assertIn(
            "Zatwierdzony artykuł",
            titles,
        )

        self.assertNotIn(
            "Oczekujący artykuł",
            titles,
        )
