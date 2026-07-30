from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article, Notification


@receiver(post_save, sender=Article)
def create_notification_for_submitted_article(sender, instance, created, **kwargs):
    """
    Gdy nowy artykuł zostaje zapisany ze statusem PENDING (czyli
    zgłoszony przez użytkownika, a nie pobrany z RSS jako APPROVED),
    automatycznie tworzymy powiadomienie widoczne dla administratorów.

    Warunek `created` gwarantuje, że powiadomienie powstaje tylko
    przy PIERWSZYM zapisie artykułu (nie przy każdej późniejszej
    aktualizacji, np. zmianie statusu przez admina).
    """
    if created and instance.status == "PENDING":
        Notification.objects.create(
            article=instance,
            message=f"Nowe zgłoszenie artykułu: '{instance.title}' oczekuje na moderację.",
        ) 