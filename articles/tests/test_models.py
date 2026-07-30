from django.test import TestCase
from ..models import Article, Category


class ArticleModelTests(TestCase):
    def test_article_creation_has_default_pending_status(self):
        category = Category.objects.create(name="Testowa kategoria")
        article = Article.objects.create(
            title="Testowy artykuł",
            content="Treść testowa",
            category=category,
        )
        self.assertEqual(article.status, "PENDING")

    def test_article_string_representation(self):
        article = Article.objects.create(title="Mój tytuł", content="Treść")
        self.assertEqual(str(article), "Mój tytuł") 