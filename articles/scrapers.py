from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


class NoScraperMatched(Exception):
    """Brak obsługiwanego scrapera dla podanej domeny."""


class ScrapingError(Exception):
    """Nie udało się znaleźć wymaganych danych artykułu."""


def scrap_bbc_news(html):
    """
    Pobiera podstawowe dane artykułu BBC z kodu HTML.
    """
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1")
    published_at = soup.find("time")
    description = soup.find("meta", attrs={"name": "description"})

    if title is None:
        raise ScrapingError("Nie znaleziono tytułu artykułu BBC.")

    return {
        "title": title.get_text(strip=True),
        "published_at": (
            published_at.get("datetime")
            if published_at is not None
            else None
        ),
        "content": (
            description.get("content", "").strip()
            if description is not None
            else ""
        ),
    }


def scrap_nasa_news(html):
    """
    Pobiera podstawowe dane artykułu NASA z kodu HTML.
    """
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1")
    published_at = soup.find("time")
    description = soup.find("meta", attrs={"name": "description"})

    if title is None:
        raise ScrapingError("Nie znaleziono tytułu artykułu NASA.")

    return {
        "title": title.get_text(strip=True),
        "published_at": (
            published_at.get("datetime")
            if published_at is not None
            else None
        ),
        "content": (
            description.get("content", "").strip()
            if description is not None
            else ""
        ),
    }


def match_scraper(url):
    """
    Rozpoznaje domenę URL i zwraca funkcję odpowiedniego scrapera.
    """
    hostname = urlparse(url).hostname

    match hostname:
        case "www.bbc.com" | "bbc.com" | "www.bbc.co.uk" | "bbc.co.uk":
            return scrap_bbc_news
        case "www.nasa.gov" | "nasa.gov":
            return scrap_nasa_news
        case _:
            raise NoScraperMatched(
                f"Brak scrapera dla domeny: {hostname}"
            )
            
def fetch_article_data(url):
    """
    Pobiera stronę artykułu i uruchamia scraper dopasowany do domeny.
    """
    scraper = match_scraper(url)

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return scraper(response.text)          
