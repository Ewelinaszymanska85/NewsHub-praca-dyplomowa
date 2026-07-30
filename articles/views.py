from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as http_status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Article, Category, Tag, Like
from .serializers import ArticleSerializer, CategorySerializer, TagSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint do przeglądania i zarządzania artykułami.

    - Odczyt (GET) dostępny dla wszystkich, tylko artykuły APPROVED.
    - Tworzenie (POST) wymaga zalogowania - artykuł automatycznie
      otrzymuje status PENDING i jest przypisywany do zalogowanego
      użytkownika jako submitted_by.
    """
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """
        GET (list/retrieve) - dostępne dla wszystkich (gości).
        POST/PUT/PATCH/DELETE - wymaga zalogowania.
        """
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Article.objects.filter(status="APPROVED")

    @extend_schema(
        summary="Lista zatwierdzonych artykułów",
        description=(
            "Zwraca listę artykułów o statusie APPROVED (zatwierdzonych "
            "przez administratora lub pobranych automatycznie z RSS). "
            "Odpowiedź jest buforowana w cache na 5 minut."
        ),
        tags=["Artykuły"],
    )
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Zgłoś nowy artykuł",
        description=(
            "Wymaga zalogowania. Artykuł automatycznie otrzymuje status "
            "PENDING i oczekuje na zatwierdzenie przez administratora. "
            "Sygnał post_save automatycznie tworzy powiadomienie dla adminów."
        ),
        tags=["Artykuły"],
        responses={
            201: ArticleSerializer,
            401: OpenApiResponse(description="Wymagane zalogowanie"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Przy tworzeniu artykułu przez API, automatycznie:
        - ustawiamy status na PENDING (wymaga moderacji)
        - przypisujemy zalogowanego użytkownika jako submitted_by
        """
        serializer.save(status="PENDING", submitted_by=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@extend_schema(
    summary="Polub lub odlub artykuł",
    description=(
        "Przełącza polubienie artykułu przez zalogowanego użytkownika. "
        "Pierwsze wywołanie tworzy polubienie (201), drugie je usuwa (200)."
    ),
    tags=["Polubienia"],
    responses={
        200: OpenApiResponse(description="Polubienie usunięte (odlubiono)"),
        201: OpenApiResponse(description="Artykuł polubiony"),
        404: OpenApiResponse(description="Artykuł nie istnieje"),
    },
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_article(request, article_id):
    """
    Przełącza polubienie artykułu przez zalogowanego użytkownika:
    - jeśli użytkownik jeszcze nie polubił artykułu, tworzy polubienie
    - jeśli już polubił, usuwa polubienie (odlubienie)

    Dzięki unique_together w modelu Like, próba dodania duplikatu
    polubienia jest niemożliwa na poziomie bazy danych.
    """
    try:
        article = Article.objects.get(id=article_id, status="APPROVED")
    except Article.DoesNotExist:
        return Response({"error": "Artykuł nie istnieje"}, status=http_status.HTTP_404_NOT_FOUND)

    like, created = Like.objects.get_or_create(user=request.user, article=article)

    if not created:
        like.delete()
        return Response({"liked": False, "message": "Polubienie usunięte"})

    return Response({"liked": True, "message": "Artykuł polubiony"}, status=http_status.HTTP_201_CREATED)
