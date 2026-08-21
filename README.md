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
- GraphQL API umożliwiające elastyczne pobieranie artykułów i powiązanych danych
- Testy jednostkowe i integracyjne (41 testów pokrywających modele, API, autoryzację, moderację, GraphQL i walidację danych) 

## Stos technologiczny

- **Backend:** Django 6.0, Django REST Framework
- **GraphQL API:** Strawberry GraphQL + Strawberry GraphQL Django
- **Baza danych:** PostgreSQL 16
- **Broker / cache:** Redis
- **Zadania w tle:** Celery + Celery Beat
- **Uwierzytelnianie:** djangorestframework-simplejwt + Djoser
- **Dokumentacja API:** drf-spectacular
- **Konteneryzacja:** Docker + Docker Compose
- **Deployment:** Railway
- **Serwer aplikacji:** Gunicorn

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

## Wdrożenie produkcyjne

Aplikacja NewsHub została wdrożona na platformie Railway.

**Publiczny adres aplikacji:**  
https://newshub-praca-dyplomowa-production.up.railway.app

**Swagger UI:**  
https://newshub-praca-dyplomowa-production.up.railway.app/api/schema/swagger-ui/

**GraphQL / GraphiQL:**  
https://newshub-praca-dyplomowa-production.up.railway.app/graphql/

**REST API:**  
https://newshub-praca-dyplomowa-production.up.railway.app/api/articles/

Środowisko produkcyjne składa się z sześciu usług:

- `NewsHub-praca-dyplomowa` — aplikacja Django / REST API / GraphQL
- `Postgres` — produkcyjna baza danych PostgreSQL
- `Redis` — broker wiadomości Celery i backend cache
- `celery-worker-rss` — worker obsługujący kolejkę zadań RSS
- `celery-worker-default` — worker obsługujący domyślną kolejkę Celery
- `celery-beat` — harmonogram cyklicznych zadań

Workery Celery działają z ograniczoną współbieżnością `--concurrency=2`,
aby ograniczyć wykorzystanie zasobów środowiska produkcyjnego.

Celery Beat odpowiada za cykliczne uruchamianie pobierania wiadomości RSS.
Komunikacja pomiędzy Celery Beat i workerami odbywa się przez Redis.

Konfiguracja produkcyjna wykorzystuje zmienne środowiskowe do przechowywania
danych dostępowych do PostgreSQL i Redis oraz ustawień Django.

## Dostępne adresy

| Adres | Opis |
|---|---|
| `/admin/` | Panel administracyjny Django |
| `/api/articles/` | Lista i zarządzanie artykułami |
| `/api/categories/` | Lista i zarządzanie kategoriami |
| `/api/tags/` | Lista i zarządzanie tagami |
| `/api/source/` | Lista i zarządzanie źródłami RSS |
| `/api/articles/<id>/like/` | Polubienie / odlubienie artykułu |
| `/api/auth/users/` | Rejestracja użytkownika (Djoser) |
| `/api/auth/jwt/create/` | Logowanie — pobranie tokenu JWT |
| `/api/schema/swagger-ui/` | Interaktywna dokumentacja API (Swagger) |
| `/graphql/` | Interaktywny endpoint GraphQL (GraphiQL) |

## GraphQL API

Oprócz REST API projekt udostępnia endpoint GraphQL zbudowany przy użyciu
Strawberry GraphQL.

Interaktywny interfejs GraphiQL jest dostępny pod adresem:

`http://127.0.0.1:8000/graphql/`

Przykładowe zapytanie:

```graphql
query {
  articles {
    id
    title
    status
    publishedAt
    category {
      id
      name
    }
    tags {
      id
      name
    }
    source {
      id
      name
      rssUrl
      isActive
    }
  }
}
```

GraphQL pozwala klientowi określić, które pola i powiązane dane mają zostać
zwrócone przez API. Endpoint GraphQL działa równolegle z istniejącym REST API.

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
docker exec -it newshub-web-1 python manage.py test 
```

## Struktura projektu

```
newshub/
├── core/              # Konfiguracja projektu (settings, urls, celery)
├── articles/          # Modele Article, Category, Tag, Like, Notification
│   └── tests/         # Testy jednostkowe i integracyjne
├── sources/           # Model Source, zadania Celery pobierające RSS
├── graphql_api/       # Schemat i konfiguracja GraphQL
├── docker-compose.yml # Definicja kontenerów (web, db, redis, celery worker/beat)
├── Dockerfile
└── requirements.txt
```

## Dokumentacja projektowa

Pełna dokumentacja projektowa (grupa docelowa, model domenowy, wymagania
niefunkcjonalne, roadmap) znajduje się w `plan_projektu.md` w głównym
folderze repozytorium.

## Decyzje projektowe i własny research

- **Czas życia tokenów JWT** — access token ustawiony na 30 minut (a nie
  domyślne 5), refresh token na 7 dni. Kompromis między bezpieczeństwem
  (krótszy access token ogranicza okno na jego nadużycie) a wygodą
  użytkownika (nie trzeba się logować co kilka minut).
- **Redis jako backend cache** zamiast domyślnego `LocMemCache` — Django
  z Gunicornem uruchamia wiele procesów roboczych (`--workers 3`), z
  których każdy miałby WŁASNĄ, osobną pamięć podręczną przy `LocMemCache`.
  Redis jest zewnętrznym, współdzielonym magazynem, więc cache działa
  spójnie niezależnie od tego, który worker obsłużył dane żądanie.
- **Idempotencja pobierania RSS** — zadanie `fetch_feed` sprawdza istnienie
  artykułu po `source_url` przed utworzeniem nowego wpisu, dzięki czemu
  wielokrotne uruchomienie tego samego zadania (np. przy błędzie sieci
  i ponownej próbie) nie tworzy duplikatów artykułów.

## Autor

Ewelina Szymańska — praca dyplomowa, kurs Python Web Development. 