from django.test import TestCase
from ..models import Article, Category, Tag
from ..serializers import ArticleSerializer
from datetime import timedelta
from django.utils import timezone


class ArticleSerializerTests(TestCase):
    """
    Testy jednostkowe ArticleSerializer, w izolacji od widoku/endpointu -
    sprawdzają bezpośrednio, jak serializer tłumaczy dane między
    modelem Article a reprezentacją JSON.
    """

    def setUp(self):
        self.category = Category.objects.create(name="Technologia")
        self.tag = Tag.objects.create(name="Python")
        self.article = Article.objects.create(
            title="Artykuł testowy",
            content="Treść testowa",
            category=self.category,
            status="APPROVED",
        )
        self.article.tags.add(self.tag)

    def test_serializer_contains_expected_fields(self):
        """
        Zserializowany artykuł powinien zawierać wszystkie zadeklarowane
        pola z Meta.fields.
        """
        serializer = ArticleSerializer(instance=self.article)
        data = serializer.data

        expected_fields = {
            "id", "title", "content", "source_url", "published_at",
            "status", "category", "category_detail", "tags",
            "tags_detail", "source", "submitted_by",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_category_detail_is_nested_serialized_object(self):
        """
        category_detail powinno zwracać pełny, zagnieżdżony obiekt
        kategorii (id + name), a nie samo ID.
        """
        serializer = ArticleSerializer(instance=self.article)
        data = serializer.data

        self.assertEqual(data["category_detail"]["name"], "Technologia")
        self.assertEqual(data["category"], self.category.id)

    def test_tags_detail_is_nested_list_of_serialized_tags(self):
        """
        tags_detail powinno zwracać listę pełnych obiektów tagów,
        nie tylko listę ID.
        """
        serializer = ArticleSerializer(instance=self.article)
        data = serializer.data

        self.assertEqual(len(data["tags_detail"]), 1)
        self.assertEqual(data["tags_detail"][0]["name"], "Python")

    def test_read_only_fields_are_ignored_on_input(self):
        """
        Pola oznaczone jako read_only (status, source, submitted_by)
        nie powinny dać się ustawić przez dane wejściowe do serializera -
        nawet jeśli klient je poda, powinny zostać zignorowane.
        """
        serializer = ArticleSerializer(data={
            "title": "Próba wymuszenia zatwierdzenia",
            "content": "Treść",
            "status": "APPROVED",  # próba obejścia moderacji
            "category": self.category.id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        # status NIE powinien znaleźć się w validated_data - jest read_only
        self.assertNotIn("status", serializer.validated_data)

    def test_serializer_requires_title_and_content(self):
        """
        Serializer powinien odrzucić dane bez wymaganych pól title/content,
        niezależnie od tego, że test_validation.py sprawdza to już przez
        pełny endpoint - tutaj sprawdzamy to na poziomie samego serializera.
        """
        serializer = ArticleSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
        self.assertIn("content", serializer.errors) 
        
    def test_serializer_rejects_duplicate_source_url(self):
        Article.objects.create(
            title="Pierwszy artykuł",
            content="Treść pierwszego artykułu",
            source_url="https://example.com/article-1",
        )

        serializer = ArticleSerializer(data={
            "title": "Drugi artykuł",
            "content": "Treść drugiego artykułu",
            "source_url": "https://example.com/article-1",
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("source_url", serializer.errors)
        self.assertEqual(
            str(serializer.errors["source_url"][0]),
            "Artykuł z tym adresem URL już istnieje.",
        )
        
    def test_serializer_rejects_article_older_than_7_days(self):
            old_date = timezone.now() - timedelta(days=8)

            serializer = ArticleSerializer(data={
            "title": "Stary artykuł",
            "content": "Treść starego artykułu",
            "source_url": "https://example.com/old-article",
            "published_at": old_date,
        })

            self.assertFalse(serializer.is_valid())
            self.assertIn("published_at", serializer.errors)
            self.assertEqual(
            str(serializer.errors["published_at"][0]),
            "Artykuł nie może być starszy niż 7 dni.",
        )

    def test_serializer_accepts_article_newer_than_7_days(self):
        recent_date = timezone.now() - timedelta(days=2)

        serializer = ArticleSerializer(data={
            "title": "Nowy artykuł",
            "content": "Treść nowego artykułu",
            "source_url": "https://example.com/recent-article",
            "published_at": recent_date,
            "category": self.category.id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_category_or_tag(self):
        serializer = ArticleSerializer(data={
            "title": "Artykuł bez kategorii i tagów",
            "content": "Treść artykułu",
            "source_url": "https://example.com/no-category-no-tags",
            "published_at": timezone.now(),
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]),
            "Artykuł musi mieć kategorię lub co najmniej jeden tag.",
        )

    def test_serializer_accepts_article_with_category_without_tags(self):
        serializer = ArticleSerializer(data={
            "title": "Artykuł z kategorią",
            "content": "Treść artykułu",
            "source_url": "https://example.com/article-with-category",
            "published_at": timezone.now(),
            "category": self.category.id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_accepts_article_with_tag_without_category(self):
        serializer = ArticleSerializer(data={
            "title": "Artykuł z tagiem",
            "content": "Treść artykułu",
            "source_url": "https://example.com/article-with-tag",
            "published_at": timezone.now(),
            "tags": [self.tag.id],
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
