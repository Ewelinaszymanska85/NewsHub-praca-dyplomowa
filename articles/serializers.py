from rest_framework import serializers
from .models import Article, Category, Tag
from datetime import timedelta
from django.utils import timezone


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ArticleSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category", read_only=True)
    tags_detail = TagSerializer(source="tags", many=True, read_only=True)
    
    def validate_source_url(self, value):
        if not value:
            return None

        articles = Article.objects.filter(source_url=value)

        if self.instance:
            articles = articles.exclude(pk=self.instance.pk)

        if articles.exists():
            raise serializers.ValidationError(
                "Artykuł z tym adresem URL już istnieje."
            )

        return value
    
    def validate_published_at(self, value):
        if not value:
            return value

        if value < timezone.now() - timedelta(days=7):
            raise serializers.ValidationError(
                "Artykuł nie może być starszy niż 7 dni."
            )

        return value

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "source_url",
            "published_at",
            "status",
            "category",
            "category_detail",
            "tags",
            "tags_detail",
            "source",
            "submitted_by",
        ]
        read_only_fields = ["status", "source", "submitted_by"]
        
        extra_kwargs = {
            "source_url": {
                "validators": [],
            },
        }
        
from .models import Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "article", "created_at"]
        read_only_fields = ["created_at"]    
