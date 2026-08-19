from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from articles.views import ArticleViewSet, CategoryViewSet, TagViewSet, like_article  
from sources.views import SourceViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.urls import path, include
from strawberry.django.views import GraphQLView
from graphql_api.schema import schema

router = routers.DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article') 
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'source', SourceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", GraphQLView.as_view(schema=schema)),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/articles/<int:article_id>/like/', like_article, name='article-like'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
 ] 