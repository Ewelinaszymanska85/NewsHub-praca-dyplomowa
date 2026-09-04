import pytest
from unittest.mock import Mock, patch

from articles.scrapers import (
    NoScraperMatched,
    ScrapingError,
    fetch_article_data,
    match_scraper,
    scrap_bbc_news,
    scrap_nasa_news,
)


@pytest.mark.parametrize(
    "url, expected_scraper",
    [
        ("https://www.bbc.com/news/article", scrap_bbc_news),
        ("https://bbc.com/news/article", scrap_bbc_news),
        ("https://www.nasa.gov/news/article", scrap_nasa_news),
        ("https://nasa.gov/news/article", scrap_nasa_news),
    ],
)
def test_match_scraper_recognizes_supported_domains(url, expected_scraper):
    scraper = match_scraper(url)

    assert scraper is expected_scraper


def test_match_scraper_rejects_unsupported_domain():
    with pytest.raises(NoScraperMatched):
        match_scraper("https://example.com/news/article")
        
def test_bbc_scraper_extracts_article_data_from_html():
    html = """
    <html>
        <head>
            <meta name="description" content="Opis artykułu BBC">
        </head>
        <body>
            <h1>Testowy artykuł BBC</h1>
            <time datetime="2026-09-04T10:00:00Z"></time>
        </body>
    </html>
    """

    data = scrap_bbc_news(html)

    assert data["title"] == "Testowy artykuł BBC"
    assert data["published_at"] == "2026-09-04T10:00:00Z"
    assert data["content"] == "Opis artykułu BBC"

def test_nasa_scraper_extracts_article_data_from_html():
    html = """
    <html>
        <head>
            <meta name="description" content="Opis artykułu NASA">
        </head>
        <body>
            <h1>Testowy artykuł NASA</h1>
            <time datetime="2026-09-04T12:30:00Z"></time>
        </body>
    </html>
    """

    data = scrap_nasa_news(html)

    assert data["title"] == "Testowy artykuł NASA"
    assert data["published_at"] == "2026-09-04T12:30:00Z"
    assert data["content"] == "Opis artykułu NASA"
    
from articles.scrapers import ScrapingError

def test_bbc_scraper_raises_error_when_title_is_missing():
    html = """
    <html>
        <body>
            <p>Brak nagłówka h1</p>
        </body>
    </html>
    """

    with pytest.raises(ScrapingError):
        scrap_bbc_news(html)
        
@patch("articles.scrapers.requests.get")
def test_fetch_article_data_downloads_page_and_uses_matching_scraper(mock_get):
    mock_response = Mock()
    mock_response.text = """
    <html>
        <head>
            <meta name="description" content="Opis z mocka">
        </head>
        <body>
            <h1>Artykuł z mocka</h1>
            <time datetime="2026-09-04T15:00:00Z"></time>
        </body>
    </html>
    """
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    data = fetch_article_data("https://www.bbc.com/news/test")

    assert data["title"] == "Artykuł z mocka"
    assert data["published_at"] == "2026-09-04T15:00:00Z"
    assert data["content"] == "Opis z mocka"

    mock_get.assert_called_once_with(
        "https://www.bbc.com/news/test",
        timeout=10,
    )          
