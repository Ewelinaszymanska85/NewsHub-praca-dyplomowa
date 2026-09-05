from django.db import IntegrityError
from django.test import TestCase
from unittest.mock import patch
from types import SimpleNamespace

from articles.models import Article

from .models import Source
from .tasks import (
    determine_article_status,
    can_fetch_source,
    extract_published_at,
    fetch_feed,
)


class SourceModelTests(TestCase):
    """
    Testy modelu Source (źródło RSS).
    """

    def test_source_creation(self):
        source = Source.objects.create(
            name="BBC News",
            rss_url="https://feeds.bbci.co.uk/news/rss.xml",
        )

        self.assertEqual(source.name, "BBC News")
        self.assertEqual(
            source.rss_url,
            "https://feeds.bbci.co.uk/news/rss.xml",
        )

    def test_source_is_active_by_default(self):
        source = Source.objects.create(
            name="NASA News",
            rss_url="https://www.nasa.gov/feed/",
        )

        self.assertTrue(source.is_active)

    def test_source_string_representation(self):
        source = Source.objects.create(
            name="Testowe źródło",
            rss_url="https://example.com/rss",
        )

        self.assertEqual(str(source), "Testowe źródło")

    def test_source_rss_url_must_be_unique(self):
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
        Source.objects.create(
            name="Zebra News",
            rss_url="https://z.com/rss",
        )
        Source.objects.create(
            name="Alpha News",
            rss_url="https://a.com/rss",
        )

        names = list(
            Source.objects.values_list("name", flat=True)
        )

        self.assertEqual(
            names,
            ["Alpha News", "Zebra News"],
        )


class SourceBusinessLogicTests(TestCase):
    """
    Testy własnej logiki biznesowej źródeł RSS.
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

    def test_active_trusted_source_can_be_fetched(self):
        source = Source(
            name="Trusted News",
            rss_url="https://example.com/trusted",
            is_active=True,
            trust_level="TRUSTED",
        )

        self.assertTrue(can_fetch_source(source))

    def test_active_normal_source_can_be_fetched(self):
        source = Source(
            name="Normal News",
            rss_url="https://example.com/normal",
            is_active=True,
            trust_level="NORMAL",
        )

        self.assertTrue(can_fetch_source(source))

    def test_blocked_source_cannot_be_fetched(self):
        source = Source(
            name="Blocked News",
            rss_url="https://example.com/blocked",
            is_active=True,
            trust_level="BLOCKED",
        )

        self.assertFalse(can_fetch_source(source))

    def test_inactive_source_cannot_be_fetched(self):
        source = Source(
            name="Inactive News",
            rss_url="https://example.com/inactive",
            is_active=False,
            trust_level="TRUSTED",
        )

        self.assertFalse(can_fetch_source(source))

    def test_blocked_source_does_not_create_articles(self):
        source = Source.objects.create(
            name="Blocked RSS",
            rss_url="https://example.com/blocked-feed",
            is_active=True,
            trust_level="BLOCKED",
        )

        result = fetch_feed(source.id)

        self.assertEqual(
            Article.objects.count(),
            0,
        )

        self.assertEqual(
            result,
            "Source 'Blocked RSS' is inactive or blocked",
        )

    @patch("sources.tasks.feedparser.parse")
    def test_trusted_source_creates_approved_article(
        self,
        mock_parse,
    ):
        source = Source.objects.create(
            name="Trusted RSS",
            rss_url="https://example.com/trusted-feed",
            is_active=True,
            trust_level="TRUSTED",
        )

        mock_parse.return_value.entries = [
            SimpleNamespace(
                title="Test article",
                summary="Test content",
                link="https://example.com/article-1",
            )
        ]

        fetch_feed(source.id)

        article = Article.objects.get(
            source_url="https://example.com/article-1"
        )

        self.assertEqual(
            article.status,
            "APPROVED",
        )

    @patch("sources.tasks.feedparser.parse")
    def test_normal_source_creates_pending_article(
        self,
        mock_parse,
    ):
        source = Source.objects.create(
            name="Normal RSS",
            rss_url="https://example.com/normal-feed",
            is_active=True,
            trust_level="NORMAL",
        )

        mock_parse.return_value.entries = [
            SimpleNamespace(
                title="Test article",
                summary="Test content",
                link="https://example.com/article-2",
            )
        ]

        fetch_feed(source.id)

        article = Article.objects.get(
            source_url="https://example.com/article-2"
        )

        self.assertEqual(
            article.status,
            "PENDING",
        )

    def test_extract_published_at_uses_published_field(self):
        entry = SimpleNamespace(
            published="2026-09-05T12:00:00Z"
        )

        result = extract_published_at(entry)

        self.assertEqual(
            result.isoformat(),
            "2026-09-05T12:00:00+00:00",
        )

    def test_extract_published_at_uses_updated_as_fallback(self):
        entry = SimpleNamespace(
            updated="2026-09-05T14:30:00Z"
        )

        result = extract_published_at(entry)

        self.assertEqual(
            result.isoformat(),
            "2026-09-05T14:30:00+00:00",
        )


    @patch("sources.tasks.feedparser.parse")
    def test_fetch_feed_saves_published_date_from_rss(self, mock_parse):
        source = Source.objects.create(
            name="RSS z datą",
            rss_url="https://example.com/feed-with-date",
            is_active=True,
            trust_level="TRUSTED",
        )

        mock_parse.return_value.entries = [
            SimpleNamespace(
                title="Artykuł z datą",
                summary="Treść artykułu",
                link="https://example.com/article-with-date",
                published="2026-09-05T10:00:00Z",
            )
        ]

        fetch_feed(source.id)

        article = Article.objects.get(
            source_url="https://example.com/article-with-date"
        )

        self.assertEqual(
            article.published_at.isoformat(),
            "2026-09-05T10:00:00+00:00",
        )
