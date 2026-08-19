import strawberry
import strawberry_django

from articles.models import Article, Category, Tag
from sources.models import Source


@strawberry_django.type(Category)
class CategoryType:
    id: strawberry.auto
    name: strawberry.auto


@strawberry_django.type(Tag)
class TagType:
    id: strawberry.auto
    name: strawberry.auto


@strawberry_django.type(Source)
class SourceType:
    id: strawberry.auto
    name: strawberry.auto
    rss_url: strawberry.auto
    is_active: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(Article)
class ArticleType:
    id: strawberry.auto
    title: strawberry.auto
    content: strawberry.auto
    source_url: strawberry.auto
    published_at: strawberry.auto
    status: strawberry.auto

    category: CategoryType | None
    tags: list[TagType]
    source: SourceType | None


@strawberry.type
class Query:
    articles: list[ArticleType] = strawberry_django.field()
    categories: list[CategoryType] = strawberry_django.field()
    tags: list[TagType] = strawberry_django.field()
    sources: list[SourceType] = strawberry_django.field()


schema = strawberry.Schema(query=Query)