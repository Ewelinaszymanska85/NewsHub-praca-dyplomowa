from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from ..models import Article, Category, Notification, UserProfile 


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
        
class UserProfileModelTests(TestCase):
    """
    Testy modelu UserProfile - relacja OneToOne z User.
    """

    def test_userprofile_creation_and_one_to_one_relation(self):
        """
        Sprawdza poprawność relacji OneToOne - profil jest powiązany
        z dokładnie jednym użytkownikiem, dostępnym z obu stron relacji.
        """
        user = User.objects.create_user(username="profil_user", password="TestPass123!")
        profile = UserProfile.objects.create(user=user, bio="Testowy opis użytkownika")

        self.assertEqual(profile.user, user)
        # Dzięki related_name="profile", z poziomu User można dotrzeć
        # do jego profilu w drugą stronę relacji
        self.assertEqual(user.profile, profile)

    def test_userprofile_string_representation(self):
        """__str__ powinien zawierać nazwę użytkownika."""
        user = User.objects.create_user(username="anna_test", password="TestPass123!")
        profile = UserProfile.objects.create(user=user)

        self.assertEqual(str(profile), "Profil anna_test")

    def test_user_can_have_only_one_profile(self):
        """
        Relacja OneToOne wymusza unikalność - nie można utworzyć
        drugiego profilu dla tego samego użytkownika.
        """
        user = User.objects.create_user(username="jeden_profil", password="TestPass123!")
        UserProfile.objects.create(user=user)

        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=user)