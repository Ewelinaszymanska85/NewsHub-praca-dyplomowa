from django.db import IntegrityError
from django.test import TestCase
from .models import Source


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
