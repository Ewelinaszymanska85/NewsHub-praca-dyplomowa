import random
import requests

from .models import Category


def categorize_article_fallback(title, content):
    """
    Awaryjna kategoryzacja artykułu bez użycia modelu AI.
    Wybiera jedną z kategorii dostępnych w bazie danych.
    """
    categories = list(Category.objects.all())

    if not categories:
        return None

    return random.choice(categories)


def categorize_article_by_keywords(title, content):
    """
    Próbuje dopasować kategorię na podstawie słów kluczowych
    znajdujących się w tytule i treści artykułu.
    """
    text = f"{title} {content}".lower()

    category_keywords = {
        "Technologia": [
            "python",
            "programowanie",
            "sztuczna inteligencja",
            "ai",
            "technologia",
            "software",
        ],
        "Sport": [
            "mecz",
            "piłka",
            "piłkarz",
            "sport",
            "liga",
            "turniej",
        ],
        "Nauka": [
            "nauka",
            "badanie",
            "naukowcy",
            "kosmos",
            "nasa",
            "odkrycie",
        ],
    }

    for category_name, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            category = Category.objects.filter(
                name__iexact=category_name
            ).first()

            if category:
                return category

    return categorize_article_fallback(title, content)


def categorize_article_with_ai(title, content):
    """
    Kategoryzuje artykuł przy użyciu lokalnego modelu AI przez Ollama API.
    Model wybiera kategorię wyłącznie spośród kategorii istniejących
    w bazie danych.
    """
    categories = list(
        Category.objects.values_list("name", flat=True)
    )

    if not categories:
        return None

    prompt = (
        "Wybierz dokładnie jedną kategorię dla poniższego artykułu. "
        f"Dozwolone kategorie: {', '.join(categories)}. "
        "Zwróć wyłącznie nazwę kategorii, bez dodatkowego tekstu.\n\n"
        f"Tytuł: {title}\n"
        f"Treść: {content}"
    )

    response = requests.post(
        "http://host.docker.internal:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
        },
        timeout=10,
    )
    response.raise_for_status()

    category_name = response.json()["response"].strip()

    category = Category.objects.filter(
        name__iexact=category_name
    ).first()

    if category is None:
        raise ValueError(
            f"Model AI zwrócił nieznaną kategorię: {category_name}"
        )

    return category


def categorize_article(title, content, use_ai=False):
    """
    Główna funkcja kategoryzacji artykułu.

    Jeśli use_ai=True, próbuje użyć kategoryzacji AI.
    W przypadku niedostępności AI przechodzi do lokalnej
    kategoryzacji na podstawie słów kluczowych.
    """
    if use_ai:
        try:
            return categorize_article_with_ai(title, content)
        except Exception:
            pass

    return categorize_article_by_keywords(title, content)
