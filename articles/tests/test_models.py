from django.test import TestCase
from ..models import Article, Category, Notification 


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
        
    def test_category_creation(self):
        category = Category.objects.create(name="Testowa kategoria numer dwa")
        self.assertEqual(category.name, "Testowa kategoria numer dwa") 
        
class NotificationModelTests(TestCase):
    """
    Testy modelu Notification.
    """

    def test_notification_is_unread_by_default(self):
        """Nowo utworzone powiadomienie powinno mieć is_read=False."""
        article = Article.objects.create(title="Artykuł testowy", content="Treść")
        notification = Notification.objects.create(
            article=article,
            message="Nowy artykuł oczekuje na moderację",
        )
        self.assertFalse(notification.is_read)

    def test_notification_string_representation(self):
        """__str__ powinien zwracać treść wiadomości powiadomienia."""
        article = Article.objects.create(title="Artykuł testowy 2", content="Treść")
        notification = Notification.objects.create(
            article=article,
            message="Testowa wiadomość powiadomienia",
        )
        self.assertEqual(str(notification), "Testowa wiadomość powiadomienia")

    def test_notifications_ordered_newest_first(self):
        """Powiadomienia powinny być sortowane od najnowszego (ordering = ['-created_at'])."""
        article = Article.objects.create(title="Artykuł testowy 3", content="Treść")
        first = Notification.objects.create(article=article, message="Pierwsze")
        second = Notification.objects.create(article=article, message="Drugie")

        notifications = list(Notification.objects.all())
        self.assertEqual(notifications[0], second)
        self.assertEqual(notifications[1], first) 