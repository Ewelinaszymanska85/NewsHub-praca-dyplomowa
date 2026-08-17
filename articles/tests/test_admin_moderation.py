from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Article


class ArticleModerationTests(TestCase):
    """
    Testy moderacji artykułów przez custom actions w panelu
    Django Admin (zatwierdzanie i odrzucanie artykułów).
    """

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="admin_test",
            password="AdminPass123!",
            email="admin@example.com",
        )
        self.client.login(username="admin_test", password="AdminPass123!")

        self.article1 = Article.objects.create(
            title="Artykuł do zatwierdzenia",
            content="Treść 1",
            status="PENDING",
        )
        self.article2 = Article.objects.create(
            title="Artykuł do odrzucenia",
            content="Treść 2",
            status="PENDING", 
        )

    def test_approve_action_changes_status_to_approved(self):
        """
        Uruchomienie akcji 'approve_articles' w panelu admina powinno
        zmienić status zaznaczonych artykułów na APPROVED.
        """
        self.client.post('/admin/articles/article/', {
            'action': 'approve_articles',
            '_selected_action': [self.article1.id],
        })

        self.article1.refresh_from_db()
        self.assertEqual(self.article1.status, "APPROVED")

    def test_reject_action_changes_status_to_rejected(self):
        """
        Uruchomienie akcji 'reject_articles' w panelu admina powinno
        zmienić status zaznaczonych artykułów na REJECTED.
        """
        self.client.post('/admin/articles/article/', {
            'action': 'reject_articles',
            '_selected_action': [self.article2.id],
        })

        self.article2.refresh_from_db()
        self.assertEqual(self.article2.status, "REJECTED")

    def test_approve_action_does_not_affect_other_articles(self):
        """
        Zatwierdzenie jednego artykułu nie powinno wpływać na status
        pozostałych, niezaznaczonych artykułów.
        """
        self.client.post('/admin/articles/article/', {
            'action': 'approve_articles',
            '_selected_action': [self.article1.id],
        })

        self.article2.refresh_from_db()
        self.assertEqual(self.article2.status, "PENDING")

    def test_non_staff_user_cannot_access_admin_panel(self):
        """
        Zwykły, niezalogowany (lub niebędący staff) użytkownik nie
        powinien mieć dostępu do panelu administracyjnego.
        """
        client = Client()
        response = client.get('/admin/articles/article/')
        # Django Admin przekierowuje niezalogowanych na stronę logowania
        self.assertEqual(response.status_code, 302) 