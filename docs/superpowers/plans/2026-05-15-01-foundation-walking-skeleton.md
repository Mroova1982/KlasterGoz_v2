# Plan 1: Foundation & Walking Skeleton — Implementation Plan

> ⚠️ **[SUPERSEDED — 2026-06-10]** Ten plan pochodzi z wcześniejszej sesji i używa innego podziału („Plan 1–7", gdzie dynamiczne header/footer to dopiero Plan 7). Został **zastąpiony** przez nowy podział na Fazy 0–6 (spec sekcja 2.1). Aktualny plan fundamentu: [`2026-06-10-faza-0-fundament.md`](2026-06-10-faza-0-fundament.md). Zachowany wyłącznie jako ślad historyczny — **nie realizować**.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wagtail project initialized with Docker (PostgreSQL + Redis), mockup styles imported, HomePage model with structured fields, home page renders 1:1 with mockup index.html, editor manages home content fully via Wagtail admin. Lokalnie działa end-to-end.

**Architecture:** Wagtail 6.x na Django 5.x z Postgres 16 + Redis 7 w Docker Compose. Split settings (base/dev). Server-side rendering — żadnego SPA/JS framework'a. CSS z mockupu (`assets/styles.css`) jako baza, vanilla JS dla slidera. Hero slides / pillars / stats jako Wagtail snippety; HomePage tylko je orkiestruje przez InlinePanel / chooser. TDD dla modeli + smoke testy dla rendering'u.

**Tech Stack:** Python 3.13, Wagtail 6, Django 5, PostgreSQL 16, Redis 7, Docker Compose, pytest-django, ruff, black, pre-commit, uv.

**Spec reference:** `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md` — sekcje 3 (Stack), 4 (Drzewo stron — tylko `/`), 5 (Modele treści — tylko HomePage + 3 snippety).

**Out of scope dla Planu 1:**
- Wszystkie page types poza HomePage (Plan 3)
- Templates poza home (Plan 4)
- Site settings beyond niezbędnego minimum (Plan 3)
- Header/footer dynamiczne sterowane z CMS (Plan 7) — w Planie 1 są statyczne partials
- Deploy / staging / CI/CD (Plan 2)
- Formularze / newsletter / email / search (Plan 5)
- Multilingual / SEO / structured data (Plan 6)
- Migracja danych (Plan 7)

---

## File structure

Pliki utworzone / zmodyfikowane w tym planie:

```
KlasterGoz_v2/
├── .gitignore                                       # CREATE
├── .editorconfig                                    # CREATE
├── README.md                                        # CREATE
├── pyproject.toml                                   # CREATE — uv-managed
├── docker-compose.dev.yml                           # CREATE
├── .dockerignore                                    # CREATE
├── Dockerfile.dev                                   # CREATE
├── .env.example                                     # CREATE
├── .env                                             # CREATE (gitignored)
├── pre-commit-config.yaml                           # CREATE
├── pytest.ini                                       # CREATE
│
├── klastergoz/                                      # main Django project
│   ├── __init__.py                                  # CREATE
│   ├── settings/
│   │   ├── __init__.py                              # CREATE
│   │   ├── base.py                                  # CREATE
│   │   ├── dev.py                                   # CREATE
│   │   └── test.py                                  # CREATE
│   ├── urls.py                                      # CREATE
│   ├── wsgi.py                                      # CREATE
│   └── asgi.py                                      # CREATE
│
├── apps/
│   ├── __init__.py                                  # CREATE
│   ├── home/                                        # CREATE — HomePage + tests
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                                # HomePage + relacje
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       └── test_views.py
│   └── shared/                                      # CREATE — snippety reużywalne
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py                                # HeroSlide, Pillar, Statistic snippety
│       ├── migrations/
│       └── tests/
│           ├── __init__.py
│           └── test_snippets.py
│
├── templates/                                       # CREATE — root templates
│   ├── base.html
│   ├── includes/
│   │   ├── header.html                              # statyczny przekład z mockupu (Plan 7 dynamizuje)
│   │   └── footer.html                              # statyczny przekład z mockupu
│   └── home/
│       └── home_page.html
│
├── static/                                          # CREATE — static assets
│   ├── css/
│   │   └── styles.css                               # kopia z mockup/assets/styles.css
│   ├── img/
│   │   ├── logo.svg                                 # kopia z mockup/assets/logo.svg
│   │   └── logo-white.svg
│   └── js/
│       └── home_slider.js                           # wyciągnięte z mockup/index.html
│
└── conftest.py                                      # CREATE — pytest fixtures root
```

---

## Task 1: Inicjalizacja repozytorium git i podstawowych plików

**Files:**
- Create: `.gitignore`, `.editorconfig`, `README.md`

- [ ] **Step 1.1: Zainicjalizować git repo w projekcie**

Run from `C:\Programer\Projekty\KlasterGoz_v2\`:
```bash
git init
git config core.autocrlf input
```
Expected: `Initialized empty Git repository in C:/Programer/Projekty/KlasterGoz_v2/.git/`

- [ ] **Step 1.2: Stworzyć `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
.eggs/
build/
dist/

# Virtual environments
.venv/
venv/
.python-version

# Django / Wagtail
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
.coverage
htmlcov/

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Docker
.docker/

# pytest
.pytest_cache/
.cache/

# uv
.uv/
# uv.lock — commit dla deterministycznych buildów (NIE ignoruj)

# OS
Thumbs.db
desktop.ini
```

- [ ] **Step 1.3: Stworzyć `.editorconfig`**

```
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true

[*.{html,css,js,json,yml,yaml,md}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

- [ ] **Step 1.4: Stworzyć początkowy `README.md`**

```markdown
# Klaster GOZ — portal

Portal marketingowy `klastergoz.pl` zarządzany przez Wagtail CMS.

## Stack

- Wagtail 6 / Django 5 / Python 3.12+
- PostgreSQL 16 / Redis 7
- Docker Compose dla dev

## Setup (dev)

\`\`\`bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up -d
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
\`\`\`

Strona: http://localhost:8000
Admin: http://localhost:8000/admin

## Dokumentacja projektu

- Spec: `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md`
- Plany: `docs/superpowers/plans/`
\`\`\`

- [ ] **Step 1.5: Commit**

```bash
git add .gitignore .editorconfig README.md
git commit -m "chore: initialize repository with base config files"
```

---

## Task 2: Konfiguracja środowiska Python z uv

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 2.1: Sprawdzić instalację uv**

```bash
uv --version
```
Expected: `uv 0.x.x` (jakikolwiek 0.4+). Jeśli brak — zainstalować: https://docs.astral.sh/uv/getting-started/installation/

- [ ] **Step 2.2: Stworzyć `pyproject.toml`**

```toml
[project]
name = "klastergoz-portal"
version = "0.1.0"
description = "Portal marketingowy klastergoz.pl — Wagtail CMS"
requires-python = ">=3.13,<3.14"
dependencies = [
    "wagtail>=6.3,<6.4",
    "django>=5.1,<5.2",
    "psycopg[binary]>=3.2",
    "redis>=5.2",
    "django-redis>=5.4",
    "python-dotenv>=1.0",
    "gunicorn>=23.0",
    "whitenoise>=6.8",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-django>=4.9",
    "pytest-cov>=5.0",
    "ruff>=0.7",
    "black>=24.10",
    "pre-commit>=4.0",
    "factory-boy>=3.3",
    "model-bakery>=1.20",
]

[tool.uv]
package = false                # to nie jest publikowany pakiet

[tool.ruff]
line-length = 100
target-version = "py313"
extend-exclude = ["migrations", "static", "media"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4", "DJ"]   # E/F/W = pyflakes/pycodestyle; I = isort; UP = pyupgrade; B = bugbear; C4 = comprehensions; DJ = Django
ignore = ["E501"]               # długość linii — Black zarządza

[tool.black]
line-length = 100
target-version = ["py313"]
extend-exclude = "migrations|static|media"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "klastergoz.settings.test"
python_files = ["test_*.py", "tests.py"]
addopts = "--reuse-db --tb=short"
```

- [ ] **Step 2.3: Zainstalować zależności**

```bash
uv sync
```
Expected: `Resolved N packages`, `Audited N packages`, virtualenv stworzony w `.venv/`.

- [ ] **Step 2.4: Sprawdzić Wagtail dostępny**

```bash
uv run wagtail --version
```
Expected: `6.3.x` (lub aktualna patch wersja).

- [ ] **Step 2.5: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: configure Python environment with uv and dependencies"
```

---

## Task 3: Bootstrap projektu Wagtail i podział settings

**Files:**
- Create: `klastergoz/{__init__.py,urls.py,wsgi.py,asgi.py}`, `klastergoz/settings/{__init__.py,base.py,dev.py,test.py}`, `manage.py`, `.env.example`, `.env`

- [ ] **Step 3.1: Wygenerować szkielet Wagtail w temp folderze, potem przenieść kluczowe pliki**

```bash
uv run wagtail start klastergoz_temp _tmp
```

Wagtail tworzy folder `_tmp/klastergoz_temp/` z domyślną strukturą. **Nie używamy jej bezpośrednio** — projekt ma niestandardowy layout z `apps/` i split settings.

- [ ] **Step 3.2: Stworzyć `manage.py` w roocie projektu**

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "klastergoz.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3.3: Stworzyć strukturę `klastergoz/`**

```bash
mkdir -p klastergoz/settings apps
touch klastergoz/__init__.py klastergoz/settings/__init__.py apps/__init__.py
```

- [ ] **Step 3.4: Stworzyć `klastergoz/settings/base.py`**

```python
"""Base settings shared across environments."""
import os
from pathlib import Path

import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv.load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    # local apps
    "apps.shared",
    "apps.home",
    # wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    # django
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "klastergoz.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "klastergoz.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{name}"}
    for name in [
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    ]
]

LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Wagtail-specific
WAGTAIL_SITE_NAME = "Klaster GOZ"
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8000")
WAGTAIL_I18N_ENABLED = False        # włączymy w Planie 6 (multilingual)
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}
WAGTAILDOCS_EXTENSIONS = ["pdf", "docx", "xlsx", "csv", "txt"]
```

- [ ] **Step 3.5: Stworzyć `klastergoz/settings/dev.py`**

```python
"""Development settings — local Docker Compose stack."""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
INSTALLED_APPS += ["wagtail.contrib.styleguide"]    # admin design system tool

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Wagtail rzecze: w dev wyłączamy cache strony, żeby zmiany w admin'ie były widoczne natychmiast.
CACHES["default"]["BACKEND"] = "django.core.cache.backends.dummy.DummyCache"
```

- [ ] **Step 3.6: Stworzyć `klastergoz/settings/test.py`**

```python
"""Test settings — SQLite in-memory dla szybkich testów."""
from .base import *

DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
CACHES["default"]["BACKEND"] = "django.core.cache.backends.dummy.DummyCache"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]   # fast hashing for tests
```

- [ ] **Step 3.7: Stworzyć `klastergoz/urls.py`**

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 3.8: Stworzyć `klastergoz/wsgi.py` i `klastergoz/asgi.py`**

```python
# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "klastergoz.settings.dev")
application = get_wsgi_application()
```

```python
# asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "klastergoz.settings.dev")
application = get_asgi_application()
```

- [ ] **Step 3.9: Stworzyć `.env.example` i `.env`**

`.env.example`:
```bash
DJANGO_SECRET_KEY=change-me-in-dev-or-set-strong-secret-in-prod
DB_NAME=klastergoz
DB_USER=klastergoz
DB_PASSWORD=klastergoz_dev_pass
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
WAGTAILADMIN_BASE_URL=http://localhost:8000
```

`.env` (kopia .env.example, dev values):
```bash
DJANGO_SECRET_KEY=dev-secret-key-not-for-prod-use-only
DB_NAME=klastergoz
DB_USER=klastergoz
DB_PASSWORD=klastergoz_dev_pass
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
WAGTAILADMIN_BASE_URL=http://localhost:8000
```

- [ ] **Step 3.10: Usunąć temp folder Wagtail starter**

```bash
rm -rf _tmp
```

- [ ] **Step 3.11: Sprawdzić, że Django potrafi się załadować**

```bash
uv run python manage.py check
```
Expected: `System check identified no issues (0 silenced).` (jeszcze bez DB).

- [ ] **Step 3.12: Commit**

```bash
git add manage.py klastergoz/ apps/__init__.py .env.example
git commit -m "feat: bootstrap Wagtail project with split settings"
```

---

## Task 4: Docker Compose dla dev (Postgres + Redis)

**Files:**
- Create: `docker-compose.dev.yml`, `.dockerignore`

- [ ] **Step 4.1: Stworzyć `docker-compose.dev.yml`**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - klastergoz_pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - klastergoz_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  klastergoz_pg_data:
  klastergoz_redis_data:
```

- [ ] **Step 4.2: Stworzyć `.dockerignore`**

```
.venv/
.git/
__pycache__/
*.pyc
.pytest_cache/
node_modules/
media/
staticfiles/
.env
*.md
```

- [ ] **Step 4.3: Uruchomić Postgres + Redis**

```bash
docker compose -f docker-compose.dev.yml up -d
```
Expected: 
```
[+] Running 3/3
 ✔ Network klastergoz_v2_default      Created
 ✔ Volume "klastergoz_v2_pg_data"     Created
 ✔ Container klastergoz_v2-db-1       Started
 ✔ Container klastergoz_v2-redis-1    Started
```

- [ ] **Step 4.4: Sprawdzić health serwisów**

```bash
docker compose -f docker-compose.dev.yml ps
```
Expected: oba serwisy ze statusem `healthy` (po ~10 sekundach).

- [ ] **Step 4.5: Wykonać migracje Django i sprawdzić połączenie z DB**

```bash
uv run python manage.py migrate
```
Expected: lista migracji do wykonania (auth, contenttypes, wagtailcore, etc.), wszystkie OK.

- [ ] **Step 4.6: Stworzyć superuser'a**

```bash
uv run python manage.py createsuperuser --username admin --email admin@klastergoz.pl
# password: admin (only dev)
```

- [ ] **Step 4.7: Uruchomić serwer i sprawdzić /admin**

```bash
uv run python manage.py runserver
```

W przeglądarce otworzyć http://localhost:8000/admin/, zalogować się jako admin.
Expected: Wagtail admin dashboard widoczny w języku polskim.

Zatrzymać serwer Ctrl+C.

- [ ] **Step 4.8: Commit**

```bash
git add docker-compose.dev.yml .dockerignore
git commit -m "feat: add Docker Compose stack for dev (Postgres + Redis)"
```

---

## Task 5: Import assets'ów z mockupu

**Files:**
- Create: `static/css/styles.css` (z `mockup/assets/styles.css`)
- Create: `static/img/logo.svg`, `static/img/logo-white.svg`
- Create: `static/js/home_slider.js`

- [ ] **Step 5.1: Skopiować mockupowe styles.css**

```bash
mkdir -p static/css static/img static/js
cp mockup/assets/styles.css static/css/styles.css
cp mockup/assets/logo.svg static/img/logo.svg
cp mockup/assets/logo-white.svg static/img/logo-white.svg
```

- [ ] **Step 5.2: Wyciągnąć JS slidera z mockup/index.html do osobnego pliku**

Stworzyć `static/js/home_slider.js`:

```javascript
// Hero slider z mockup/index.html — wyciągnięte z inline <script>
(function () {
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  const counter = document.getElementById('curSlide');
  const progress = document.querySelector('.slide-progress-bar');
  const pauseBtn = document.getElementById('pauseBtn');
  if (!slides.length) return;

  let idx = 0, timer = null, paused = false;
  const DURATION = 6000;

  function go(n, manual) {
    idx = (n + slides.length) % slides.length;
    slides.forEach((s, i) => s.classList.toggle('is-active', i === idx));
    dots.forEach((d, i) => d.classList.toggle('is-active', i === idx));
    counter.textContent = String(idx + 1).padStart(2, '0');
    progress.style.animation = 'none';
    progress.offsetHeight;
    if (!paused) progress.style.animation = `slideProgress ${DURATION}ms linear forwards`;
    if (manual) restart();
  }
  function tick() { go(idx + 1); }
  function start() { timer = setInterval(tick, DURATION); }
  function stop() { clearInterval(timer); }
  function restart() { stop(); if (!paused) start(); }

  document.querySelectorAll('[data-dir]').forEach(b =>
    b.addEventListener('click', () => go(idx + parseInt(b.dataset.dir, 10), true))
  );
  dots.forEach(d =>
    d.addEventListener('click', () => go(parseInt(d.dataset.go, 10), true))
  );
  if (pauseBtn) {
    pauseBtn.addEventListener('click', () => {
      paused = !paused;
      pauseBtn.classList.toggle('is-paused', paused);
      pauseBtn.innerHTML = paused
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20"></polygon></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>';
      if (paused) { stop(); progress.style.animationPlayState = 'paused'; }
      else { restart(); progress.style.animationPlayState = 'running'; }
    });
  }

  go(0);
  start();
})();
```

- [ ] **Step 5.3: Sprawdzić, że pliki istnieją**

```bash
ls -la static/css/styles.css static/img/logo.svg static/js/home_slider.js
```
Expected: wszystkie 3 pliki obecne.

- [ ] **Step 5.4: Wykonać collectstatic (sanity check)**

```bash
uv run python manage.py collectstatic --noinput --dry-run | tail -3
```
Expected: `N static files copied`, gdzie N > 0 (więc nasze pliki są widoczne).

- [ ] **Step 5.5: Commit**

```bash
git add static/
git commit -m "feat: import mockup styles, logos, and slider JS as static assets"
```

---

## Task 6: Base template + header/footer partials (statyczne)

**Files:**
- Create: `templates/base.html`, `templates/includes/header.html`, `templates/includes/footer.html`

- [ ] **Step 6.1: Stworzyć `templates/base.html`**

```html
{% load static wagtailuserbar %}
<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ page.title }}{% endblock %} — Klaster GOZ</title>
  <meta name="description" content="{% block meta_description %}{% endblock %}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/styles.css' %}">

  {% block extra_head %}{% endblock %}
</head>
<body data-page="{% block body_page %}{% endblock %}">

  {% wagtailuserbar %}

  {% include "includes/header.html" %}

  {% block content %}{% endblock %}

  {% include "includes/footer.html" %}

  {% block extra_scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 6.2: Stworzyć `templates/includes/header.html` (1:1 z mockupu, statyczne linki)**

Skopiować zawartość `mockup/assets/header.html` jako bazę. Zamienić ścieżki `https://klastergoz.pl/static/...` na `{% static '...' %}` i hard-coded linki na placeholder URL-e (`#` lub przyszłe path-y — działają, choć cele zwrócą 404 do Planu 3).

Kluczowa zmiana: zamiana `<img src="https://klastergoz.pl/static/assets/images/icons/header-text.svg">` na `<img src="{% static 'img/logo.svg' %}">`.

```html
{% load static %}
<!-- shared header — Plan 1: statyczne. Plan 7 zamienia na dynamiczne z Site Settings -->
<header class="site-header">
  <div class="utility">
    <div class="utility-inner">
      <div class="utility-left">
        <a href="tel:+48221234567" class="util-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.37 1.9.72 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.35 1.85.59 2.81.72A2 2 0 0 1 22 16.92Z"></path></svg>
          +48 22 123 45 67
        </a>
        <a href="mailto:biuro@klastergoz.pl" class="util-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2Z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
          biuro@klastergoz.pl
        </a>
      </div>
      <div class="utility-right">
        <div class="lang-switch">
          <button class="lang active" aria-pressed="true">PL</button>
          <button class="lang">EN</button>
        </div>
      </div>
    </div>
  </div>

  <nav class="nav">
    <a href="/" class="brand">
      <img src="{% static 'img/logo.svg' %}" alt="Klaster Gospodarki Cyrkularnej i Recyklingu — Krajowy Klaster Kluczowy" class="brand-logo">
    </a>

    <ul class="nav-list">
      <li><a href="/wydarzenia" data-nav="wydarzenia">Wydarzenia</a></li>
      <li><a href="/klaster" data-nav="klaster">Klaster</a></li>
      <li><a href="/edukacja" data-nav="edukacja">Edukacja</a></li>
      <li><a href="/doradztwo" data-nav="doradztwo">Doradztwo</a></li>
      <li><a href="/projekty" data-nav="projekty">Projekty</a></li>
      <li><a href="/kontakt" data-nav="kontakt">Kontakt</a></li>
    </ul>

    <div class="nav-right">
      <button class="icon-btn" aria-label="Szukaj">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      </button>
      <a href="#" class="btn btn--primary login-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        Strefa logowania
      </a>
      <button class="burger" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </nav>
</header>
```

> Uwaga: Plan 1 pomija mega-dropdown w nawigacji. Pojawi się w Planie 7 razem z dynamicznym menu sterowanym przez `NavigationSettings`.

- [ ] **Step 6.3: Stworzyć `templates/includes/footer.html` (uproszczone, statyczne)**

```html
{% load static %}
<!-- shared footer — Plan 1: statyczne. Plan 7 dynamizuje. -->
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a href="/" class="brand brand--footer">
          <img src="{% static 'img/logo-white.svg' %}" alt="Klaster GOZ" class="brand-logo brand-logo--footer">
        </a>
        <p style="color: rgba(255,255,255,0.65); font-size: 14.5px; margin-top: 18px; max-width: 320px;">
          Klaster Gospodarki Cyrkularnej i Recyklingu — od 2012 roku łączymy firmy, naukę i instytucje wokół transformacji cyrkularnej polskiego przemysłu.
        </p>
      </div>
      <div>
        <h4>Kontakt</h4>
        <ul>
          <li style="color: rgba(255,255,255,0.7);">ul. Przykładowa 12<br>00-001 Warszawa</li>
          <li><a href="mailto:biuro@klastergoz.pl">biuro@klastergoz.pl</a></li>
          <li><a href="tel:+48221234567">+48 22 123 45 67</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year"></span> Klaster Gospodarki Cyrkularnej i Recyklingu</span>
    </div>
  </div>
</footer>
<script>document.getElementById('year').textContent = new Date().getFullYear();</script>
```

- [ ] **Step 6.4: Commit**

```bash
git add templates/
git commit -m "feat: add base template, header, footer partials from mockup"
```

---

## Task 7: Snippet `Statistic`

**Files:**
- Create: `apps/shared/apps.py`, `apps/shared/models.py`
- Create: `apps/shared/tests/__init__.py`, `apps/shared/tests/test_snippets.py`

- [ ] **Step 7.1: Stworzyć `apps/shared/apps.py`**

```python
from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shared"
    verbose_name = "Współdzielone"
```

- [ ] **Step 7.2: Napisać failing test dla Statistic**

`apps/shared/tests/test_snippets.py`:

```python
import pytest
from apps.shared.models import Statistic


@pytest.mark.django_db
class TestStatistic:
    def test_can_create_statistic_with_required_fields(self):
        stat = Statistic.objects.create(
            value="150+",
            label="firm i instytucji członkowskich",
            group="home_strip",
            sort_order=1,
        )
        assert stat.pk is not None
        assert str(stat) == "150+ — firm i instytucji członkowskich"

    def test_statistics_ordered_by_sort_order(self):
        Statistic.objects.create(value="12", label="lat działalności", group="home_strip", sort_order=2)
        Statistic.objects.create(value="150+", label="firm", group="home_strip", sort_order=1)
        values = list(Statistic.objects.values_list("value", flat=True))
        assert values == ["150+", "12"]
```

- [ ] **Step 7.3: Uruchomić test, sprawdzić że failuje**

```bash
uv run pytest apps/shared/tests/test_snippets.py -v
```
Expected: ImportError / ModuleNotFoundError (modelu Statistic jeszcze nie ma).

- [ ] **Step 7.4: Stworzyć model Statistic w `apps/shared/models.py`**

```python
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Statistic(models.Model):
    """Pojedyncza statystyka do paska liczbowego lub sekcji 'liczby'.

    Group decyduje gdzie używamy: home_strip (4 liczby pod hero), home_section
    (sekcja stats dalej), about_klastra (na podstronie 'O klastrze').
    """

    GROUP_HOME_STRIP = "home_strip"
    GROUP_HOME_SECTION = "home_section"
    GROUP_ABOUT_KLASTRA = "about_klastra"
    GROUP_CHOICES = [
        (GROUP_HOME_STRIP, "Home — pasek pod hero"),
        (GROUP_HOME_SECTION, "Home — sekcja stats"),
        (GROUP_ABOUT_KLASTRA, "Strona 'O klastrze'"),
    ]

    value = models.CharField(
        max_length=32,
        help_text="Liczba z jednostką (np. '150+', '240 mln zł', '12').",
    )
    label = models.CharField(max_length=120, help_text="Opis poniżej liczby.")
    group = models.CharField(max_length=24, choices=GROUP_CHOICES)
    sort_order = models.PositiveSmallIntegerField(default=0)

    panels = [
        FieldPanel("value"),
        FieldPanel("label"),
        FieldPanel("group"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["group", "sort_order", "id"]
        verbose_name = "Statystyka"
        verbose_name_plural = "Statystyki"

    def __str__(self) -> str:
        return f"{self.value} — {self.label}"
```

- [ ] **Step 7.5: Wygenerować i wykonać migrację**

```bash
uv run python manage.py makemigrations shared
uv run python manage.py migrate
```
Expected: `Migrations for 'shared': 0001_initial.py`, potem `Applying shared.0001_initial... OK`.

- [ ] **Step 7.6: Uruchomić test ponownie, sprawdzić że pass'uje**

```bash
uv run pytest apps/shared/tests/test_snippets.py -v
```
Expected: 2 PASSED.

- [ ] **Step 7.7: Commit**

```bash
git add apps/shared/
git commit -m "feat(shared): add Statistic snippet"
```

---

## Task 8: Snippet `Pillar`

**Files:**
- Modify: `apps/shared/models.py`
- Modify: `apps/shared/tests/test_snippets.py`

- [ ] **Step 8.1: Dopisać failing test dla Pillar**

Dodać do `apps/shared/tests/test_snippets.py`:

```python
from apps.shared.models import Pillar


@pytest.mark.django_db
class TestPillar:
    def test_can_create_pillar_with_bullets(self):
        pillar = Pillar.objects.create(
            number="01 / FILAR",
            title="Klaster ogólnokrajowy",
            lead="Krajowy Klaster Kluczowy — platforma kooperacji 150+ firm.",
            bullets=["Członkostwo i networking", "Wspólne projekty B+R"],
            cta_label="Dołącz do klastra",
            color="green",
            sort_order=1,
        )
        assert pillar.pk is not None
        assert pillar.bullets == ["Członkostwo i networking", "Wspólne projekty B+R"]
        assert str(pillar) == "01 / FILAR — Klaster ogólnokrajowy"

    def test_pillars_ordered_by_sort_order(self):
        Pillar.objects.create(number="02", title="Drugi", lead="x", sort_order=2)
        Pillar.objects.create(number="01", title="Pierwszy", lead="x", sort_order=1)
        titles = list(Pillar.objects.values_list("title", flat=True))
        assert titles == ["Pierwszy", "Drugi"]
```

- [ ] **Step 8.2: Uruchomić test, sprawdzić że failuje**

```bash
uv run pytest apps/shared/tests/test_snippets.py::TestPillar -v
```
Expected: ImportError dla `Pillar`.

- [ ] **Step 8.3: Dopisać model Pillar w `apps/shared/models.py`**

Dodać po klasie `Statistic`:

```python
@register_snippet
class Pillar(models.Model):
    """Pojedynczy filar (Klaster / Edukacja / Doradztwo) wyświetlany na home."""

    COLOR_GREEN = "green"
    COLOR_DARK = "dark"
    COLOR_LIGHT = "light"
    COLOR_CHOICES = [
        (COLOR_GREEN, "Zielony (primary)"),
        (COLOR_DARK, "Ciemny"),
        (COLOR_LIGHT, "Jasny"),
    ]

    number = models.CharField(
        max_length=24,
        help_text="Numer/etykieta, np. '01 / FILAR'.",
    )
    title = models.CharField(max_length=120)
    lead = models.TextField(help_text="1–2 zdania opisu filaru.")
    bullets = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista 3–4 kluczowych usług/punktów (jeden ciąg na linię w admin'ie).",
    )
    cta_label = models.CharField(max_length=80, default="Sprawdź")
    cta_link = models.URLField(blank=True, help_text="Link docelowy filaru.")
    color = models.CharField(max_length=16, choices=COLOR_CHOICES, default=COLOR_GREEN)
    sort_order = models.PositiveSmallIntegerField(default=0)

    panels = [
        FieldPanel("number"),
        FieldPanel("title"),
        FieldPanel("lead"),
        FieldPanel("bullets"),
        FieldPanel("cta_label"),
        FieldPanel("cta_link"),
        FieldPanel("color"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Filar"
        verbose_name_plural = "Filary"

    def __str__(self) -> str:
        return f"{self.number} — {self.title}"
```

- [ ] **Step 8.4: Migracja**

```bash
uv run python manage.py makemigrations shared
uv run python manage.py migrate
```

- [ ] **Step 8.5: Test pass**

```bash
uv run pytest apps/shared/tests/test_snippets.py::TestPillar -v
```
Expected: 2 PASSED.

- [ ] **Step 8.6: Commit**

```bash
git add apps/shared/
git commit -m "feat(shared): add Pillar snippet"
```

---

## Task 9: Snippet `HeroSlide`

**Files:**
- Modify: `apps/shared/models.py`, `apps/shared/tests/test_snippets.py`

- [ ] **Step 9.1: Dopisać failing test dla HeroSlide**

Dodać do `apps/shared/tests/test_snippets.py`:

```python
from apps.shared.models import HeroSlide
from wagtail.images.tests.utils import get_test_image_file
from wagtail.images.models import Image


@pytest.mark.django_db
class TestHeroSlide:
    def test_can_create_hero_slide(self):
        img = Image.objects.create(title="Test", file=get_test_image_file())
        slide = HeroSlide.objects.create(
            image=img,
            eyebrow="Platforma KLASTERBOX",
            headline_html="Najnowsza<br>platforma <em>klasterbox</em>.",
            lead="Od ponad 10 lat wspólnie kreujemy nowoczesną organizację.",
            primary_cta_label="Wejdź do KLASTERBOX",
            primary_cta_url="/login?p=czlonek",
            secondary_cta_label="Poznaj klaster",
            secondary_cta_url="/o-klastrze",
            sort_order=1,
        )
        assert slide.pk is not None
        assert slide.is_active is True
        assert "klasterbox" in slide.headline_html

    def test_only_active_slides_returned_by_active_manager(self):
        img = Image.objects.create(title="Test", file=get_test_image_file())
        active = HeroSlide.objects.create(image=img, eyebrow="A", headline_html="H1", lead="L", sort_order=1)
        HeroSlide.objects.create(image=img, eyebrow="B", headline_html="H2", lead="L", sort_order=2, is_active=False)
        assert list(HeroSlide.objects.active()) == [active]
```

- [ ] **Step 9.2: Sprawdzić, że failuje**

```bash
uv run pytest apps/shared/tests/test_snippets.py::TestHeroSlide -v
```
Expected: ImportError dla `HeroSlide`.

- [ ] **Step 9.3: Dopisać model HeroSlide**

Dodać do `apps/shared/models.py` (na końcu):

```python
class HeroSlideQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


@register_snippet
class HeroSlide(models.Model):
    """Pojedynczy slajd hero-slidera na home.

    Headline_html celowo nie sanitizujemy — redaktor wie, że może użyć <br> i <em>
    dla emfazy. Wagtail dostarcza warning'a w admin panel'u, jeśli redaktor wprowadzi
    coś dziwnego.
    """

    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        help_text="Tło slajdu. Min. 1920×1080, zalecane WebP/JPEG.",
    )
    eyebrow = models.CharField(
        max_length=80,
        help_text="Krótki tekst nad headline'em, np. 'Platforma KLASTERBOX'.",
    )
    headline_html = models.CharField(
        max_length=400,
        help_text="Główny nagłówek — dozwolone <br> i <em>.",
    )
    lead = models.TextField(help_text="Krótki opis pod nagłówkiem (1–2 zdania).")
    primary_cta_label = models.CharField(max_length=60, blank=True)
    primary_cta_url = models.CharField(max_length=255, blank=True)
    secondary_cta_label = models.CharField(max_length=60, blank=True)
    secondary_cta_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True, help_text="Odznacz, by ukryć slajd bez kasowania.")
    sort_order = models.PositiveSmallIntegerField(default=0)

    objects = HeroSlideQuerySet.as_manager()

    panels = [
        FieldPanel("image"),
        FieldPanel("eyebrow"),
        FieldPanel("headline_html"),
        FieldPanel("lead"),
        FieldPanel("primary_cta_label"),
        FieldPanel("primary_cta_url"),
        FieldPanel("secondary_cta_label"),
        FieldPanel("secondary_cta_url"),
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Slajd hero"
        verbose_name_plural = "Slajdy hero"

    def __str__(self) -> str:
        return f"Hero: {self.eyebrow}"
```

- [ ] **Step 9.4: Migracja**

```bash
uv run python manage.py makemigrations shared
uv run python manage.py migrate
```

- [ ] **Step 9.5: Test pass**

```bash
uv run pytest apps/shared/tests/test_snippets.py -v
```
Expected: 6 PASSED (2 statistic + 2 pillar + 2 hero).

- [ ] **Step 9.6: Commit**

```bash
git add apps/shared/
git commit -m "feat(shared): add HeroSlide snippet with active manager"
```

---

## Task 10: Model `HomePage` (Wagtail Page) z polami strukturalnymi

**Files:**
- Create: `apps/home/apps.py`, `apps/home/models.py`
- Create: `apps/home/tests/__init__.py`, `apps/home/tests/test_models.py`

- [ ] **Step 10.1: Stworzyć `apps/home/apps.py`**

```python
from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.home"
    verbose_name = "Strona główna"
```

- [ ] **Step 10.2: Napisać failing test dla HomePage**

`apps/home/tests/__init__.py`: pusty.

`apps/home/tests/test_models.py`:

```python
import pytest
from wagtail.models import Page, Site

from apps.home.models import HomePage


@pytest.mark.django_db
class TestHomePage:
    def test_can_create_home_page_under_root(self):
        root = Page.objects.get(depth=1)
        home = HomePage(
            title="Strona główna",
            slug="home",
            hero_intro="Najnowsza platforma KLASTERBOX.",
            pillars_eyebrow="Co robimy",
            pillars_heading="Trzy filary GOZ.",
            pillars_lead="Trzy filary, jedna misja.",
            consult_eyebrow="Bezpłatna konsultacja",
            consult_heading="Nie wiesz, od czego zacząć?",
            consult_steps=["Rozmowa diagnostyczna", "Rekomendacja ścieżki", "Źródła finansowania"],
            services_eyebrow="Usługi klastra",
            services_heading="Pełen portfel narzędzi.",
            members_eyebrow="Zaufali nam",
            members_heading="Wybrane firmy członkowskie",
            about_eyebrow="O klastrze",
            about_heading="Zaplecze surowcowe dla polskiego przemysłu.",
            news_eyebrow="Aktualności",
            news_heading="Co dzieje się w cyrkularnej Polsce.",
            cta_strip_heading="Wzmocnij konkurencyjność firmy.",
            cta_strip_lead="Dołącz do 150+ partnerów.",
        )
        root.add_child(instance=home)
        assert home.pk is not None
        assert home.url_path == "/home/"
        assert home.consult_steps == ["Rozmowa diagnostyczna", "Rekomendacja ścieżki", "Źródła finansowania"]

    def test_home_page_template_path(self):
        assert HomePage.template == "home/home_page.html"
```

- [ ] **Step 10.3: Test failuje**

```bash
uv run pytest apps/home/tests/test_models.py -v
```
Expected: ImportError dla `HomePage`.

- [ ] **Step 10.4: Stworzyć `apps/home/models.py`**

```python
from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """Strona główna klastergoz.pl.

    Wszystkie sekcje sterowane przez strukturalne pola — żaden StreamField.
    Redaktor edytuje treść przez Wagtail admin, układ jest sztywno przewidywalny.

    Slajdy hero, filary, statystyki, członkowie — wybierane przez M2M chooser
    do snippetów (HeroSlide, Pillar, Statistic, Member). Nadrzędne pola tekstowe
    (eyebrow / heading / lead) są bezpośrednio na HomePage.
    """

    # SEKCJA: hero slider
    hero_intro = models.TextField(
        blank=True,
        help_text="Krótki tekst pomocniczy (jeśli potrzeba) — większość treści w HeroSlide snippetach.",
    )
    hero_slides = ParentalManyToManyField(
        "shared.HeroSlide",
        blank=True,
        related_name="+",
        help_text="Slajdy w sliderze hero.",
    )

    # SEKCJA: pasek statystyk (4 liczby pod hero)
    stats_strip = ParentalManyToManyField(
        "shared.Statistic",
        blank=True,
        related_name="home_strip",
        help_text="4 statystyki w pasku tuż pod hero. Filtruj po group=home_strip.",
    )

    # SEKCJA: filary
    pillars_eyebrow = models.CharField(max_length=60, default="Co robimy")
    pillars_heading = models.CharField(max_length=200, help_text="Główny nagłówek sekcji filarów.")
    pillars_lead = models.TextField(help_text="Lead pod nagłówkiem sekcji filarów.")
    pillars = ParentalManyToManyField(
        "shared.Pillar",
        blank=True,
        related_name="+",
        help_text="3 filary do wyświetlenia.",
    )

    # SEKCJA: konsultacja CTA
    consult_eyebrow = models.CharField(max_length=60, default="Bezpłatna konsultacja")
    consult_heading = models.CharField(max_length=200)
    consult_lead = models.TextField(blank=True)
    consult_steps = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista 3 kroków konsultacji.",
    )

    # SEKCJA: stats secondary (4 liczby pod konsultacją)
    stats_secondary = ParentalManyToManyField(
        "shared.Statistic",
        blank=True,
        related_name="home_section",
        help_text="4 statystyki w sekcji 'Liczby'. Filtruj po group=home_section.",
    )

    # SEKCJA: usługi (kafelki)
    services_eyebrow = models.CharField(max_length=60, default="Usługi klastra")
    services_heading = models.CharField(max_length=200)
    services_lead = models.TextField(blank=True)
    # Listę faktycznych ServicePage Plan 3 doda jako auto-listing.

    # SEKCJA: członkowie (logosy)
    members_eyebrow = models.CharField(max_length=60, default="Zaufali nam")
    members_heading = models.CharField(max_length=200)

    # SEKCJA: o klastrze (feature)
    about_eyebrow = models.CharField(max_length=60, default="O klastrze")
    about_heading = models.CharField(max_length=200)
    about_lead = RichTextField(features=["bold", "italic", "link"], blank=True)
    about_bullets = models.JSONField(default=list, blank=True)

    # SEKCJA: aktualności
    news_eyebrow = models.CharField(max_length=60, default="Aktualności")
    news_heading = models.CharField(max_length=200)
    # Listę 3 najnowszych ArticlePage Plan 6 doda jako auto-fetch.

    # SEKCJA: CTA strip (na dole)
    cta_strip_heading = models.CharField(max_length=200)
    cta_strip_lead = models.TextField(blank=True)

    template = "home/home_page.html"
    max_count = 1   # tylko jedna strona główna w site'cie

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_intro"),
                FieldPanel("hero_slides"),
            ],
            heading="Hero slider",
        ),
        MultiFieldPanel(
            [FieldPanel("stats_strip")],
            heading="Pasek statystyk pod hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("pillars_eyebrow"),
                FieldPanel("pillars_heading"),
                FieldPanel("pillars_lead"),
                FieldPanel("pillars"),
            ],
            heading="Sekcja filarów",
        ),
        MultiFieldPanel(
            [
                FieldPanel("consult_eyebrow"),
                FieldPanel("consult_heading"),
                FieldPanel("consult_lead"),
                FieldPanel("consult_steps"),
            ],
            heading="Sekcja konsultacji",
        ),
        MultiFieldPanel(
            [FieldPanel("stats_secondary")],
            heading="Sekcja 'Liczby'",
        ),
        MultiFieldPanel(
            [
                FieldPanel("services_eyebrow"),
                FieldPanel("services_heading"),
                FieldPanel("services_lead"),
            ],
            heading="Sekcja usług",
        ),
        MultiFieldPanel(
            [
                FieldPanel("members_eyebrow"),
                FieldPanel("members_heading"),
            ],
            heading="Sekcja członków",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_eyebrow"),
                FieldPanel("about_heading"),
                FieldPanel("about_lead"),
                FieldPanel("about_bullets"),
            ],
            heading="Sekcja 'O klastrze'",
        ),
        MultiFieldPanel(
            [
                FieldPanel("news_eyebrow"),
                FieldPanel("news_heading"),
            ],
            heading="Sekcja aktualności",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_strip_heading"),
                FieldPanel("cta_strip_lead"),
            ],
            heading="CTA strip (dolny)",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx["hero_slides_active"] = self.hero_slides.filter(is_active=True).order_by("sort_order")
        ctx["pillars_ordered"] = self.pillars.order_by("sort_order")
        ctx["stats_strip_ordered"] = self.stats_strip.order_by("sort_order")
        ctx["stats_secondary_ordered"] = self.stats_secondary.order_by("sort_order")
        return ctx
```

- [ ] **Step 10.5: Dodać `apps.home` do INSTALLED_APPS — sprawdzić, że już jest**

Już dodane w base.py w Task 3. Sprawdzić:

```bash
grep "apps.home" klastergoz/settings/base.py
```
Expected: `    "apps.home",`

- [ ] **Step 10.6: Migracja**

```bash
uv run python manage.py makemigrations home
uv run python manage.py migrate
```

- [ ] **Step 10.7: Test pass**

```bash
uv run pytest apps/home/tests/test_models.py -v
```
Expected: 2 PASSED.

- [ ] **Step 10.8: Stworzyć management command `setup_initial_site`**

Po świeżych migracjach Wagtail trzyma default "Welcome" page jako site root. Trzeba ją zastąpić naszym HomePage. Robimy to przez idempotentny management command (nie przez data migration — czystsza Wagtail API).

```bash
mkdir -p apps/home/management/commands
touch apps/home/management/__init__.py apps/home/management/commands/__init__.py
```

Stworzyć `apps/home/management/commands/setup_initial_site.py`:

```python
"""One-time setup: replace Wagtail's default Welcome page with HomePage as site root."""
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.home.models import HomePage


class Command(BaseCommand):
    help = "Set up initial site: create HomePage and configure it as default site root."

    def handle(self, *args, **options):
        if HomePage.objects.exists():
            self.stdout.write(self.style.WARNING("HomePage already exists — skipping setup."))
            return

        root = Page.objects.get(depth=1)

        # Usuń default Welcome page (slug='home', depth=2) jeśli istnieje
        default_welcome = Page.objects.filter(slug="home", depth=2).first()
        if default_welcome:
            self.stdout.write(f"Removing default Wagtail Welcome page: {default_welcome.title}")
            default_welcome.delete()

        # Stwórz HomePage z domyślnymi wartościami
        homepage = HomePage(
            title="Klaster GOZ",
            slug="home",
            pillars_heading="Trzy filary GOZ.",
            pillars_lead="Każdy filar to osobna ścieżka wsparcia.",
            consult_heading="Nie wiesz, od czego zacząć cyrkularną transformację?",
            consult_lead="Umów 30 min spotkanie z ekspertem klastra.",
            consult_steps=[
                "Rozmowa diagnostyczna — gdzie jesteś w transformacji",
                "Rekomendacja konkretnej ścieżki w klastrze",
                "Konkretne źródła finansowania transformacji",
            ],
            services_heading="Pełen portfel narzędzi transformacji cyrkularnej.",
            members_heading="Wybrane firmy i instytucje członkowskie",
            about_heading="Zaplecze surowcowe dla polskiego przemysłu.",
            news_heading="Co dzieje się w cyrkularnej Polsce.",
            cta_strip_heading="Wzmocnij konkurencyjność firmy w sieci 150+ partnerów.",
            cta_strip_lead="Dołącz do społeczności, która od 12 lat realnie wpływa na cyrkularną transformację.",
        )
        root.add_child(instance=homepage)
        homepage.save_revision().publish()

        # Ustaw HomePage jako root domyślnej witryny
        default_site = Site.objects.filter(is_default_site=True).first()
        if default_site:
            default_site.root_page = homepage
            default_site.hostname = "localhost"
            default_site.port = 8000
            default_site.save()
            self.stdout.write(f"Updated default site root to: {homepage.title}")
        else:
            Site.objects.create(
                hostname="localhost",
                port=8000,
                is_default_site=True,
                root_page=homepage,
            )
            self.stdout.write(f"Created default site with root: {homepage.title}")

        self.stdout.write(self.style.SUCCESS(f"✓ HomePage created and configured: {homepage.url}"))
```

- [ ] **Step 10.9: Uruchomić command i sprawdzić efekt**

```bash
uv run python manage.py setup_initial_site
```
Expected: `✓ HomePage created and configured: /` (lub podobne).

Kolejne uruchomienie (idempotencja):
```bash
uv run python manage.py setup_initial_site
```
Expected: `HomePage already exists — skipping setup.`

- [ ] **Step 10.10: Napisać test dla command'a**

Dodać do `apps/home/tests/test_models.py`:

```python
from django.core.management import call_command
from wagtail.models import Site


@pytest.mark.django_db
class TestSetupInitialSiteCommand:
    def test_command_creates_homepage_and_sets_as_root(self):
        call_command("setup_initial_site")

        assert HomePage.objects.count() == 1
        homepage = HomePage.objects.first()
        default_site = Site.objects.filter(is_default_site=True).first()
        assert default_site.root_page_id == homepage.pk

    def test_command_is_idempotent(self):
        call_command("setup_initial_site")
        call_command("setup_initial_site")    # drugie uruchomienie nie powinno failować
        assert HomePage.objects.count() == 1
```

- [ ] **Step 10.11: Test pass**

```bash
uv run pytest apps/home/tests/test_models.py -v
```
Expected: 4 PASSED.

- [ ] **Step 10.12: Commit**

```bash
git add apps/home/
git commit -m "feat(home): add HomePage model + setup_initial_site management command"
```

---

## Task 11: Template `home_page.html` — odzwierciedlenie mockupu

**Files:**
- Create: `templates/home/home_page.html`
- Create: `apps/home/tests/test_views.py`

- [ ] **Step 11.1: Stworzyć failing test renderingu**

`apps/home/tests/test_views.py`:

```python
import pytest
from django.test import Client
from wagtail.models import Page, Site

from apps.home.models import HomePage


@pytest.fixture
@pytest.mark.django_db
def home_page(db):
    """Stworzony HomePage osadzony pod root'em jako default site root_page."""
    root = Page.objects.get(depth=1)
    home = HomePage(
        title="Klaster GOZ",
        slug="home",
        pillars_heading="Trzy filary",
        pillars_lead="Każdy filar to osobna ścieżka wsparcia.",
        consult_heading="Bezpłatna konsultacja",
        services_heading="Usługi klastra",
        members_heading="Wybrane firmy",
        about_heading="O klastrze",
        news_heading="Aktualności",
        cta_strip_heading="Dołącz do klastra",
    )
    root.add_child(instance=home)

    site = Site.objects.first()
    site.root_page = home
    site.save()
    return home


@pytest.mark.django_db
def test_home_page_returns_200(client: Client, home_page: HomePage):
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_page_renders_pillars_heading(client: Client, home_page: HomePage):
    response = client.get("/")
    assert b"Trzy filary" in response.content


@pytest.mark.django_db
def test_home_page_renders_consult_section(client: Client, home_page: HomePage):
    response = client.get("/")
    assert b"Bezpłatna konsultacja" in response.content


@pytest.mark.django_db
def test_home_page_includes_styles_css(client: Client, home_page: HomePage):
    response = client.get("/")
    assert b'styles.css' in response.content
```

- [ ] **Step 11.2: Test failuje**

```bash
uv run pytest apps/home/tests/test_views.py -v
```
Expected: TemplateDoesNotExist: home/home_page.html.

- [ ] **Step 11.3: Stworzyć `templates/home/home_page.html`**

Bazuj na `mockup/index.html`, ale:
1. Wszystkie sekcje przekształcone na Django template syntax
2. Wartości statyczne w mockupie zastąpione `{{ page.X }}` lub `{% for %}`
3. Slider JS przeniesiony z inline `<script>` na `<script src="{% static 'js/home_slider.js' %}">`
4. Sekcja "Usługi klastra" — w Planie 1 jeszcze hardcoded (Plan 3 doda model ServicePage)
5. Sekcja "Aktualności" — hardcoded placeholder (Plan 6 doda ArticlePage)

```html
{% extends "base.html" %}
{% load static wagtailimages_tags %}

{% block body_page %}home{% endblock %}

{% block content %}
<section class="hero-slider" id="heroSlider">
  <div class="slider-track">
    {% for slide in hero_slides_active %}
      <article class="slide {% if forloop.first %}is-active{% endif %}" data-slide="{{ forloop.counter0 }}">
        {% image slide.image fill-1920x1080 as slide_img %}
        <div class="slide-bg" style="background-image: url('{{ slide_img.url }}');"></div>
        <div class="slide-overlay"></div>
        <div class="container slide-inner">
          <span class="eyebrow" style="color: var(--lime-300);">{{ slide.eyebrow }}</span>
          <h1>{{ slide.headline_html|safe }}</h1>
          <p class="hero-lead">{{ slide.lead }}</p>
          <div class="hero-ctas">
            {% if slide.primary_cta_label %}
              <a href="{{ slide.primary_cta_url }}" class="btn btn--accent">{{ slide.primary_cta_label }} <span class="arr">→</span></a>
            {% endif %}
            {% if slide.secondary_cta_label %}
              <a href="{{ slide.secondary_cta_url }}" class="btn btn--light">{{ slide.secondary_cta_label }}</a>
            {% endif %}
          </div>
        </div>
      </article>
    {% endfor %}
  </div>

  <div class="slider-nav container">
    <div class="slider-meta">
      <span class="slide-counter"><span id="curSlide">01</span><span class="of">/</span><span>{{ hero_slides_active.count|stringformat:"02d" }}</span></span>
      <span class="slide-progress"><span class="slide-progress-bar"></span></span>
    </div>
    <div class="slider-controls">
      <button class="slider-btn" data-dir="-1" aria-label="Poprzedni">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
      </button>
      <button class="slider-btn slider-btn--pause" id="pauseBtn" aria-label="Pauza">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
      </button>
      <button class="slider-btn" data-dir="1" aria-label="Następny">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
      </button>
    </div>
    <div class="slider-dots">
      {% for slide in hero_slides_active %}
        <button class="dot {% if forloop.first %}is-active{% endif %}" data-go="{{ forloop.counter0 }}" aria-label="Slajd {{ forloop.counter }}"></button>
      {% endfor %}
    </div>
  </div>
</section>

<section class="hero-stats-strip">
  <div class="container">
    {% for stat in stats_strip_ordered %}
      <div class="hsm"><strong>{{ stat.value }}</strong><span>{{ stat.label }}</span></div>
    {% endfor %}
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="pillars-head">
      <div>
        <span class="eyebrow">{{ page.pillars_eyebrow }}</span>
        <h2 style="margin-top: 14px;">{{ page.pillars_heading }}</h2>
      </div>
      <p class="lead muted">{{ page.pillars_lead }}</p>
    </div>

    <div class="pillars-grid">
      {% for pillar in pillars_ordered %}
        <a href="{{ pillar.cta_link|default:'#' }}" class="pillar {% if pillar.color == 'dark' %}pillar--dark{% endif %}">
          <span class="num">{{ pillar.number }}</span>
          <span class="ico"></span>{# Plan 3 dorzuci ikonę z FK do snippeta ikon #}
          <h3>{{ pillar.title }}</h3>
          <p>{{ pillar.lead }}</p>
          <ul>
            {% for bullet in pillar.bullets %}
              <li>{{ bullet }}</li>
            {% endfor %}
          </ul>
          <span class="pill-link">{{ pillar.cta_label }}</span>
        </a>
      {% endfor %}
    </div>
  </div>
</section>

<section class="section bg-green">
  <div class="container consult">
    <div>
      <span class="eyebrow">{{ page.consult_eyebrow }}</span>
      <h2 style="margin-top: 14px;">{{ page.consult_heading }}</h2>
      <p class="lead muted" style="max-width: 520px;">{{ page.consult_lead }}</p>
      <ul style="list-style: none; padding: 0; margin: 28px 0 0; display: grid; gap: 12px;">
        {% for step in page.consult_steps %}
          <li style="display: flex; gap: 12px; align-items: center; font-size: 15px;">
            <span style="width: 28px; height: 28px; background: var(--green-700); color: #fff; border-radius: 50%; display: grid; place-items: center; font-weight: 700; font-size: 13px;">{{ forloop.counter }}</span>
            {{ step }}
          </li>
        {% endfor %}
      </ul>
    </div>
    {# Formularz konsultacji — placeholder. Plan 5 podłączy ConsultationRequest model. #}
    <div class="consult-form">
      <h3>Bezpłatna konsultacja</h3>
      <p class="muted">Formularz pojawi się w Planie 5 (Forms + integracje).</p>
    </div>
  </div>
</section>

<section class="section--tight">
  <div class="container">
    <div class="stats">
      {% for stat in stats_secondary_ordered %}
        <div class="stat-item"><strong>{{ stat.value }}</strong><span>{{ stat.label }}</span></div>
      {% endfor %}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <span class="eyebrow">{{ page.services_eyebrow }}</span>
        <h2 style="margin-top: 14px;">{{ page.services_heading }}</h2>
      </div>
    </div>
    <p class="muted">Lista 6 usług — placeholder. Plan 3 doda ServicePage i auto-listing.</p>
  </div>
</section>

<section class="section--tight">
  <div class="container">
    <div style="text-align: center; margin-bottom: 36px;">
      <span class="eyebrow">{{ page.members_eyebrow }}</span>
      <h3 style="margin-top: 12px; font-size: 24px; max-width: 720px; margin-left: auto; margin-right: auto;">{{ page.members_heading }}</h3>
    </div>
    <p class="muted">Logosy członków — placeholder. Plan 3 doda Member snippets.</p>
  </div>
</section>

<section class="section">
  <div class="container feature feature--reverse">
    <div class="feature-text">
      <span class="eyebrow">{{ page.about_eyebrow }}</span>
      <h2 style="margin-top: 14px;">{{ page.about_heading }}</h2>
      <div class="lead muted">{{ page.about_lead|safe }}</div>
      <ul>
        {% for bullet in page.about_bullets %}
          <li>{{ bullet }}</li>
        {% endfor %}
      </ul>
    </div>
    <div class="feature-img"><span>Zdjęcie / wideo — Plan 3 podłączy</span></div>
  </div>
</section>

<section class="section bg-green">
  <div class="container">
    <div class="section-head">
      <div>
        <span class="eyebrow">{{ page.news_eyebrow }}</span>
        <h2 style="margin-top: 14px;">{{ page.news_heading }}</h2>
      </div>
    </div>
    <p class="muted">3 najnowsze artykuły — placeholder. Plan 6 doda auto-listing.</p>
  </div>
</section>

<section class="section--tight">
  <div class="container">
    <div class="cta-strip">
      <div>
        <h2 style="margin-top: 14px;">{{ page.cta_strip_heading }}</h2>
        <p>{{ page.cta_strip_lead }}</p>
      </div>
    </div>
  </div>
</section>
{% endblock %}

{% block extra_scripts %}
  <script src="{% static 'js/home_slider.js' %}"></script>
{% endblock %}
```

- [ ] **Step 11.4: Test pass**

```bash
uv run pytest apps/home/tests/test_views.py -v
```
Expected: 4 PASSED.

- [ ] **Step 11.5: Sanity check — uruchomić runserver i sprawdzić w przeglądarce**

(Zakładamy, że `setup_initial_site` z Task 10.9 już zostało uruchomione — HomePage istnieje, jest root'em strony.)

```bash
uv run python manage.py runserver
```

W przeglądarce:
1. http://localhost:8000/ — strona ładuje się z placeholderowymi treściami z command'a (heading'i widoczne, ale brak hero slajdów / filarów / statystyk bo jeszcze nie istnieją)
2. http://localhost:8000/admin/ — zalogować się
3. Snippety → "Slajdy hero" → stwórz 3 instancje (z upload obrazów)
4. Snippety → "Filary" → stwórz 3 instancje (color: green / dark / green; sort_order 1/2/3; wypełnione bullets)
5. Snippety → "Statystyki" → stwórz 4 instancje z group="home_strip" + 4 z group="home_section"
6. Pages → Klaster GOZ (HomePage) → Edit → wybierz hero_slides, pillars, stats_strip, stats_secondary → Publish
7. http://localhost:8000/ — odświeżyć, sprawdzić że strona renderuje wszystkie wprowadzone treści

Expected: Strona wygląda jak `mockup/index.html` z hero-sliderem (3 slajdy), paskiem statystyk, sekcją filarów (3 karty), sekcją konsultacji, statsami, placeholderami dla usług / członków / aktualności, sekcją "O klastrze" i CTA strip.

Zatrzymać serwer.

- [ ] **Step 11.6: Commit**

```bash
git add templates/home/ apps/home/tests/
git commit -m "feat(home): add home_page template rendering structured fields and snippets"
```

---

## Task 12: Pytest config + conftest + smoke testy

**Files:**
- Create: `conftest.py`, `pytest.ini`

- [ ] **Step 12.1: Stworzyć `pytest.ini` (alternatywa: zostawić w pyproject.toml — Task 2 już dodał `[tool.pytest.ini_options]`)**

Sekcja `[tool.pytest.ini_options]` w pyproject.toml już jest. Sprawdzić:

```bash
grep -A 4 "pytest.ini_options" pyproject.toml
```
Expected: blok obecny.

- [ ] **Step 12.2: Stworzyć `conftest.py` w roocie**

```python
"""Pytest fixtures dostępne globalnie."""
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    user = User.objects.create_superuser(
        username="admin", email="admin@klastergoz.pl", password="admin"
    )
    return user


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client
```

- [ ] **Step 12.3: Uruchomić cały test suite**

```bash
uv run pytest -v
```
Expected: All tests PASSED (6 z apps/shared + 8 z apps/home = 14 total).

- [ ] **Step 12.4: Sprawdzić coverage**

```bash
uv run pytest --cov=apps --cov-report=term-missing
```
Expected: coverage report z aktualnymi statystykami (>70% dla `apps/shared/models.py` i `apps/home/models.py`).

- [ ] **Step 12.5: Commit**

```bash
git add conftest.py
git commit -m "test: add root conftest with admin user fixtures"
```

---

## Task 13: Linting i formatowanie (ruff + black + pre-commit)

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 13.1: Stworzyć `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: mixed-line-ending
        args: ["--fix=lf"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.4
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black

  - repo: local
    hooks:
      - id: django-check
        name: Django system check
        entry: uv run python manage.py check
        language: system
        pass_filenames: false
        files: \.py$
```

- [ ] **Step 13.2: Zainstalować i uruchomić pre-commit**

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
Expected: Wszystkie hooki passują (poza ewentualnymi auto-fixami trailing whitespace itp., które są applied — uruchomić ponownie żeby zobaczyć pass).

- [ ] **Step 13.3: Uruchomić ruff i black manualnie**

```bash
uv run ruff check .
uv run black --check .
```
Expected: No issues / All files formatted.

- [ ] **Step 13.4: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: add pre-commit hooks (ruff, black, hygiene checks)"
```

---

## Task 14: Aktualizacja README z workflow dewelopera

**Files:**
- Modify: `README.md`

- [ ] **Step 14.1: Rozszerzyć README**

```markdown
# Klaster GOZ — portal

Portal marketingowy `klastergoz.pl` zarządzany przez Wagtail CMS.

## Stack

- Wagtail 6 / Django 5 / Python 3.12+
- PostgreSQL 16 / Redis 7 (Docker Compose w dev)
- pytest-django + ruff + black + pre-commit

## Setup (dev)

Wymagane: Python 3.12+, uv, Docker Desktop.

```bash
# 1. Sklonować repo
git clone <repo-url> klastergoz
cd klastergoz

# 2. Skopiować env, zainstalować dependencies
cp .env.example .env
uv sync

# 3. Wystartować Postgres + Redis
docker compose -f docker-compose.dev.yml up -d

# 4. Migracje, setup początkowej strony, superuser
uv run python manage.py migrate
uv run python manage.py setup_initial_site
uv run python manage.py createsuperuser

# 5. Pre-commit hooks
uv run pre-commit install

# 6. Run dev server
uv run python manage.py runserver
```

- Strona: http://localhost:8000
- Wagtail admin: http://localhost:8000/admin

## Testy

```bash
uv run pytest                          # cały suite
uv run pytest apps/home -v             # tylko jedna app
uv run pytest --cov=apps               # z coverage
```

## Linting

```bash
uv run ruff check .                    # lint
uv run ruff check . --fix              # lint + auto-fix
uv run black .                         # format
uv run pre-commit run --all-files      # wszystko naraz
```

## Struktura projektu

```
klastergoz/                  # Django project (settings, urls, wsgi)
apps/
  ├── shared/                # snippety reużywalne (HeroSlide, Pillar, Statistic, ...)
  └── home/                  # HomePage Page model + tests
templates/                   # Django templates (base, includes, home, ...)
static/                      # CSS / JS / images z mockupu
docs/
  ├── specs/                 # design docs
  └── plans/                 # implementation plans
```

## Dokumentacja projektu

- Spec: `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md`
- Plany: `docs/superpowers/plans/`

## Wagtail admin po polsku

Locale `pl` ustawione w `settings/base.py`. Wagtail wykrywa preferencję przeglądarki + Accept-Language.

## Kolejne plany

Plan 2 (Deployment) — Hetzner + Caddy + GitHub Actions deploy + staging.
Plan 3 (Content architecture) — pozostałe page types + snippety + site settings.
```

- [ ] **Step 14.2: Commit**

```bash
git add README.md
git commit -m "docs: expand README with dev workflow, testing, linting commands"
```

---

## Task 15: Końcowa weryfikacja całego Planu 1

**Files:**
- Modify: brak (smoke test pełnego flow)

- [ ] **Step 15.1: Pełen test suite**

```bash
uv run pytest -v
```
Expected: 14 PASSED, 0 FAILED.

- [ ] **Step 15.2: Pełen check lintera**

```bash
uv run pre-commit run --all-files
```
Expected: All hooks PASS.

- [ ] **Step 15.3: Smoke test — start od zera**

Z czystego stanu (zatrzymane kontenery, no media):

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
# czekać aż db healthy: docker compose -f docker-compose.dev.yml ps
uv run python manage.py migrate
uv run python manage.py setup_initial_site
DJANGO_SUPERUSER_PASSWORD=admin uv run python manage.py createsuperuser \
    --username admin --email admin@klastergoz.pl --noinput
uv run python manage.py runserver
```

W przeglądarce:
1. http://localhost:8000/ — strona renderuje się z placeholderowymi headinami (HomePage utworzony przez `setup_initial_site`)
2. http://localhost:8000/admin/ — login admin/admin
3. Wypełnić sekcje przez snippety (jak w 11.5)
4. Odświeżyć http://localhost:8000/ — pełna strona z treścią

Expected: end-to-end działa bez modyfikacji kodu po setup'cie.

- [ ] **Step 15.4: Tag wersji**

```bash
git tag -a v0.1.0-foundation -m "Plan 1 complete: Walking skeleton with HomePage"
```

- [ ] **Step 15.5: Aktualizacja todo / odznaczenie Planu 1 w spec'u (opcjonalne)**

Jeśli prowadzi się ogólne TODO projektu w repo (np. `TODO.md` lub GitHub issues) — odznaczyć Plan 1 jako completed.

---

## Definition of Done dla Planu 1

- [x] Wagtail project działa lokalnie pod http://localhost:8000
- [x] Wagtail admin po polsku, dostępny pod /admin
- [x] HomePage edytowalny w admin'ie z wszystkimi sekcjami strukturalnymi
- [x] Snippety HeroSlide / Pillar / Statistic edytowalne, używane przez HomePage M2M
- [x] Strona główna renderuje się 1:1 z mockupowymi stylami
- [x] Wszystkie testy pass (`uv run pytest`)
- [x] Pre-commit hooki działają, kod sformatowany
- [x] README dokumentuje setup + workflow
- [x] Repo zawiera tag `v0.1.0-foundation`

## Co się otwiera po Planie 1

- Plan 2 może deployować to do staging (mamy działający Wagtail + Docker)
- Plan 3 może dorzucać kolejne page types pod tę samą strukturę
- Plan 4 może bezpośrednio kopiować mockupowe templates dla nowych sekcji
- Plan 5+ rozbudowuje funkcjonalność bez ruszania bazy
