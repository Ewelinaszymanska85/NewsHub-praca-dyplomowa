from django.contrib import admin
from .models import Category, Tag, Article, Like, Notification, UserProfile


@admin.action(description="Zatwierdź zaznaczone artykuły")
def approve_articles(modeladmin, request, queryset):
    updated = queryset.update(status="APPROVED")
    modeladmin.message_user(request, f"Zatwierdzono {updated} artykułów.")


@admin.action(description="Odrzuć zaznaczone artykuły")
def reject_articles(modeladmin, request, queryset):
    updated = queryset.update(status="REJECTED")
    modeladmin.message_user(request, f"Odrzucono {updated} artykułów.")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "category", "source", "submitted_by", "published_at"]
    list_filter = ["status", "category", "source"]
    search_fields = ["title", "content"]
    actions = [approve_articles, reject_articles]


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Notification) 
admin.site.register(UserProfile) 