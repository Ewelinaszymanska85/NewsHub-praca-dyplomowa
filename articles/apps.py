from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

    def ready(self):
        """
        Metoda ready() jest wywoływana automatycznie przy starcie
        Django - to standardowe miejsce na import sygnałów, żeby
        zostały zarejestrowane i faktycznie zadziałały.
        """
        import articles.signals 
        