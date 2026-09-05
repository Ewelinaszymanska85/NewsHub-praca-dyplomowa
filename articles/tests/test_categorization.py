import pytest
from unittest.mock import Mock, patch

from articles.categorization import categorize_article_fallback, categorize_article_by_keywords, categorize_article, categorize_article_with_ai
from articles.models import Category


@pytest.mark.django_db
def test_categorize_article_fallback_returns_existing_category():
    category = Category.objects.create(name="Technologia")

    result = categorize_article_fallback(
        title="Nowy model AI",
        content="Artykuł o sztucznej inteligencji.",
    )

    assert result == category


@pytest.mark.django_db
def test_categorize_article_fallback_returns_none_when_no_categories_exist():
    result = categorize_article_fallback(
        title="Artykuł bez kategorii",
        content="Brak dostępnych kategorii w bazie.",
    )

    assert result is None


@pytest.mark.django_db
def test_keyword_categorization_assigns_technology():
    technology = Category.objects.create(name="Technologia")
    Category.objects.create(name="Sport")
    Category.objects.create(name="Nauka")

    result = categorize_article_by_keywords(
        title="Python i sztuczna inteligencja",
        content="Nowe narzędzia AI wspierają programowanie.",
    )

    assert result == technology


@pytest.mark.django_db
def test_keyword_categorization_assigns_science():
    science = Category.objects.create(name="Nauka")
    Category.objects.create(name="Technologia")
    Category.objects.create(name="Sport")

    result = categorize_article_by_keywords(
        title="NASA ogłasza nowe odkrycie",
        content="Naukowcy badają kolejne zjawiska w kosmosie.",
    )

    assert result == science


@pytest.mark.django_db
def test_keyword_categorization_uses_fallback_when_no_keyword_matches():
    category = Category.objects.create(name="Inne")

    result = categorize_article_by_keywords(
        title="Zupełnie neutralny tytuł",
        content="Tekst bez słów pasujących do zdefiniowanych kategorii.",
    )

    assert result == category


@pytest.mark.django_db
def test_categorize_article_uses_local_logic_when_ai_is_unavailable():
    technology = Category.objects.create(name="Technologia")
    Category.objects.create(name="Sport")

    result = categorize_article(
        title="Python i sztuczna inteligencja",
        content="Nowe narzędzia AI pomagają w programowaniu.",
        use_ai=True,
    )

    assert result == technology


@pytest.mark.django_db
@patch("articles.categorization.requests.post")
def test_ai_categorization_returns_category_selected_by_model(mock_post):
    technology = Category.objects.create(name="Technologia")
    Category.objects.create(name="Sport")
    Category.objects.create(name="Nauka")

    mock_response = Mock()
    mock_response.json.return_value = {
        "response": "Technologia"
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = categorize_article_with_ai(
        title="Nowy model sztucznej inteligencji",
        content="Rozwój narzędzi AI przyspiesza.",
    )

    assert result == technology
    mock_post.assert_called_once()
