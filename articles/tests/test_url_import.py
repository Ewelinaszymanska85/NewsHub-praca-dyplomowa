from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from articles.models import Category


@pytest.mark.django_db
@patch("articles.views.fetch_article_data")
def test_authenticated_user_can_fetch_article_data_from_url(mock_fetch):
    user = User.objects.create_user(
        username="scraper_user",
        password="TestPass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    mock_fetch.return_value = {
        "title": "Automatycznie pobrany artykuł",
        "published_at": "2026-09-04T15:00:00Z",
        "content": "Opis pobrany automatycznie ze strony.",
    }

    response = client.post(
        "/api/articles/fetch-from-url/",
        {
            "url": "https://www.bbc.com/news/test",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["title"] == "Automatycznie pobrany artykuł"
    assert response.data["published_at"] == "2026-09-04T15:00:00Z"
    assert response.data["content"] == "Opis pobrany automatycznie ze strony."
    assert response.data["source_url"] == "https://www.bbc.com/news/test"

    mock_fetch.assert_called_once_with(
        "https://www.bbc.com/news/test"
    )

@pytest.mark.django_db
def test_anonymous_user_cannot_fetch_article_from_url():
    client = APIClient()

    response = client.post(
        "/api/articles/fetch-from-url/",
        {
            "url": "https://www.bbc.com/news/test",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
@patch("articles.views.fetch_article_data")
def test_unsupported_domain_returns_400(mock_fetch):
    user = User.objects.create_user(
        username="unsupported_user",
        password="TestPass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    from articles.scrapers import NoScraperMatched

    mock_fetch.side_effect = NoScraperMatched(
        "Brak scrapera dla domeny: example.com"
    )

    response = client.post(
        "/api/articles/fetch-from-url/",
        {
            "url": "https://example.com/news/test",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "Brak scrapera" in response.data["error"]


@pytest.mark.django_db
@patch("articles.views.fetch_article_data")
def test_scraping_error_returns_422(mock_fetch):
    user = User.objects.create_user(
        username="scraping_error_user",
        password="TestPass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    from articles.scrapers import ScrapingError

    mock_fetch.side_effect = ScrapingError(
        "Nie znaleziono tytułu artykułu BBC."
    )

    response = client.post(
        "/api/articles/fetch-from-url/",
        {
            "url": "https://www.bbc.com/news/test",
        },
        format="json",
    )

    assert response.status_code == 422
    assert "Nie znaleziono tytułu" in response.data["error"]


@pytest.mark.django_db
@patch("articles.views.categorize_article")
@patch("articles.views.fetch_article_data")
def test_url_import_returns_suggested_category(mock_fetch, mock_categorize):
    user = User.objects.create_user(
        username="category_user",
        password="TestPass123!",
    )
    category = Category.objects.create(name="Technologia")

    client = APIClient()
    client.force_authenticate(user=user)

    mock_fetch.return_value = {
        "title": "Nowy model AI",
        "content": "Artykuł o sztucznej inteligencji.",
        "published_at": "2026-09-05T12:00:00Z",
    }
    mock_categorize.return_value = category

    response = client.post(
        "/api/articles/fetch-from-url/",
        {"url": "https://www.bbc.com/news/test"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["suggested_category"]["id"] == category.id
    assert response.data["suggested_category"]["name"] == "Technologia"

    mock_categorize.assert_called_once_with(
        title="Nowy model AI",
        content="Artykuł o sztucznej inteligencji.",
        use_ai=True,
    )
