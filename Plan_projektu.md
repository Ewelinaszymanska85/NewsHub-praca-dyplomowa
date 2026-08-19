# NewsHub — Agregator wiadomości
### Praca dyplomowa — Python Web Development (Django)

---

## 1. Discovery / Definicja produktu

NewsHub to agregator wiadomości pobierający artykuły z co najmniej dwóch zewnętrznych
źródeł RSS w sposób cykliczny i automatyczny. Zalogowani użytkownicy mogą dodatkowo
zgłaszać własne artykuły do publikacji — każde takie zgłoszenie wymaga zatwierdzenia przez
administratora (superusera), zanim stanie się publicznie widoczne.

**Priorytety:**
- Automatyczna, cykliczna agregacja treści z zewnętrznych źródeł RSS
- Przejrzysty przepływ moderacji treści zgłaszanych przez użytkowników
- W pełni udokumentowane, przetestowane REST API

---

## 2. Grupa docelowa (Target Audience)

- **Czytelnicy indywidualni** — osoby chcące mieć jedno miejsce do śledzenia wiadomości
  z kilku różnych źródeł bez konieczności odwiedzania każdej strony osobno (oszczędność czasu,
  wygoda filtrowania po kategoriach/tagach)
- **Aktywni użytkownicy/twórcy treści** — osoby chcące zgłaszać własne artykuły/newsy do
  szerszej publiczności, z korzyścią w postaci mniejszych, bardziej niszowych społeczności
  tematycznych niż duże portale
- **Administratorzy/moderatorzy treści** — osoby zarządzające jakością publikowanych treści,
  potrzebujące wygodnego panelu do zatwierdzania/odrzucania zgłoszeń oraz zarządzania
  źródłami RSS
- **Deweloperzy/integratorzy zewnętrzni** — potencjalni odbiorcy udokumentowanego REST
  API, którzy mogliby zbudować własną aplikację kliencką (np. mobilną) korzystającą z danych
  NewsHub

---

## 3. Uzasadnienie wyboru frameworka i technologii

- **Django + Django REST Framework** — wybrany ze względu na wbudowany ORM, gotowy
  system uwierzytelniania i panel administracyjny, co pozwala skupić się na logice biznesowej
  agregacji treści zamiast budować te elementy od zera. Alternatywy (FastAPI, Flask) wymagałyby
  ręcznej konfiguracji panelu admina i ORM.
- **PostgreSQL** — relacyjna baza danych z pełnym wsparciem dla blokad wierszy
  (`select_for_update`), co jest istotne przy współbieżnym przetwarzaniu artykułów przez
  Celery workery.
- **Redis** — broker wiadomości dla Celery oraz backend cache.
- **Celery + Celery Beat** — do cyklicznego pobierania kanałów RSS w tle, bez blokowania
  głównego procesu Django.
- **Docker + docker-compose** — do konteneryzacji całego środowiska (Django, PostgreSQL,
  Redis, Celery worker, Celery Beat) i ułatwienia wdrożenia (deployment).

---

## 4. Założenia architektoniczne (Core Architecture Assumptions)

- Aplikacja webowa z REST API jako głównym interfejsem (Django REST Framework) —
  bez własnego frontendu w zakresie tego projektu; klientem API może być dowolna
  aplikacja zewnętrzna (przeglądarkowa, mobilna) lub narzędzia typu Postman/Swagger UI
- Artykuły pozyskiwane automatycznie z min. 2 kanałów RSS (biblioteka `feedparser`)
- Użytkownicy mogą się rejestrować i logować (JWT — `djangorestframework-simplejwt` + `djoser`)
- Zgłoszenia artykułów od użytkowników wymagają zatwierdzenia przez administratora
  (superusera) przed publikacją
- Całość uruchamiana i konteneryzowana przez Docker (Django, baza danych, Redis, workery Celery)
- Brak wymogu komunikacji w czasie rzeczywistym (np. WebSockety) — aktualizacje treści
  odbywają się cyklicznie przez Celery Beat, nie na żywo

---

## 5. Wymagania użytkownika (User Stories)

- Jako **gość**, chcę przeglądać zatwierdzone artykuły i filtrować je po kategorii/tagach, aby
  szybko znaleźć interesujące mnie treści.
- Jako **zalogowany użytkownik**, chcę zgłosić własny artykuł do publikacji, aby podzielić się
  interesującą treścią ze społecznością.
- Jako **zalogowany użytkownik**, chcę polubić artykuł, aby wyrazić zainteresowanie daną treścią.
- Jako **administrator (superuser)**, chcę przeglądać oczekujące zgłoszenia i zatwierdzać lub
  odrzucać je masowo, aby efektywnie moderować treści.
- Jako **administrator**, chcę zarządzać źródłami RSS (dodawać/wyłączać kanały), aby
  kontrolować, skąd pochodzą agregowane treści.
- Jako **deweloper/integrator**, chcę mieć dostęp do dobrze udokumentowanego API
  (Swagger/OpenAPI), aby łatwo zintegrować się z systemem.

---

## 6. Specyfikacja funkcjonalna (Functional Specification)

- Cykliczne pobieranie artykułów z min. 2 źródeł RSS (Celery Beat + `feedparser`)
- Rejestracja, logowanie, wylogowanie z uwierzytelnianiem tokenowym (JWT)
- Przeglądanie, wyszukiwanie i filtrowanie artykułów (po kategorii, tagach, źródle)
- Zgłaszanie własnych artykułów przez zalogowanych użytkowników (status: PENDING)
- Panel moderacji w Django Admin: zatwierdzanie/odrzucanie zgłoszeń (custom actions)
- Polubienia artykułów (relacja ManyToMany User ↔ Article)
- Cache najpopularniejszych/najnowszych artykułów (niskopoziomowe API cache)
- Powiadomienie (sygnał `post_save`) informujące adminów o nowym zgłoszeniu do moderacji
- Pełna dokumentacja API (drf-spectacular / Swagger UI)
- Walidacja danych wejściowych z czytelnymi komunikatami błędów
- Testy jednostkowe i integracyjne kluczowych funkcjonalności

---

## 7. Specyfikacja przepływu użytkownika (User Flow Specification)

**Przepływ: czytelnik przegląda i filtruje artykuły**
1. Użytkownik (gość lub zalogowany) wysyła żądanie `GET /api/articles/`
2. Opcjonalnie dodaje parametry filtrowania (`?category=`, `?tag=`, `?search=`)
3. API zwraca listę zatwierdzonych artykułów (status=APPROVED), z paginacją
4. Użytkownik może pobrać szczegóły pojedynczego artykułu (`GET /api/articles/{id}/`)

**Przepływ: zgłoszenie artykułu przez użytkownika**
1. Użytkownik loguje się (`POST /api/auth/jwt/create/`) i otrzymuje token
2. Wysyła `POST /api/articles/` z tytułem, treścią i tokenem w nagłówku Authorization
3. Artykuł zapisywany ze statusem `PENDING`
4. Sygnał `post_save` tworzy rekord `Notification` powiązany z artykułem, widoczny dla
   administratorów
5. Użytkownik widzi status swojego zgłoszenia przez `GET /api/articles/my-submissions/`

**Przepływ: moderacja zgłoszenia przez administratora**
1. Superuser loguje się do panelu Django Admin
2. Przegląda listę artykułów filtrowaną po statusie `PENDING`
3. Zaznacza wybrane artykuły i wybiera akcję "Zatwierdź" lub "Odrzuć"
4. Status zmienia się na `APPROVED`/`REJECTED`; zatwierdzone artykuły stają się widoczne
   publicznie w API

**Przepływ: cykliczne pobieranie z RSS (w tle, bez udziału użytkownika)**
1. Celery Beat wysyła sygnał zgodnie z harmonogramem (np. co 30 minut)
2. Worker Celery pobiera każde aktywne źródło (`Source.objects.filter(is_active=True)`)
3. Dla każdego źródła: parsowanie przez `feedparser`, sprawdzenie duplikatów po linku,
   zapis nowych artykułów ze statusem `APPROVED` (treści z zaufanych, predefiniowanych
   źródeł nie wymagają ręcznej moderacji)

---

## 8. Wymagania niefunkcjonalne (Non-Functional Requirements)

- **Wydajność** — lista artykułów powinna odpowiadać szybko dzięki cache; pobieranie RSS
  nie powinno blokować głównego procesu Django (realizowane przez Celery)
- **Skalowalność** — architektura z osobnym brokerem (Redis) i workerami Celery pozwala
  dodawać kolejne procesy robocze niezależnie od serwera aplikacji
- **Niezawodność** — mechanizm retry przy pobieraniu RSS (chwilowa niedostępność źródła
  nie powoduje utraty danych z innych źródeł)
- **Spójność danych** — zabezpieczenie przed duplikatami artykułów (idempotencja) oraz przed
  race condition przy równoległym przetwarzaniu tego samego źródła (`select_for_update`)
- **Bezpieczeństwo** — uwierzytelnianie tokenowe, ograniczenie operacji zapisu do zalogowanych
  użytkowników, ograniczenie moderacji wyłącznie do superusera
- **Utrzymywalność** — dobrze udokumentowany kod, testy jednostkowe/integracyjne,
  wygenerowana dokumentacja API (Swagger), czytelny README z historią commitów

---

## 9. Model domenowy (Domain Model)

**Główne encje i relacje:**

- **Source** (źródło RSS) — nazwa, URL kanału, aktywność (`is_active`)
- **Category** (kategoria) — nazwa; artykuł należy do jednej kategorii (`ForeignKey`)
- **Tag** — nazwa; artykuł może mieć wiele tagów (`ManyToMany`)
- **Article** (artykuł) — tytuł, treść/streszczenie, link źródłowy, data publikacji, status
  (`PENDING` / `APPROVED` / `REJECTED`), źródło (`ForeignKey` do `Source`, opcjonalne —
  puste dla zgłoszeń użytkowników), autor zgłoszenia (`ForeignKey` do `User`, opcjonalne —
  puste dla artykułów z RSS)
- **Like** (tabela pośrednia `through`, opcjonalnie z `created_at`) — łączy `User` i `Article`,
  reprezentuje polubienie
- **Notification** (powiadomienie) — treść komunikatu, powiązany artykuł (`ForeignKey` do
  `Article`), status przeczytania (`is_read`), data utworzenia; tworzony automatycznie przez
  sygnał `post_save` przy każdym nowym zgłoszeniu artykułu, widoczny dla adminów w panelu
- **User** — wbudowany model Django; może zgłaszać artykuły i polubienia; superuser
  moderuje zgłoszenia

**Relacje:**
- Source → Article: `OneToMany` (jedno źródło, wiele artykułów)
- Category → Article: `OneToMany`
- Article ←→ Tag: `ManyToMany`
- User ←→ Article (polubienia): `ManyToMany` przez tabelę pośrednią `Like`
- User → Article (zgłoszenia): `OneToMany` przez pole `submitted_by`
- Article → Notification: `OneToMany` (jeden artykuł może wygenerować powiadomienie o
  zgłoszeniu; model przygotowany też pod przyszłe rozszerzenie o inne typy powiadomień)

**Podsumowanie modeli (6 własnych + wbudowany User):** Source, Category, Tag, Article,
Like, Notification.

---

## 10. Uwierzytelnianie i zarządzanie użytkownikami (Authentication & User Management)

- **JWT** (`djangorestframework-simplejwt` + `djoser`) — logowanie, odświeżanie tokenu
- **Własny research:** świadome skonfigurowanie `ACCESS_TOKEN_LIFETIME` i
  `REFRESH_TOKEN_LIFETIME` w `SIMPLE_JWT`, z uzasadnieniem wybranych wartości
  (krótszy token dostępowy ze względów bezpieczeństwa, dłuższy refresh dla wygody użytkownika)
- **Superuser** — pełny dostęp do panelu admina, jedyna rola mogąca zatwierdzać/odrzucać
  zgłoszenia artykułów
- **Uprawnienia API (permissions)** — np. tylko zalogowani użytkownicy mogą zgłaszać artykuły
  i polubienia; tylko właściciel zgłoszenia może je edytować/usunąć przed moderacją

---

## 11. Panel administracyjny (Django Admin)

- `list_display` — tytuł, źródło, kategoria, status, data zgłoszenia
- `list_filter` — status (PENDING/APPROVED/REJECTED), kategoria, źródło
- `search_fields` — tytuł, treść
- **Custom admin actions** — "Zatwierdź zaznaczone artykuły", "Odrzuć zaznaczone artykuły"
  (akcje masowe)
- `inlines` — np. wyświetlanie tagów bezpośrednio przy artykule

---

## 12. Sygnały Django

- `post_save` na modelu `Article` — gdy nowy artykuł zostaje zgłoszony przez użytkownika
  (status=PENDING), sygnał tworzy nowy rekord `Notification` powiązany z tym artykułem,
  widoczny dla administratorów w panelu Django Admin jako lista oczekujących powiadomień

---

## 13. Cache i współbieżność (Performance & Background Processing)

- **Cache** — niskopoziomowe API cache dla list najpopularniejszych/najnowszych artykułów
  (LocMemCache lub Redis), z inwalidacją po zatwierdzeniu nowego artykułu
- **Celery + Celery Beat** — cykliczne zadanie pobierające artykuły z każdego aktywnego źródła
  RSS (np. co 30 minut), z mechanizmem retry przy niedostępności źródła i zabezpieczeniem
  przed duplikatami (idempotencja — sprawdzenie unikalności po linku artykułu)
- **`select_for_update()`** — zabezpieczenie przed race condition przy jednoczesnym
  przetwarzaniu tego samego źródła przez dwa workery

---

## 14. Wyszukiwanie i indeksowanie (Search & Indexing)

- Wyszukiwanie tekstowe artykułów po tytule i treści (np. `Q(title__icontains=) |
  Q(content__icontains=)`, zgodnie ze wzorcem poznanym przy budowie wyszukiwarki postów)
- Filtrowanie po kategorii, tagach i źródle jako dodatkowe, łączone parametry zapytania
- Aktualizacja dostępnych wyników wyszukiwania odbywa się na bieżąco — nowe zatwierdzone
  artykuły są od razu uwzględniane w wynikach (poza czasem życia cache listy)
- Rozszerzenie na przyszłość (poza zakresem MVP): pełnotekstowe wyszukiwanie PostgreSQL
  (`to_tsvector`/`to_tsquery`) dla bardziej zaawansowanego dopasowania

---

## 15. Warstwa API (API Layer) i dokumentacja

- REST API budowane w Django REST Framework — `ModelViewSet` dla głównych zasobów
  (Article, Source, Category, Tag), dodatkowe widoki funkcyjne dla akcji specjalnych (np.
  polubienie, zgłoszenia własne)
- **drf-spectacular** — automatyczna generacja schematu OpenAPI
- **`@extend_schema`** — opisy, tagi, parametry zapytań i kody odpowiedzi dla kluczowych
  endpointów (lista artykułów, zgłoszenie artykułu, polubienie, moderacja)
- Swagger UI dostępny pod `/api/schema/swagger-ui/`
- Minimalizacja liczby zapytań — eager loading (`select_related`/`prefetch_related`) przy
  pobieraniu artykułów z powiązanymi kategoriami/tagami, aby uniknąć problemu N+1

---

## 16. Wydajność i optymalizacja (Performance & Optimization Strategy)

- Cache list artykułów (najnowsze/najpopularniejsze) redukujący obciążenie bazy danych
- `select_related`/`prefetch_related` przy zapytaniach ORM, by uniknąć problemu N+1 przy
  wyświetlaniu list artykułów z kategoriami i tagami
- Paginacja wyników list (artykuły, zgłoszenia) zamiast zwracania wszystkich rekordów naraz
- Pobieranie RSS w tle (Celery) zamiast synchronicznie w cyklu żądania HTTP — użytkownik
  nigdy nie czeka na odpowiedź zewnętrznego serwisu RSS

---

## 17. Model bezpieczeństwa (Security Model)

- Uwierzytelnianie tokenowe (JWT) zamiast przechowywania haseł w każdym żądaniu
- Rozdzielenie uprawnień: zwykły użytkownik (odczyt + zgłaszanie/polubienia) vs superuser
  (pełna moderacja i zarządzanie źródłami)
- Walidacja i sanityzacja danych wejściowych na poziomie serializerów DRF (ochrona przed
  nieprawidłowymi/złośliwymi danymi w zgłoszeniach użytkowników)
- HTTPS zakładany jako standard w środowisku produkcyjnym (szyfrowanie danych w tranzycie)
- Konfigurowalny czas życia tokenów (krótszy access token ogranicza ryzyko nadużycia
  przechwyconego tokenu)
- Brak możliwości moderacji przez zwykłych użytkowników — wyłącznie superuser/staff

---

## 18. Walidacja i obsługa błędów

- **Walidacja danych wejściowych** — serializery DRF z czytelnymi komunikatami błędów
  (np. tytuł artykułu nie może być pusty, URL musi być poprawny)
- **Walidacja logiki biznesowej** — np. nie można zatwierdzić już zatwierdzonego artykułu;
  nie można polubić tego samego artykułu dwukrotnie
- **Poprawne kody HTTP** — 200/201/202/204 dla sukcesu, 400 dla błędnej walidacji, 401/403
  dla braku uprawnień, 404 dla nieistniejących zasobów

---

## 19. Testy

## 19. Testy

Zaimplementowano **33 testy** jednostkowe i integracyjne, wszystkie przechodzące
(`python manage.py test` uruchomione wewnątrz kontenera Docker):

- **Modele** (Article, Category, Notification, Source) — poprawność tworzenia,
  wartości domyślne, `__str__`, ograniczenia unikalności, sortowanie
- **API artykułów** — lista publiczna (tylko APPROVED), szczegóły, 404 dla
  nieistniejących zasobów
- **Walidacja danych wejściowych** — brakujące pola wymagane, niepoprawny URL
- **Polubienia** — autoryzacja (401 dla gościa), toggle like/unlike
- **Zgłaszanie artykułów** — autoryzacja, status PENDING, przypisanie
  `submitted_by`, tworzenie `Notification` przez sygnał `post_save`
- **Autoryzacja JWT** — rejestracja, walidacja siły hasła, logowanie,
  odrzucenie błędnych danych, odświeżanie tokenu (refresh)
- **Moderacja (Django Admin)** — custom actions zatwierdzania/odrzucania,
  izolacja działania (nie wpływa na inne rekordy), zabezpieczenie dostępu 
---

## 20. Docker i wdrożenie (Deployment & Distribution)

- `docker-compose.yml` z osobnymi kontenerami: Django (web), PostgreSQL, Redis,
  Celery worker, Celery Beat
- Osobne obrazy/serwisy dla każdej odpowiedzialności (dobra struktura kontenerów, nie
  jeden monolityczny kontener)
- Zmienne środowiskowe (`.env`) do konfiguracji sekretów (klucze, hasła do bazy)
- Plan wdrożenia (deployment) na docelowy serwer/hosting (do doprecyzowania na etapie
  implementacji)

---

## 21. Monitorowanie i utrzymanie (Observability & Maintenance)

- Logowanie błędów backendu (np. nieudane próby pobrania RSS, błędy walidacji) do pliku
  logów lub konsoli w środowisku deweloperskim
- Logi z Celery (worker/beat) jako podstawowy wgląd w stan cyklicznych zadań w tle
- Możliwość rozszerzenia o narzędzie **Flower** do monitoringu kolejek i workerów Celery
  (poza zakresem MVP, wymieniane jako świadome rozszerzenie architektury)
- Podstawowe metryki do obserwacji: liczba nieudanych pobrań RSS, liczba oczekujących
  zgłoszeń do moderacji, czas odpowiedzi kluczowych endpointów

---

## 22. Plan działania (Implementation Roadmap)

### 22.1 MVP
- Modele: Source, Category, Tag, Article, Like
- Rejestracja/logowanie z JWT
- Cykliczne pobieranie z 2 źródeł RSS (Celery Beat)
- Przeglądanie i filtrowanie zatwierdzonych artykułów
- Podstawowy panel admina z moderacją

### 22.2 V1.0
- Zgłaszanie artykułów przez użytkowników + pełny przepływ moderacji
- Polubienia artykułów
- Sygnał powiadamiający o nowych zgłoszeniach
- Cache list artykułów
- Dokumentacja API (drf-spectacular)

### 22.3 V1.5+
### 22.3 V1.5+

**Zrealizowane:**
- ✅ Testy jednostkowe i integracyjne (33 testy, pełne pokrycie kluczowych funkcjonalności)
- ✅ Docker Compose z pełnym stosem (Django + DB + Redis + Celery + Beat),
  zweryfikowany przez pełne uruchomienie od zera (`docker compose down -v`
  + `up -d --build` + migracje + testy na czystym środowisku)
- ✅ Idempotencja przy pobieraniu RSS (sprawdzenie unikalności po `source_url`)

**Poza zakresem MVP obrony (plan na przyszłość):**
- Mechanizm retry przy chwilowej niedostępności źródła RSS
- Deployment na docelowe środowisko produkcyjne (VPS/PaaS)
- Rozszerzenia: komentarze, personalizowane rekomendacje na podstawie polubień,
  pełnotekstowe wyszukiwanie PostgreSQL, monitoring przez Flower
---

## Plan deploymentu (Deployment & Distribution)

### Stan obecny — przygotowanie produkcyjne

Aplikacja jest już częściowo przygotowana do wdrożenia produkcyjnego, co zostało
faktycznie zaimplementowane i przetestowane lokalnie:

- **Serwer aplikacji:** Gunicorn (`gunicorn core.wsgi:application --workers 3`)
  zamiast developerskiego `manage.py runserver` - Gunicorn to standardowy,
  produkcyjny serwer WSGI, obsługujący wiele procesów-workerów jednocześnie
- **Konfiguracja przez zmienne środowiskowe** - `SECRET_KEY`, `DEBUG`,
  `ALLOWED_HOSTS`, `DATABASE_HOST`, `REDIS_HOST` są odczytywane ze zmiennych
  środowiskowych z bezpiecznymi wartościami domyślnymi do developmentu, co
  pozwala na łatwą zmianę konfiguracji na produkcji bez modyfikacji kodu
- **Pełna konteneryzacja** - wszystkie komponenty (aplikacja Django, baza
  danych PostgreSQL, broker/cache Redis, Celery worker, Celery Beat) działają
  jako osobne, niezależne kontenery zdefiniowane w `docker-compose.yml`, co
  jest bezpośrednio przenośne na środowisko produkcyjne
- **Współdzielony cache** - użycie Redis (zamiast domyślnego `LocMemCache`)
  zapewnia poprawne działanie cache niezależnie od liczby uruchomionych
  procesów/workerów serwera aplikacji

### Docelowa platforma wdrożenia

Jako docelowe środowisko produkcyjne rozważane jest jedno z następujących
rozwiązań (typowych dla mniejszych/średnich projektów tej skali):

- **VPS (Virtual Private Server)** z zainstalowanym Dockerem (np. DigitalOcean
  Droplet, Hetzner Cloud) - daje pełną kontrolę nad środowiskiem przy
  relatywnie niskim koszcie, i pozwala uruchomić dokładnie ten sam
  `docker-compose.yml`, który już działa lokalnie
- **Platforma PaaS z natywnym wsparciem dla Dockera** (np. Render, Railway) -
  jako alternatywa wymagająca mniejszej ręcznej konfiguracji serwera, kosztem
  nieco mniejszej elastyczności

### Planowane kroki wdrożenia

1. Wynajęcie serwera / założenie konta na wybranej platformie
2. Skonfigurowanie zmiennych środowiskowych produkcyjnych (silny, losowy
   `SECRET_KEY`; `DEBUG=False`; `ALLOWED_HOSTS` ograniczone do docelowej domeny)
3. Wdrożenie serwera odwrotnego proxy (np. Nginx) przed Gunicornem - do obsługi
   plików statycznych, terminacji SSL/HTTPS oraz jako dodatkowa warstwa
   bezpieczeństwa przed bezpośrednią ekspozycją Gunicorna
4. Skonfigurowanie certyfikatu SSL (np. przez Let's Encrypt/Certbot) - HTTPS
   jest wymogiem bezpieczeństwa dla API obsługującego uwierzytelnianie
   tokenowe
5. Uruchomienie `docker compose up -d --build` na docelowym serwerze
6. Zastosowanie migracji i utworzenie konta administratora na produkcyjnej
   bazie danych
7. Skonfigurowanie automatycznych kopii zapasowych bazy danych PostgreSQL
8. Podłączenie domeny do adresu IP serwera

### Możliwe rozszerzenie: CI/CD

Jako naturalne rozszerzenie procesu wdrożenia rozważane jest skonfigurowanie
prostego pipeline'u CI/CD (np. GitHub Actions), który przy każdym pushu do
głównej gałęzi repozytorium automatycznie:
- uruchamia zestaw testów (`python manage.py test articles`)
- w przypadku powodzenia, buduje i wypycha nowy obraz Docker
- opcjonalnie automatycznie wdraża nową wersję na serwer produkcyjny

Ten element pozostaje na etapie planowania (poza zakresem MVP obrony), ale
architektura projektu (pełna konteneryzacja, testy w izolowanym środowisku)
jest już przygotowana pod jego wdrożenie w przyszłości.

## Napotkane problemy i rozwiązania — migracja na PostgreSQL i pełny Docker Compose

Podczas przechodzenia z domyślnej bazy SQLite na docelowy, produkcyjny PostgreSQL
napotkano kilka rzeczywistych problemów, których rozwiązanie dobrze ilustruje
różnice między środowiskiem developerskim a produkcyjnym.

### Problem 1: UnicodeDecodeError przy połączeniu z PostgreSQL (Windows)

Po skonfigurowaniu `psycopg2` do połączenia z kontenerem PostgreSQL uruchomionym
lokalnie przez Docker, próba połączenia z poziomu lokalnego środowiska
wirtualnego (Windows, polska lokalizacja systemu) kończyła się błędem:

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb3 in position 86: invalid start byte
```

**Diagnoza:** błąd nie wskazywał bezpośrednio na przyczynę - `UnicodeDecodeError`
maskował prawdziwy komunikat błędu. Weryfikacja przez bezpośrednie połączenie
`psql` wewnątrz kontenera (`docker exec -it <kontener> psql -U ... -d ...`)
potwierdziła, że dane logowania i sama baza danych są poprawnie skonfigurowane -
problem leżał wyłącznie w sposobie, w jaki biblioteka `psycopg2` na Windowsie
(przy polskiej lokalizacji systemu) dekodowała komunikaty zwracane przez
bibliotekę `libpq`.

**Rozwiązanie:** zamiast dalej debugować specyficzny problem Windows/psycopg2/
locale, przeniesiono całą aplikację (Django, Celery worker, Celery Beat) do
działania w pełni wewnątrz Docker Compose. Kontenery komunikują się między sobą
przez wewnętrzną sieć Dockera (adresowanie po nazwie usługi, np. `db`, `redis`),
zamiast przez `localhost` z poziomu Windowsa - co całkowicie eliminuje
problematyczną ścieżkę połączenia. Jest to również bardziej poprawne
architektonicznie podejście produkcyjne (spójne środowisko w kontenerach),
a nie tylko obejście błędu.

### Problem 2: Ograniczenia długości pól ujawnione dopiero na PostgreSQL

Po przejściu na PostgreSQL i próbie ponownego pobrania rzeczywistych danych
z RSS (BBC News, NASA), zadanie Celery `fetch_feed` zaczęło zgłaszać błędy:

```
django.db.utils.DataError: value too long for type character varying(200)
```

**Diagnoza:** pola `title` (pierwotnie `max_length=300`, ale w bazie
zapisane z wcześniejszym limitem 200 z poprzedniej migracji) oraz `source_url`
(domyślny limit `URLField` w Django to 200 znaków) okazały się za krótkie dla
rzeczywistych danych - część tytułów artykułów BBC News przekraczała limit,
a linki RSS z BBC zawierają długie parametry śledzenia
(`?at_medium=RSS&at_campaign=rss`), które znacząco wydłużają URL.

Co istotne, ten problem **nie ujawnił się w ogóle podczas pracy na SQLite** -
SQLite jest znacznie mniej rygorystyczny w egzekwowaniu ograniczeń długości
pól tekstowych niż PostgreSQL, który ściśle przestrzega zadeklarowanego
`VARCHAR(n)`.

**Rozwiązanie:** zwiększono `max_length` pola `title` do 500 oraz jawnie
ustawiono `max_length=500` dla pola `source_url` (zamiast polegać na
domyślnym limicie 200 znaków `URLField`), a następnie wygenerowano
i zastosowano odpowiednie migracje.

### Wniosek

Ten epizod jest dobrą, praktyczną ilustracją tego, dlaczego testowanie na
docelowym silniku bazy danych (a nie tylko na wygodnym SQLite) jest istotne
przed wdrożeniem produkcyjnym - niektóre ograniczenia i błędy ujawniają się
wyłącznie przy bardziej rygorystycznym zachowaniu PostgreSQL, mimo że kod
działał pozornie bezbłędnie na SQLite przez cały wcześniejszy etap rozwoju
projektu.

## Napotkane problemy i rozwiązania — cache a wiele procesów Gunicorna

Po przejściu z developerskiego `runserver` na produkcyjny serwer Gunicorn
(uruchomiony z 3 workerami: `--workers 3`), zaobserwowano niespójne czasy
odpowiedzi dla endpointu `/api/articles/`, mimo że lista artykułów była
buforowana w cache na 5 minut (`@cache_page(60 * 5)`):

```
Żądanie 1: 1097 ms
Żądanie 2: 143 ms
Żądanie 3: 749 ms
Żądanie 4: 188 ms
```

**Diagnoza:** domyślny backend cache Django (`LocMemCache`) przechowuje dane
**w pamięci pojedynczego procesu**. Gunicorn z `--workers 3` uruchamia trzy
całkowicie niezależne procesy Pythona, z których każdy ma **własną, oddzielną
kopię** cache. W efekcie żądanie trafiające losowo (przez load-balancing
Gunicorna) do workera, który jeszcze nie obsłużył danego zapytania, zawsze
skutkowało brakiem trafienia w cache (cache miss) - niezależnie od tego, że
inny worker mógł już mieć te same dane zbuforowane.

Jest to praktyczna ilustracja zasady poznanej przy okazji omawiania architektury
Django/Gunicorn: globalny stan (w tym cache) trzymany lokalnie w procesie nie
jest widoczny dla innych procesów tego samego serwera - musi być przechowywany
w zewnętrznym, współdzielonym systemie.

**Rozwiązanie:** zmieniono backend cache z `LocMemCache` na `django-redis`
(`RedisCache`), wykorzystując już istniejący w projekcie kontener Redis (ten
sam, który służy jako broker dla Celery, ale pod inną bazą logiczną - `/1`
zamiast `/0` używanego przez Celery, aby uniknąć mieszania danych).

Po zmianie, kolejne żądania do tego samego endpointu zwracały spójnie niskie
czasy odpowiedzi (~140-160 ms) niezależnie od tego, który worker Gunicorna
obsłużył żądanie - potwierdzając, że cache jest teraz poprawnie współdzielony
między wszystkimi procesami serwera aplikacji.

### Wniosek

Ten problem nie ujawniłby się przy testowaniu wyłącznie na developerskim
`runserver` (który domyślnie działa jako pojedynczy proces) - stał się widoczny
dopiero po przejściu na architekturę wieloprocesową, bliższą rzeczywistemu
środowisku produkcyjnemu. Pokazuje to, dlaczego testowanie z konfiguracją
zbliżoną do produkcyjnej (Gunicorn z wieloma workerami) jest istotnym etapem
przygotowania aplikacji do wdrożenia, niezależnie od tego, czy faktyczny
deployment na zewnętrzny serwer został wykonany. 

## Rozszerzenie API o GraphQL

W finalnej wersji projektu NewsHub, obok istniejącego REST API, dodano również
endpoint GraphQL z wykorzystaniem bibliotek Strawberry GraphQL oraz
Strawberry GraphQL Django.

Endpoint dostępny jest pod adresem:

`/graphql/`

GraphQL umożliwia klientowi pobieranie tylko wybranych pól oraz powiązanych
danych, np. artykułu razem z kategorią, tagami i źródłem RSS.

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

## Uwagi końcowe

Ten dokument celowo pomija dwie sekcje z ogólnego szablonu planowania aplikacji, które nie
mają zastosowania do tego projektu: **Frontend Architecture & UI Foundation** (NewsHub jest
projektem czysto backendowym/API, bez własnego interfejsu SPA w zakresie pracy dyplomowej)
oraz **Sync Architecture (Cloud Layer)** (dotyczyła specyficznie synchronizacji danych offline-
online w innym typie aplikacji i nie ma odpowiednika w architekturze agregatora wiadomości).

Plan zostanie doprecyzowany na etapie implementacji (dokładne pola modeli, pełna lista
endpointów, struktura testów), zgodnie z pełną listą kryteriów oceny obrony: jakość pracy i
kodu, praca z Gitem (README + historia commitów), uzasadnienie wyboru frameworka, Docker,
zgodność z CRUD/REST, współbieżność (Celery), baza danych, pokrycie testami, deployment,
tokeny/superuser, relacje 1:1 i many-to-many, własny research, walidacja danych i logiki
biznesowej, udokumentowane endpointy, poprawne kody błędów, konfiguracja panelu admina,
akcje podpięte pod sygnały.

