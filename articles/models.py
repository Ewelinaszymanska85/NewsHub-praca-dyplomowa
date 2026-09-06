from django.db import models
from django.conf import settings


class Category(models.Model):
    """
    Kategoria tematyczna artykułu (np. Technologia, Sport, Polityka).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa kategorii")

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tag przypisywany do artykułu, umożliwiający elastyczne oznaczanie treści.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Nazwa tagu")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tagi"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Artykuł - pochodzący z automatycznej agregacji RSS (source ustawione,
    submitted_by puste) albo zgłoszony przez użytkownika (submitted_by
    ustawione, source puste, wymaga moderacji).
    """

    STATUS_CHOICES = [
        ("PENDING", "Oczekujący"),
        ("APPROVED", "Zatwierdzony"),
        ("REJECTED", "Odrzucony"),
    ]

    title = models.CharField(max_length=500, verbose_name="Tytuł")
    content = models.TextField(verbose_name="Treść / streszczenie")
    source_url = models.URLField(max_length=500, blank=True, null=True, unique=True, verbose_name="Link źródłowy")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Data publikacji")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES, 
        default="PENDING",
        verbose_name="Status moderacji",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Kategoria",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="articles",
        blank=True,
        verbose_name="Tagi",
    )

    # Wypełnione dla artykułów pobranych automatycznie z RSS - FK do Source
    # (Source zdefiniujemy w aplikacji 'sources', dlatego używamy stringa
    # 'sources.Source', żeby uniknąć cyklicznego importu)
    source = models.ForeignKey(
        "sources.Source",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Źródło RSS",
    )

    # Wypełnione dla artykułów zgłoszonych ręcznie przez użytkownika
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="submitted_articles",
        verbose_name="Zgłoszone przez",
    )

    class Meta:
        verbose_name = "Artykuł"
        verbose_name_plural = "Artykuły"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class Like(models.Model):
    """
    Tabela pośrednia reprezentująca polubienie artykułu przez użytkownika.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Polubienie"
        verbose_name_plural = "Polubienia"
        # Zapobiega dwukrotnemu polubieniu tego samego artykułu przez
        # tego samego użytkownika (walidacja na poziomie bazy danych)
        unique_together = ("user", "article")

    def __str__(self):
        return f"{self.user} lubi {self.article}"


class Notification(models.Model):
    """
    Powiadomienie tworzone automatycznie (przez sygnał post_save) przy
    każdym nowym zgłoszeniu artykułu przez użytkownika - widoczne dla
    administratorów w panelu Django Admin.
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Powiadomienie"
        verbose_name_plural = "Powiadomienia"
        ordering = ["-created_at"]

    def __str__(self):
        return self.message 
    
class UserProfile(models.Model):
    """
    Rozszerzenie standardowego modelu User o dodatkowe dane profilowe.

    Django's User model jest częścią frameworka i nie powinien być
    modyfikowany bezpośrednio - standardową praktyką jest dodanie
    osobnego modelu w relacji OneToOne, powiązanego z User.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Użytkownik",
    )
    bio = models.TextField(
        blank=True,
        verbose_name="O mnie",
        help_text="Krótki opis użytkownika, widoczny przy zgłaszanych artykułach.",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Avatar",
    )

    class Meta:
        verbose_name = "Profil użytkownika"
        verbose_name_plural = "Profile użytkowników"

    def __str__(self):
        return f"Profil {self.user.username}"
