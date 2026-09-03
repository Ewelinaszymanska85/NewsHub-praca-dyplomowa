from django.db import models


class Source(models.Model):
    """
    Zewnętrzne źródło RSS, z którego cyklicznie pobierane są artykuły
    (np. konkretny serwis informacyjny).
    """

    TRUST_LEVEL_CHOICES = [
        ("TRUSTED", "Zaufane"),
        ("NORMAL", "Standardowe"),
        ("BLOCKED", "Zablokowane"),
    ]

    name = models.CharField(max_length=200, verbose_name="Nazwa źródła")
    rss_url = models.URLField(unique=True, verbose_name="Adres kanału RSS")
    is_active = models.BooleanField(default=True, verbose_name="Aktywne")

    trust_level = models.CharField(
        max_length=20,
        choices=TRUST_LEVEL_CHOICES,
        default="NORMAL",
        verbose_name="Poziom zaufania",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Źródło RSS"
        verbose_name_plural = "Źródła RSS"
        ordering = ["name"]

    def __str__(self):
        return self.name
