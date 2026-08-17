from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class ArticleValidationTests(TestCase):
    """
    Testy walidacji danych wejściowych przy tworzeniu artykułu przez API.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="validator", password="TestPass123!")
        self.client.force_authenticate(user=self.user)

    def test_article_without_title_is_rejected(self):
        """
        Zgłoszenie artykułu bez wymaganego pola 'title' powinno
        zostać odrzucone z kodem 400 i czytelnym komunikatem błędu.
        """
        response = self.client.post('/api/articles/', {
            "content": "Treść bez tytułu",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_article_without_content_is_rejected(self):
        """
        Zgłoszenie artykułu bez wymaganego pola 'content' powinno
        zostać odrzucone z kodem 400.
        """
        response = self.client.post('/api/articles/', {
            "title": "Tytuł bez treści",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_article_with_invalid_source_url_is_rejected(self):
        """
        Pole source_url powinno akceptować tylko poprawne adresy URL
        (walidacja URLField).
        """
        response = self.client.post('/api/articles/', {
            "title": "Artykuł z błędnym linkiem",
            "content": "Treść",
            "source_url": "to-nie-jest-poprawny-url",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("source_url", response.data)

    def test_article_with_valid_data_is_accepted(self):
        """
        Kontrolny test pozytywny - poprawne dane powinny zostać
        zaakceptowane (żeby upewnić się, że powyższe testy faktycznie
        sprawdzają walidację, a nie ogólny błąd serwera).
        """
        response = self.client.post('/api/articles/', {
            "title": "Poprawny artykuł",
            "content": "Poprawna treść",
            "source_url": "https://example.com/news/1",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 
        