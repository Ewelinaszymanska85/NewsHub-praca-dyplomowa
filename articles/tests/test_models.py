from django.test import TestCase

from ..models import Article, Category, Notification


class ArticleModelTests(TestCase):

    def test_article_creation_has_default_pending_status(self):
        category = Category.objects.create(
            name="Testowa kategoria"
        )

        article = Article.objects.create(
            title="Testowy artykuł",
            content="Treść testowa",
            category=category,
        )

        self.assertEqual(
            article.status,
            "PENDING",
        )


class NotificationModelTests(TestCase):

    def test_notification_is_unread_by_default(self):
        article = Article.objects.create(
            title="Artykuł testowy",
            content="Treść",
        )

        notification = Notification.objects.create(
            article=article,
            message="Nowy artykuł oczekuje na moderację",
        )

        self.assertFalse(notification.is_read)
