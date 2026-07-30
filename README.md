# NewsHub — Agregator wiadomości

Praca dyplomowa — kurs Python Web Development (Django).

Agregator wiadomości pobierający artykuły z co najmniej dwóch zewnętrznych
źródeł RSS w sposób cykliczny i automatyczny. Zalogowani użytkownicy mogą
dodatkowo zgłaszać własne artykuły do publikacji — każde zgłoszenie wymaga
zatwierdzenia przez administratora, zanim stanie się publicznie widoczne.

## Funkcjonalności

- Automatyczna, cykliczna agregacja artykułów z min. 2 źródeł RSS (Celery Beat + `feedparser`)
- Rejestracja i logowanie z uwierzytelnianiem tokenowym (JWT)
- Zgłaszanie artykułów przez zalogowanych użytkowników z pełnym przepływem moderacji
- Panel administracyjny z akcjami masowymi do zatwierdzania/odrzucania zgłoszeń
- Polubienia artykułów
- Automatyczne powiadomienia (sygnał Django) o nowych zgłoszeniach do moderacji
- Cache list artykułów
- W pełni udokumentowane REST API (Swagger UI / drf-spectacular)
- Testy jednostkowe i integracyjne

## Stos technologiczny

- **Backend:** Django 6.0, Django REST Framework
- **Baza danych:** PostgreSQL 16
- **Broker / cache:** Redis
- **Zadania w tle:** Celery + Celery Beat
- **Uwierzytelnianie:** djangorestframework-simplejwt + Djoser
- **Dokumentacja API:** drf-spectacular
- **Konteneryzacja:** Docker + Docker Compose

## Model domenowy

| Model | Opis |
|---|---|
| `Source` | Źródło RSS (nazwa, URL kanału, aktywność) |
| `Category` | Kategoria tematyczna artykułu (relacja 1:N z artykułem) |
| `Tag` | Tag przypisywany do artykułu (relacja M:N z artykułem) |
| `Article` | Artykuł — pochodzący z RSS albo zgłoszony przez użytkownika |
| `Like` | Polubienie artykułu przez użytkownika (relacja M:N przez tabelę pośrednią) |
| `Notification` | Powiadomienie tworzone automatycznie przez sygnał `post_save` |

## Uruchomienie projektu (Docker)

Wymagania: zainstalowany Docker Desktop.

```bash
# Sklonuj repozytorium
git clone <adres-repo>
cd newshub

# Zbuduj i uruchom wszystkie kontenery
docker compose up -d --build

# Zastosuj migracje
docker exec -it newshub-web-1 python manage.py migrate

# Stwórz konto administratora
docker exec -it newshub-web-1 python manage.py createsuperuser
```

Aplikacja będzie dostępna pod adresem: `http://127.0.0.1:8000/`

## Dostępne adresy

| Adres | Opis |
|---|---|
| `/admin/` | Panel administracyjny Django |
| `/api/articles/` | Lista i zarządzanie artykułami |
| `/api/categories/` | Lista i zarządzanie kategoriami |
| `/api/tags/` | Lista i zarządzanie tagami |
| `/api/sources/` | Lista i zarządzanie źródłami RSS |
| `/api/articles/<id>/like/` | Polubienie / odlubienie artykułu |
| `/api/auth/users/` | Rejestracja użytkownika (Djoser) |
| `/api/auth/jwt/create/` | Logowanie — pobranie tokenu JWT |
| `/api/schema/swagger-ui/` | Interaktywna dokumentacja API (Swagger) |

## Dodawanie źródeł RSS

Źródła RSS dodaje się przez panel administracyjny (`/admin/` → Źródła RSS) lub
przez Django shell:

```python
from sources.models import Source

Source.objects.create(
    name="BBC News",
    rss_url="http://feeds.bbci.co.uk/news/rss.xml",
    is_active=True,
)
```

Celery Beat automatycznie pobiera artykuły z aktywnych źródeł co 30 minut.

## Uruchamianie testów

```bash
docker exec -it newshub-web-1 python manage.py test articles
```

## Struktura projektu

```
newshub/
├── core/              # Konfiguracja projektu (settings, urls, celery)
├── articles/          # Modele Article, Category, Tag, Like, Notification
│   └── tests/         # Testy jednostkowe i integracyjne
├── sources/           # Model Source, zadania Celery pobierające RSS
├── docker-compose.yml # Definicja kontenerów (web, db, redis, celery worker/beat)
├── Dockerfile
└── requirements.txt
```

## Dokumentacja projektowa

Pełna dokumentacja projektowa (grupa docelowa, model domenowy, wymagania
niefunkcjonalne, roadmap) znajduje się w `plan_projektu.md` w głównym
folderze repozytorium.

## Autor

Ewelina Szymańska — praca dyplomowa, kurs Python Web Development. 