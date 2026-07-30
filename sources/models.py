from django.db import models


class Source(models.Model):
    """
    Zewnętrzne źródło RSS, z którego cyklicznie pobierane są artykuły
    (np. konkretny serwis informacyjny).
    """
    name = models.CharField(max_length=200, verbose_name="Nazwa źródła")
    rss_url = models.URLField(unique=True, verbose_name="Adres kanału RSS")
    is_active = models.BooleanField(default=True, verbose_name="Aktywne")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Źródło RSS"
        verbose_name_plural = "Źródła RSS"
        ordering = ["name"]

    def __str__(self):
        return self.name 