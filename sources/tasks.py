import feedparser
from celery import shared_task
from django.utils.dateparse import parse_datetime
from articles.models import Article
from .models import Source


def determine_article_status(source):
    """
    Ustala status artykułu na podstawie poziomu zaufania źródła.
    """
    if source.trust_level == "TRUSTED":
        return "APPROVED"

    if source.trust_level == "BLOCKED":
        return "REJECTED"

    return "PENDING"

def can_fetch_source(source):
    """
    Sprawdza, czy źródło może być przetwarzane przez agregator RSS.
    """
    return source.is_active and source.trust_level != "BLOCKED"


@shared_task
def fetch_feed(source_id):
    """
    Pobiera i parsuje pojedyncze źródło RSS, tworząc nowe artykuły
    dla wpisów, których jeszcze nie ma w bazie (idempotencja -
    sprawdzenie unikalności po source_url zapobiega duplikatom przy
    wielokrotnym uruchomieniu tego samego zadania).
    """
    try:
        source = Source.objects.get(id=source_id)
    except Source.DoesNotExist:
        return f"Source {source_id} not found"

    if not can_fetch_source(source):
        return f"Source '{source.name}' is inactive or blocked"

    feed = feedparser.parse(source.rss_url)
    created_count = 0

    for entry in feed.entries:
        link = getattr(entry, "link", None)
        if not link:
            continue

        # Idempotencja: pomijamy wpis, jeśli artykuł o tym samym
        # linku źródłowym już istnieje w bazie
        if Article.objects.filter(source_url=link).exists():
            continue

        Article.objects.create(
            title=getattr(entry, "title", "Bez tytułu"),
            content=getattr(entry, "summary", ""),
            source_url=link,
            source=source,
            status=determine_article_status(source),  
        )
        created_count += 1

    return f"Source '{source.name}': created {created_count} new articles"


@shared_task
def fetch_all_active_feeds():
    """
    Zadanie cykliczne (wywoływane przez Celery Beat) - zleca pobranie
    każdego aktywnego źródła RSS jako osobne zadanie.
    """
    active_source_ids = Source.objects.filter(
        is_active=True
    ).exclude(
        trust_level="BLOCKED"
    ).values_list("id", flat=True)

    for source_id in active_source_ids:
        fetch_feed.delay(source_id)
    return f"Dispatched fetch for {len(active_source_ids)} sources" 
