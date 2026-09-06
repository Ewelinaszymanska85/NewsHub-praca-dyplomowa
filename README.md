# NewsHub — Agregator wiadomości

Praca dyplomowa — kurs Python Web Development (Django).

NewsHub to aplikacja webowa służąca do agregowania, przetwarzania i udostępniania artykułów informacyjnych.

System automatycznie i cyklicznie pobiera artykuły z zewnętrznych źródeł RSS. Zalogowani użytkownicy mogą również zgłaszać własne artykuły do publikacji. Artykuły podlegają moderacji przed ich publicznym udostępnieniem.

Projekt udostępnia REST API, GraphQL API, panel administracyjny Django oraz mechanizmy automatyzacji oparte na Celery i Redis.

## Funkcjonalności

- Automatyczna, cykliczna agregacja artykułów z wielu źródeł RSS przy użyciu Celery Beat i `feedparser`
- Obsługa poziomów zaufania źródeł RSS: `TRUSTED`, `NORMAL` i `BLOCKED`
- Automatyczne nadawanie statusu artykułu na podstawie poziomu zaufania źródła
- Pomijanie nieaktywnych i zablokowanych źródeł RSS
- Ochrona przed tworzeniem duplikatów artykułów na podstawie `source_url`
- Pobieranie i zapisywanie daty publikacji artykułu z RSS z obsługą pól `published` i `updated`
- Import danych artykułu bezpośrednio z podanego adresu URL
- Dedykowane scrapery oraz obsługa nieobsługiwanych domen i błędów scrapowania
- Automatyczna kategoryzacja artykułów
- Możliwość kategoryzacji przy użyciu lokalnego modelu AI przez Ollama API
- Lokalna kategoryzacja na podstawie słów kluczowych jako fallback w przypadku niedostępności AI
- Dodatkowy fallback kategoryzacji w przypadku braku dopasowania słów kluczowych
- Rejestracja i logowanie użytkowników z uwierzytelnianiem JWT
- Zgłaszanie artykułów przez zalogowanych użytkowników
- Moderacja artykułów przed ich publicznym udostępnieniem
- Panel administracyjny Django z akcjami masowymi do zatwierdzania i odrzucania artykułów
- Publiczne API udostępniające zatwierdzone artykuły
- Polubienia i odlubienia artykułów
- Automatyczne powiadomienia o nowych zgłoszeniach do moderacji
- Cache list artykułów
- Paginacja REST API
- Dokumentacja REST API przez Swagger UI / drf-spectacular
- GraphQL API do elastycznego pobierania artykułów i powiązanych danych
- Testy jednostkowe i integracyjne przy użyciu `pytest` i `pytest-django`
- Automatyczne uruchamianie testów przez GitHub Actions

## Stos technologiczny

- **Backend:** Django 6.0, Django REST Framework
- **REST API:** Django REST Framework
- **GraphQL API:** Strawberry GraphQL + Strawberry GraphQL Django
- **Baza danych:** PostgreSQL 16
- **Broker / cache:** Redis
- **Zadania w tle:** Celery + Celery Beat
- **Uwierzytelnianie:** djangorestframework-simplejwt + Djoser
- **Dokumentacja API:** drf-spectacular
- **Agregacja RSS:** feedparser
- **Scraping:** requests + BeautifulSoup
- **AI:** Ollama API + lokalny model Llama 3.2
- **Testy:** pytest + pytest-django
- **CI:** GitHub Actions
- **Konteneryzacja:** Docker + Docker Compose
- **Deployment:** Railway
- **Serwer aplikacji:** Gunicorn

## Model domenowy

| Model | Opis |
|---|---|
| `Source` | Źródło RSS — nazwa, URL kanału, aktywność i poziom zaufania |
| `Category` | Kategoria tematyczna artykułu |
| `Tag` | Tag przypisywany do artykułu |
| `Article` | Artykuł pochodzący z RSS albo zgłoszony przez użytkownika |
| `Like` | Polubienie artykułu przez użytkownika |
| `Notification` | Powiadomienie tworzone automatycznie dla zdarzeń wymagających uwagi |

## Źródła RSS i poziomy zaufania

Każde źródło RSS posiada poziom zaufania:

- `TRUSTED` — artykuły otrzymują automatycznie status `APPROVED`
- `NORMAL` — artykuły otrzymują status `PENDING`
- `BLOCKED` — źródło nie jest pobierane przez agregator

Nieaktywne źródła również są pomijane.

Zadanie pobierające RSS sprawdza `source_url` przed utworzeniem artykułu, dzięki czemu ponowne przetworzenie tego samego wpisu nie powoduje tworzenia duplikatów.

## Kategoryzacja artykułów

NewsHub posiada osobną warstwę odpowiedzialną za automatyczną kategoryzację artykułów.

Kategoryzacja może działać w kilku etapach:

1. Próba kategoryzacji przy użyciu lokalnego modelu AI przez Ollama API.
2. W przypadku niedostępności AI uruchamiana jest lokalna kategoryzacja na podstawie słów kluczowych.
3. Jeśli żadne słowo kluczowe nie zostanie dopasowane, wykorzystywany jest mechanizm fallback.

Model AI może wybrać kategorię wyłącznie spośród kategorii istniejących w bazie danych. Odpowiedź modelu jest dodatkowo weryfikowana przed zwróceniem kategorii przez aplikację.

Dzięki oddzieleniu kategoryzacji AI od pozostałej logiki awaria lub brak lokalnego modelu nie blokuje podstawowego działania systemu.

## Import artykułów z URL

Zalogowany użytkownik może przekazać adres URL artykułu do API.

Aplikacja:

1. Waliduje przekazany adres.
2. Dobiera odpowiedni scraper.
3. Pobiera dane artykułu.
4. Obsługuje nieobsługiwane domeny i błędy scrapowania.
5. Uruchamia mechanizm kategoryzacji.
6. Zwraca pobrane dane wraz z sugerowaną kategorią.

Mechanizm posiada testy obejmujące poprawny import, brak autoryzacji, nieobsługiwaną domenę, błąd scrapowania oraz zwracanie sugerowanej kategorii.

## Uruchomienie projektu — Docker

Wymagany jest Docker Desktop.

```bash
git clone <adres-repo>
cd newshub
docker compose up -d --build
```

Zastosowanie migracji:

```bash
docker compose exec web python manage.py migrate
```

Utworzenie administratora:

```bash
docker compose exec web python manage.py createsuperuser
```

Sprawdzenie konfiguracji Django:

```bash
docker compose exec web python manage.py check
```

Aplikacja lokalna jest dostępna pod adresem `http://127.0.0.1:8000/`.

## Dostępne adresy

| Adres | Opis |
|---|---|
| `/admin/` | Panel administracyjny Django |
| `/api/articles/` | REST API artykułów |
| `/api/articles/fetch-from-url/` | Import danych artykułu z podanego adresu URL i sugerowanie kategorii |
| `/api/categories/` | REST API kategorii |
| `/api/tags/` | REST API tagów |
| `/api/source/` | REST API źródeł RSS |
| `/api/articles/<id>/like/` | Polubienie / odlubienie artykułu |
| `/api/auth/users/` | Rejestracja użytkownika |
| `/api/auth/jwt/create/` | Logowanie i pobranie tokenów JWT |
| `/api/auth/jwt/refresh/` | Odświeżenie tokenu JWT |
| `/api/auth/jwt/verify/` | Weryfikacja tokenu JWT |
| `/api/schema/swagger-ui/` | Swagger UI |
| `/graphql/` | GraphQL / GraphiQL |

## GraphQL API

Oprócz REST API projekt udostępnia endpoint GraphQL zbudowany przy użyciu Strawberry GraphQL.

Lokalny interfejs GraphiQL jest dostępny pod adresem `http://127.0.0.1:8000/graphql/`.

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

GraphQL pozwala klientowi określić dokładnie, które pola i powiązane dane mają zostać zwrócone. Endpoint GraphQL działa równolegle z REST API.

## Dodawanie źródeł RSS

Źródła RSS można dodawać przez panel administracyjny: `/admin/` → Źródła RSS.

Przykład utworzenia źródła przez Django shell:

```python
from sources.models import Source

Source.objects.create(
    name="BBC News",
    rss_url="http://feeds.bbci.co.uk/news/rss.xml",
    is_active=True,
    trust_level="NORMAL",
)
```

Celery Beat odpowiada za cykliczne uruchamianie agregacji aktywnych źródeł RSS.

## Testy

Projekt wykorzystuje `pytest` oraz `pytest-django`.

Uruchomienie pełnego zestawu testów w Dockerze:

```bash
docker compose exec web pytest
```

Aktualny zestaw obejmuje 68 testów jednostkowych i integracyjnych.

Testy koncentrują się między innymi na:

- własnej logice biznesowej
- moderacji artykułów
- poziomach zaufania źródeł RSS
- agregacji RSS
- obsłudze dat publikacji
- scraperach
- walidacji danych
- imporcie artykułów z URL
- automatycznej kategoryzacji
- fallbacku w przypadku niedostępności AI
- publicznym API artykułów
- mechanizmie polubień

Testy zewnętrznych bibliotek i standardowego zachowania frameworka zostały ograniczone na rzecz testowania logiki należącej do aplikacji NewsHub.

## CI — GitHub Actions

Projekt posiada workflow GitHub Actions uruchamiany dla zmian kierowanych do głównej gałęzi projektu.

Środowisko CI wykorzystuje PostgreSQL i Redis jako usługi pomocnicze. Testy są uruchamiane poleceniem:

```bash
pytest
```

Dzięki temu lokalne środowisko testowe i CI korzystają z tego samego runnera testów.

## Wdrożenie produkcyjne

Aplikacja NewsHub została wdrożona na platformie Railway.

- **Publiczna aplikacja:** `https://newshub-praca-dyplomowa-production.up.railway.app`
- **Swagger UI:** `https://newshub-praca-dyplomowa-production.up.railway.app/api/schema/swagger-ui/`
- **GraphQL / GraphiQL:** `https://newshub-praca-dyplomowa-production.up.railway.app/graphql/`
- **REST API:** `https://newshub-praca-dyplomowa-production.up.railway.app/api/articles/`

Środowisko produkcyjne składa się z sześciu usług:

- `NewsHub-praca-dyplomowa` — aplikacja Django / REST API / GraphQL
- `Postgres` — baza danych PostgreSQL
- `Redis` — broker wiadomości Celery i backend cache
- `celery-worker-rss` — worker obsługujący zadania RSS
- `celery-worker-default` — worker obsługujący domyślną kolejkę Celery
- `celery-beat` — harmonogram zadań cyklicznych

Workery Celery działają z ograniczoną współbieżnością `--concurrency=2`, aby ograniczyć wykorzystanie zasobów środowiska produkcyjnego.

Celery Beat odpowiada za cykliczne uruchamianie pobierania wiadomości RSS. Komunikacja pomiędzy Celery Beat i workerami odbywa się przez Redis.

Konfiguracja produkcyjna wykorzystuje zmienne środowiskowe do przechowywania danych dostępowych do PostgreSQL i Redis oraz ustawień Django.

## Struktura projektu

```text
newshub/
├── .github/
│   └── workflows/          # GitHub Actions / CI
├── core/                   # Konfiguracja projektu Django
├── articles/               # Artykuły, kategorie, tagi, moderacja i polubienia
│   ├── tests/              # Testy aplikacji articles
│   └── categorization.py   # Automatyczna kategoryzacja i integracja AI
├── sources/                # Źródła RSS i zadania Celery
├── graphql_api/            # Schemat i konfiguracja GraphQL
├── docker-compose.yml      # Kontenery projektu
├── Dockerfile
├── pytest.ini              # Konfiguracja pytest-django
├── requirements.txt
└── README.md
```

## Decyzje projektowe

### JWT

Access token jest ustawiony na 30 minut, a refresh token na 7 dni. Rozwiązanie stanowi kompromis pomiędzy bezpieczeństwem a wygodą użytkownika.

### Redis jako backend cache

Redis został wykorzystany zamiast lokalnego `LocMemCache`.

Aplikacja uruchomiona z wieloma procesami Gunicorn wymaga współdzielonego magazynu cache. Redis zapewnia wspólną pamięć podręczną niezależnie od procesu obsługującego żądanie.

### Idempotencja pobierania RSS

Zadanie `fetch_feed` sprawdza, czy artykuł o danym `source_url` już istnieje. Dzięki temu wielokrotne wykonanie zadania nie powoduje tworzenia duplikatów.

### Poziomy zaufania źródeł

Poziom zaufania źródła wpływa bezpośrednio na sposób przetwarzania pobieranych artykułów.

Zaufane źródła mogą automatycznie publikować artykuły, standardowe źródła kierują je do moderacji, a źródła zablokowane nie są przetwarzane.

### Kategoryzacja z fallbackiem

Integracja AI została oddzielona od podstawowej logiki kategoryzacji. Jeśli lokalny model AI jest niedostępny, aplikacja nadal działa i wykorzystuje lokalną kategoryzację na podstawie słów kluczowych.

## Dokumentacja projektowa

Pełna dokumentacja projektowa, obejmująca m.in. grupę docelową, model domenowy, wymagania niefunkcjonalne i roadmapę, znajduje się w pliku `plan_projektu.md`.

## Autor

Ewelina Szymańska — praca dyplomowa, kurs Python Web Development.
