from django.db import IntegrityError
from django.test import TestCase
from .models import Source
from .tasks import determine_article_status


class SourceModelTests(TestCase):
    """
    Testy modelu Source (źródło RSS).
    """

    def test_source_creation(self):
        """Sprawdza, czy źródło RSS tworzy się poprawnie z podanymi danymi."""
        source = Source.objects.create(
            name="BBC News",
            rss_url="https://feeds.bbci.co.uk/news/rss.xml",
        )
        self.assertEqual(source.name, "BBC News")
        self.assertEqual(source.rss_url, "https://feeds.bbci.co.uk/news/rss.xml")

    def test_source_is_active_by_default(self):
        """Nowo utworzone źródło powinno być domyślnie aktywne."""
        source = Source.objects.create(
            name="NASA News",
            rss_url="https://www.nasa.gov/feed/",
        )
        self.assertTrue(source.is_active)

    def test_source_string_representation(self):
        """__str__ powinien zwracać nazwę źródła."""
        source = Source.objects.create(
            name="Testowe źródło",
            rss_url="https://example.com/rss",
        )
        self.assertEqual(str(source), "Testowe źródło")

    def test_source_rss_url_must_be_unique(self):
        """
        Dwa źródła nie mogą mieć tego samego adresu RSS - baza danych
        powinna wymusić ten warunek (unique=True w modelu).
        """
        Source.objects.create(
            name="Pierwsze źródło",
            rss_url="https://duplicate.com/rss",
        )
        with self.assertRaises(IntegrityError):
            Source.objects.create(
                name="Drugie źródło",
                rss_url="https://duplicate.com/rss",
            )

    def test_sources_ordered_by_name(self):
        """Źródła powinny być domyślnie sortowane alfabetycznie po nazwie."""
        Source.objects.create(name="Zebra News", rss_url="https://z.com/rss")
        Source.objects.create(name="Alpha News", rss_url="https://a.com/rss")

        names = list(Source.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha News", "Zebra News"])
        
        
class SourceBusinessLogicTests(TestCase):
    """
    Testy własnej logiki biznesowej dla poziomu zaufania źródła.
    """

    def test_trusted_source_returns_approved(self):
        source = Source(
            name="BBC News",
            rss_url="https://example.com/trusted-rss",
            trust_level="TRUSTED",
        )

        status = determine_article_status(source)

        self.assertEqual(status, "APPROVED")

    def test_normal_source_returns_pending(self):
        source = Source(
            name="Standard News",
            rss_url="https://example.com/normal-rss",
            trust_level="NORMAL",
        )

        status = determine_article_status(source)

        self.assertEqual(status, "PENDING")

    def test_blocked_source_returns_rejected(self):
        source = Source(
            name="Blocked News",
            rss_url="https://example.com/blocked-rss",
            trust_level="BLOCKED",
        )

        status = determine_article_status(source)

        self.assertEqual(status, "REJECTED")

    def test_default_source_returns_pending(self):
        source = Source(
            name="Default News",
            rss_url="https://example.com/default-rss",
        )

        status = determine_article_status(source)

        self.assertEqual(status, "PENDING")

    def test_unknown_trust_level_returns_pending(self):
        source = Source(
            name="Unknown News",
            rss_url="https://example.com/unknown-rss",
            trust_level="UNKNOWN",
        )

        status = determine_article_status(source)

        self.assertEqual(status, "PENDING")
