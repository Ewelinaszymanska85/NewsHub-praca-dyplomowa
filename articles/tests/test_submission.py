from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Article, Notification


class ArticleSubmissionTests(TestCase):
    """
    Testy zgłaszania artykułów przez zalogowanych użytkowników
    oraz automatycznego tworzenia powiadomień (sygnał).
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")

    def test_anonymous_user_cannot_submit_article(self):
        response = self.client.post('/api/articles/', {
            "title": "Próba bez logowania",
            "content": "Treść",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_submit_article_as_pending(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/articles/', {
            "title": "Zgłoszony artykuł testowy",
            "content": "Treść zgłoszenia",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        article = Article.objects.get(title="Zgłoszony artykuł testowy")
        self.assertEqual(article.status, "PENDING")
        self.assertEqual(article.submitted_by, self.user)

    def test_submitting_article_creates_notification(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/articles/', {
            "title": "Artykuł generujący powiadomienie",
            "content": "Treść",
        })
        self.assertTrue(
            Notification.objects.filter(
                article__title="Artykuł generujący powiadomienie"
            ).exists()
        ) 