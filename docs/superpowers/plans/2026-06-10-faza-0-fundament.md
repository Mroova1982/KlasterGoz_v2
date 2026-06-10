# Faza 0 — Fundament — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zbudować wdrażalny szkielet portalu klastergoz.pl — design system z mockupu, w pełni edytowalna nawigacja/stopka/ustawienia w panelu Wagtail, podstawy SEO (sitemap, robots, meta/OG), strony statyczne (LegalPage ×3, ContactPage z formularzem) oraz cookie banner pod GA4.

**Architecture:** Cała treść chrome'u strony (utility bar, menu, stopka, portale, social, dane kontaktowe, GA4) pochodzi z Wagtail Site Settings (część jako StreamField, żeby redaktor swobodnie układał linki). Strony to klasyczne Wagtail Page types renderowane server-side szablonami Django, dziedziczące wspólny `BasePage` z mixinem SEO. Statyczny `styles.css` z mockupu jest źródłem prawdy dla wyglądu — kopiujemy go bez zmian; szablony Django odtwarzają strukturę HTML mockupu, podmieniając statyczne fragmenty na pętle po danych z Settings/modeli. Zero treści zahardkodowanej w szablonach (DoD Fazy 0).

**Tech Stack:** Wagtail 6.3 / Django 5.1 / Python 3.13 / PostgreSQL 16 / Redis 7. Testy: pytest + pytest-django (SQLite in-memory, `--reuse-db`). Bez nowych zależności zewnętrznych — używamy `wagtail.contrib.settings`, `wagtail.contrib.forms`, `wagtail.contrib.sitemaps`, `django.contrib.sitemaps` (wszystko w ekosystemie Wagtail/Django).

> **Decyzja implementacyjna (odstępstwo od specu do potwierdzenia):** spec sekcja 2.1 wymienia `wagtail-seo` w „podstawach SEO". W tym planie realizujemy podstawy SEO **bez pakietu `wagtail-seo`** — własnym, lekkim `SeoMixin` opartym o wbudowane pola Wagtaila (`seo_title`, `search_description`) + `wagtail.contrib.sitemaps` + widok `robots.txt`. Powód: brak ryzyka niezgodności wersji zewnętrznego pakietu, pełna kontrola nad markupem, zgodność z „premium look, bez framework feel". Rozbudowany panel SEO (live SERP preview, walidacja długości — spec 7.4 MVP) ląduje w Fazie 5. Jeśli wolisz trzymać się `wagtail-seo` — zgłoś przy review planu.

---

## Mapa plików (co powstaje / co modyfikujemy)

**Konfiguracja:**
- Modify: `klastergoz/settings/base.py` — INSTALLED_APPS (+ `wagtail.contrib.settings`, `wagtail.contrib.sitemaps`, `django.contrib.sitemaps`, `apps.pages`), context processors (+ settings, +request już jest), `WAGTAILIMAGES_EXTENSIONS`, flaga `SEO_ALLOW_INDEXING`
- Modify: `klastergoz/settings/dev.py` — `SEO_ALLOW_INDEXING = True`
- Modify: `klastergoz/urls.py` — sitemap, robots.txt

**apps/shared** (cross-cutting: SEO, Settings, bloki, base page):
- Create: `apps/shared/models.py` — `SeoMixin`, `BasePage`, `GeneralSettings`, `SocialMediaSettings`, `AnalyticsSettings`, `NavigationSettings`, `FooterSettings`, `PortalsSettings`
- Create: `apps/shared/blocks.py` — `LinkBlock`, `MenuColumnBlock`, `MenuItemBlock`, `FooterColumnBlock`, `PortalLinkBlock`
- Create: `apps/shared/views.py` — `robots_txt`
- Create: `apps/shared/migrations/` (przez `makemigrations`)
- Create: `apps/shared/README.md`
- Create: `apps/shared/tests/__init__.py`, `apps/shared/tests/test_settings.py`, `apps/shared/tests/test_seo.py`, `apps/shared/tests/test_navigation.py`, `apps/shared/tests/test_robots_sitemap.py`

**apps/pages** (nowy app: statyczne typy stron):
- Create: `apps/pages/__init__.py`, `apps/pages/apps.py`, `apps/pages/models.py` (`LegalPage`, `ContactPage`, `ContactFormField`, `ContactPageContactCard`), `apps/pages/forms.py` (honeypot)
- Create: `apps/pages/migrations/`
- Create: `apps/pages/README.md`
- Create: `apps/pages/tests/__init__.py`, `apps/pages/tests/test_legal_page.py`, `apps/pages/tests/test_contact_page.py`

**Szablony:**
- Create: `templates/base.html`
- Create: `templates/includes/header.html`, `templates/includes/footer.html`, `templates/includes/cookie_banner.html`, `templates/includes/meta_tags.html`, `templates/includes/_picture.html`
- Create: `apps/pages/templates/pages/legal_page.html`
- Create: `apps/pages/templates/pages/contact_page.html`, `apps/pages/templates/pages/contact_page_landing.html`

**Statyki (z mockupu):**
- Create: `static/css/styles.css` (kopia `mockup/assets/styles.css`)
- Create: `static/img/logo.svg`, `static/img/logo-white.svg` (kopie z `mockup/assets/`)
- Create: `static/js/main.js` (nawigacja mobilna + cookie consent, vanilla)

---

## Konwencje testów (przeczytaj przed Task 1)

- Uruchamianie: `uv run pytest <ścieżka> -v` (settings testowe są w `pyproject.toml` → `DJANGO_SETTINGS_MODULE=klastergoz.settings.test`).
- Wszystkie testy dotykające bazy: dekorator `@pytest.mark.django_db`.
- Tworzenie stron w testach — pod root page domyślnego Site:

```python
import pytest
from wagtail.models import Page, Site


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


def add_page(parent, instance):
    parent.add_child(instance=instance)
    instance.save_revision().publish()
    return instance
```

- Klient HTTP: `django.test.Client` (import `from django.test import Client`), albo fixture `client` z pytest-django.

---

## Task 1: Konfiguracja Fazy 0 (INSTALLED_APPS, context processor, app `pages`, statyki)

**Files:**
- Modify: `klastergoz/settings/base.py`
- Modify: `klastergoz/settings/dev.py`
- Create: `apps/pages/__init__.py`, `apps/pages/apps.py`
- Create: `static/css/styles.css`, `static/img/logo.svg`, `static/img/logo-white.svg`

- [ ] **Step 1: Dodaj nowy app `apps.pages` (scaffold)**

Create `apps/pages/__init__.py`:

```python
# (pusty plik)
```

Create `apps/pages/apps.py`:

```python
from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    verbose_name = "Strony statyczne"
```

- [ ] **Step 2: Zaktualizuj INSTALLED_APPS i context processors w `base.py`**

Modify `klastergoz/settings/base.py`. W bloku `INSTALLED_APPS` dodaj lokalny app `apps.pages` (po `apps.home`) oraz contrib-y Wagtaila/Django. Zmień sekcję local apps i dodaj brakujące:

```python
INSTALLED_APPS = [
    # local apps
    "apps.shared",
    "apps.home",
    "apps.pages",
    # wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.sitemaps",
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
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
]
```

W bloku `TEMPLATES` → `OPTIONS` → `context_processors` dodaj na końcu listy procesor ustawień Wagtaila:

```python
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
```

Na końcu sekcji „Wagtail-specific" dodaj obsługę SVG dla obrazów i flagę indeksowania:

```python
# Obrazy: pozwól na upload SVG (logo, ikony) obok rastrów.
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]

# Czy serwować robots.txt z pełnym indeksowaniem. Prod=True, staging nadpisuje na False.
SEO_ALLOW_INDEXING = False
```

- [ ] **Step 3: Włącz indeksowanie w dev**

Modify `klastergoz/settings/dev.py` — dodaj na końcu:

```python
SEO_ALLOW_INDEXING = True
```

- [ ] **Step 4: Skopiuj statyki z mockupu**

Run (PowerShell):

```powershell
New-Item -ItemType Directory -Force static\css, static\img, static\js | Out-Null
Copy-Item mockup\assets\styles.css static\css\styles.css
Copy-Item mockup\assets\logo.svg static\img\logo.svg
Copy-Item mockup\assets\logo-white.svg static\img\logo-white.svg
```

Expected: pliki `static/css/styles.css`, `static/img/logo.svg`, `static/img/logo-white.svg` istnieją.

- [ ] **Step 5: Sprawdź, że Django się ładuje (system check)**

Run: `uv run python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 6: Commit**

```bash
git add klastergoz/settings/base.py klastergoz/settings/dev.py apps/pages/__init__.py apps/pages/apps.py static/css/styles.css static/img/logo.svg static/img/logo-white.svg
git commit -m "chore(faza-0): wire settings/sitemaps/forms apps + app pages + static assets

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: SeoMixin + BasePage (apps/shared)

Wspólny mixin SEO i bazowa strona, z której dziedziczą wszystkie typy stron (kontekst meta/OG/canonical). Mixin to abstrakcyjny `models.Model` (komponowalny z `Page` i `AbstractEmailForm`).

**Files:**
- Create: `apps/shared/models.py`
- Test: `apps/shared/tests/test_seo.py` (test przez konkretną stronę powstaje w Task 5; tu testujemy metody mixinu na lekkim modelu)

- [ ] **Step 1: Napisz `SeoMixin` i `BasePage` w `apps/shared/models.py`**

Create `apps/shared/models.py`:

```python
"""Współdzielone modele: mixin SEO, bazowa strona, ustawienia globalne."""
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page


class SeoMixin(models.Model):
    """Wspólne pola i kontekst SEO. Komponowalny z Page i AbstractEmailForm.

    Korzysta z wbudowanych pól Wagtaila (`seo_title`, `search_description`)
    i dokłada obraz Open Graph oraz metody budujące kontekst dla szablonu meta.
    """

    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Obraz social (Open Graph)",
        help_text="Obraz pokazywany przy udostępnianiu na FB/LinkedIn. Zalecane 1200×630 px.",
    )

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("slug"),
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel("og_image"),
            ],
            heading="SEO i social",
        ),
    ]

    class Meta:
        abstract = True

    def get_meta_title(self) -> str:
        """Tytuł do <title> i og:title — seo_title z fallbackiem do title."""
        return self.seo_title or self.title

    def get_meta_description(self) -> str:
        return self.search_description or ""

    def get_meta_image(self):
        """Obraz OG strony albo None (szablon spada wtedy do domyślnego)."""
        return self.og_image


class BasePage(SeoMixin, Page):
    """Bazowa strona portalu — wszystkie typy dziedziczą stąd dla spójnego SEO."""

    class Meta:
        abstract = True
```

- [ ] **Step 2: Napisz test metod SeoMixin (bez bazy)**

Create `apps/shared/tests/__init__.py`:

```python
# (pusty plik)
```

Create `apps/shared/tests/test_seo.py`:

```python
from apps.shared.models import SeoMixin


class _Dummy(SeoMixin):
    """Lekki obiekt do testu metod (bez zapisu do bazy)."""

    class Meta:
        app_label = "shared"
        abstract = True

    def __init__(self, title="", seo_title="", search_description=""):
        self.title = title
        self.seo_title = seo_title
        self.search_description = search_description
        self.og_image = None


def test_meta_title_falls_back_to_title():
    d = _Dummy(title="Kontakt", seo_title="")
    assert d.get_meta_title() == "Kontakt"


def test_meta_title_uses_seo_title_when_set():
    d = _Dummy(title="Kontakt", seo_title="Kontakt — Klaster GOZ")
    assert d.get_meta_title() == "Kontakt — Klaster GOZ"


def test_meta_description_empty_by_default():
    d = _Dummy(title="X")
    assert d.get_meta_description() == ""
```

- [ ] **Step 3: Uruchom test — ma przejść (czysta logika, bez migracji)**

Run: `uv run pytest apps/shared/tests/test_seo.py -v`
Expected: 3 PASSED.

- [ ] **Step 4: Commit**

```bash
git add apps/shared/models.py apps/shared/tests/__init__.py apps/shared/tests/test_seo.py
git commit -m "feat(faza-0): SeoMixin + BasePage z fallbackami meta

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Bloki nawigacji i linków (apps/shared/blocks.py)

StreamField-owe bloki, z których redaktor składa menu i stopkę. Link może wskazywać stronę Wagtaila ALBO zewnętrzny URL (portale, placeholdery do stron z kolejnych faz).

**Files:**
- Create: `apps/shared/blocks.py`
- Test: `apps/shared/tests/test_navigation.py` (część bloków; pełny render w Task 7)

- [ ] **Step 1: Napisz bloki w `apps/shared/blocks.py`**

Create `apps/shared/blocks.py`:

```python
"""Bloki StreamField dla nawigacji, stopki i portali (Site Settings)."""
from wagtail import blocks


class LinkBlock(blocks.StructBlock):
    """Pojedynczy link: tekst + cel (strona Wagtaila ALBO zewnętrzny URL).

    Jeśli ustawione oba — wygrywa `page`. `get_url` zwraca finalny adres.
    """

    label = blocks.CharBlock(label="Tekst linku", max_length=80)
    page = blocks.PageChooserBlock(label="Strona (wewnętrzna)", required=False)
    url = blocks.URLBlock(label="Adres URL (zewnętrzny)", required=False)
    description = blocks.CharBlock(
        label="Opis (mały tekst pod linkiem)", required=False, max_length=120
    )

    class Meta:
        icon = "link"
        label = "Link"

    def get_url(self, value) -> str:
        page = value.get("page")
        if page:
            return page.url
        return value.get("url") or "#"


class MenuColumnBlock(blocks.StructBlock):
    """Kolumna w dropdownie/mega-menu: opcjonalny nagłówek + lista linków."""

    heading = blocks.CharBlock(label="Nagłówek kolumny", required=False, max_length=80)
    links = blocks.ListBlock(LinkBlock(), label="Linki")

    class Meta:
        icon = "list-ul"
        label = "Kolumna menu"


class MenuItemBlock(blocks.StructBlock):
    """Pozycja menu głównego. Bez kolumn = zwykły link.

    Z kolumnami = dropdown (1 kolumna) lub mega-menu (≥2 kolumny).
    """

    label = blocks.CharBlock(label="Tekst pozycji", max_length=60)
    page = blocks.PageChooserBlock(label="Strona docelowa", required=False)
    url = blocks.URLBlock(label="URL docelowy (jeśli brak strony)", required=False)
    nav_key = blocks.CharBlock(
        label="Klucz aktywności",
        required=False,
        max_length=40,
        help_text="np. 'klaster' — podświetla pozycję na stronach tego działu.",
    )
    columns = blocks.ListBlock(MenuColumnBlock(), label="Kolumny dropdownu", required=False)

    class Meta:
        icon = "bars"
        label = "Pozycja menu"

    def get_url(self, value) -> str:
        page = value.get("page")
        if page:
            return page.url
        return value.get("url") or "#"


class FooterColumnBlock(blocks.StructBlock):
    """Kolumna stopki: nagłówek + lista linków."""

    heading = blocks.CharBlock(label="Nagłówek kolumny", max_length=80)
    links = blocks.ListBlock(LinkBlock(), label="Linki")

    class Meta:
        icon = "list-ul"
        label = "Kolumna stopki"


class PortalLinkBlock(blocks.StructBlock):
    """Zewnętrzny portal w dropdownie 'Strefa logowania'."""

    label = blocks.CharBlock(label="Nazwa portalu", max_length=80)
    description = blocks.CharBlock(label="Opis", required=False, max_length=120)
    url = blocks.URLBlock(label="Adres portalu")

    class Meta:
        icon = "user"
        label = "Portal logowania"
```

- [ ] **Step 2: Napisz test logiki `get_url` (page wygrywa nad url, fallback `#`)**

Create `apps/shared/tests/test_navigation.py`:

```python
import pytest

from apps.shared.blocks import LinkBlock, MenuItemBlock


def test_linkblock_url_fallback_hash():
    block = LinkBlock()
    value = block.to_python({"label": "X", "page": None, "url": "", "description": ""})
    assert block.get_url(value) == "#"


def test_linkblock_uses_external_url_when_no_page():
    block = LinkBlock()
    value = block.to_python(
        {"label": "RODO", "page": None, "url": "https://example.org/rodo", "description": ""}
    )
    assert block.get_url(value) == "https://example.org/rodo"


def test_menuitemblock_url_fallback_hash():
    block = MenuItemBlock()
    value = block.to_python({"label": "Klaster", "page": None, "url": "", "nav_key": "", "columns": []})
    assert block.get_url(value) == "#"
```

- [ ] **Step 3: Uruchom test — ma przejść**

Run: `uv run pytest apps/shared/tests/test_navigation.py -v`
Expected: 3 PASSED.

- [ ] **Step 4: Commit**

```bash
git add apps/shared/blocks.py apps/shared/tests/test_navigation.py
git commit -m "feat(faza-0): bloki nawigacji/stopki/portali (StreamField)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Proste Site Settings — General, SocialMedia, Analytics

Ustawienia oparte o zwykłe pola (kontakt, social, GA4). Edytowalne w `/admin/settings/`.

**Files:**
- Modify: `apps/shared/models.py` (dopisanie settingów)
- Test: `apps/shared/tests/test_settings.py`

- [ ] **Step 1: Dopisz settingi do `apps/shared/models.py`**

Na górze pliku rozszerz importy:

```python
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.shared import blocks
```

Na końcu pliku dodaj:

```python
@register_setting
class GeneralSettings(BaseSiteSetting):
    """Dane kontaktowe i tożsamość klastra (header utility bar, stopka, ContactPage)."""

    organization_name = models.CharField(
        "Nazwa organizacji", max_length=200, default="Klaster GOZ"
    )
    phone = models.CharField("Telefon", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    address = models.TextField("Adres", blank=True, help_text="Może być wieloliniowy.")
    nip = models.CharField("NIP", max_length=20, blank=True)
    footer_description = models.TextField(
        "Opis w stopce", blank=True, max_length=400
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Logo w headerze. Puste = domyślne logo z design systemu.",
    )

    panels = [
        FieldPanel("organization_name"),
        FieldPanel("logo"),
        MultiFieldPanel(
            [FieldPanel("phone"), FieldPanel("email"), FieldPanel("address"), FieldPanel("nip")],
            heading="Kontakt",
        ),
        FieldPanel("footer_description"),
    ]

    class Meta:
        verbose_name = "Dane ogólne"


@register_setting
class SocialMediaSettings(BaseSiteSetting):
    """Linki do social media (stopka)."""

    linkedin = models.URLField("LinkedIn", blank=True)
    facebook = models.URLField("Facebook", blank=True)
    youtube = models.URLField("YouTube", blank=True)

    class Meta:
        verbose_name = "Social media"


@register_setting
class AnalyticsSettings(BaseSiteSetting):
    """Google Analytics 4 + treść bannera cookies (RODO)."""

    ga4_measurement_id = models.CharField(
        "GA4 Measurement ID",
        max_length=20,
        blank=True,
        help_text="np. G-XXXXXXXXXX. Puste = analytics wyłączone.",
    )
    cookie_banner_text = models.TextField(
        "Treść bannera cookies",
        blank=True,
        default=(
            "Używamy plików cookies do analizy ruchu (Google Analytics). "
            "Możesz zaakceptować lub odrzucić."
        ),
    )

    class Meta:
        verbose_name = "Analytics i cookies"
```

- [ ] **Step 2: Wygeneruj migracje**

Run: `uv run python manage.py makemigrations shared`
Expected: utworzona migracja z `GeneralSettings`, `SocialMediaSettings`, `AnalyticsSettings`.

- [ ] **Step 3: Napisz test settingów**

Create `apps/shared/tests/test_settings.py`:

```python
import pytest
from wagtail.models import Site

from apps.shared.models import AnalyticsSettings, GeneralSettings, SocialMediaSettings


@pytest.mark.django_db
def test_general_settings_defaults():
    site = Site.objects.get(is_default_site=True)
    gs = GeneralSettings.for_site(site)
    assert gs.organization_name == "Klaster GOZ"


@pytest.mark.django_db
def test_general_settings_editable():
    site = Site.objects.get(is_default_site=True)
    gs = GeneralSettings.for_site(site)
    gs.phone = "+48 22 123 45 67"
    gs.email = "biuro@klastergoz.pl"
    gs.save()
    reloaded = GeneralSettings.for_site(site)
    assert reloaded.phone == "+48 22 123 45 67"
    assert reloaded.email == "biuro@klastergoz.pl"


@pytest.mark.django_db
def test_analytics_default_cookie_text_present():
    site = Site.objects.get(is_default_site=True)
    a = AnalyticsSettings.for_site(site)
    assert "cookies" in a.cookie_banner_text.lower()


@pytest.mark.django_db
def test_social_settings_blank_by_default():
    site = Site.objects.get(is_default_site=True)
    s = SocialMediaSettings.for_site(site)
    assert s.linkedin == ""
```

- [ ] **Step 4: Uruchom test — ma przejść**

Run: `uv run pytest apps/shared/tests/test_settings.py -v`
Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add apps/shared/models.py apps/shared/migrations/ apps/shared/tests/test_settings.py
git commit -m "feat(faza-0): GeneralSettings + SocialMediaSettings + AnalyticsSettings

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Settingi nawigacji — Navigation, Footer, Portals (StreamField)

**Files:**
- Modify: `apps/shared/models.py` (3 settingi StreamField)
- Test: `apps/shared/tests/test_navigation.py` (dopisanie)

- [ ] **Step 1: Dopisz settingi StreamField do `apps/shared/models.py`**

Na końcu pliku dodaj:

```python
@register_setting
class NavigationSettings(BaseSiteSetting):
    """Menu główne (header). Każda pozycja: link + opcjonalne kolumny dropdownu."""

    primary_menu = StreamField(
        [("item", blocks.MenuItemBlock())],
        blank=True,
        help_text="Pozycje menu głównego, w kolejności od lewej.",
    )

    panels = [FieldPanel("primary_menu")]

    class Meta:
        verbose_name = "Nawigacja (menu główne)"


@register_setting
class FooterSettings(BaseSiteSetting):
    """Kolumny linków w stopce (5 kolumn wg mockupu, ale dowolna liczba)."""

    columns = StreamField(
        [("column", blocks.FooterColumnBlock())],
        blank=True,
        help_text="Kolumny linków w stopce.",
    )
    newsletter_heading = models.CharField(
        "Nagłówek newslettera", max_length=80, blank=True, default="Newsletter"
    )
    newsletter_subtext = models.CharField(
        "Podtekst newslettera",
        max_length=160,
        blank=True,
        default="Co miesiąc — bez spamu, sama treść.",
    )

    panels = [
        FieldPanel("columns"),
        MultiFieldPanel(
            [FieldPanel("newsletter_heading"), FieldPanel("newsletter_subtext")],
            heading="Newsletter (placeholder — pełna integracja w Fazie 4)",
        ),
    ]

    class Meta:
        verbose_name = "Stopka"


@register_setting
class PortalsSettings(BaseSiteSetting):
    """Zewnętrzne portale w dropdownie 'Strefa logowania' + stopce."""

    portals = StreamField(
        [("portal", blocks.PortalLinkBlock())],
        blank=True,
        help_text="Portale logowania (Strefa członka, LMS Akademii, Giełda B2B, Platforma badań).",
    )

    panels = [FieldPanel("portals")]

    class Meta:
        verbose_name = "Portale logowania"
```

- [ ] **Step 2: Wygeneruj migracje**

Run: `uv run python manage.py makemigrations shared`
Expected: migracja z `NavigationSettings`, `FooterSettings`, `PortalsSettings`.

- [ ] **Step 3: Dopisz test — settingi StreamField przyjmują dane**

Dopisz do `apps/shared/tests/test_navigation.py`:

```python
from wagtail.models import Site

from apps.shared.models import FooterSettings, NavigationSettings, PortalsSettings


@pytest.mark.django_db
def test_navigation_accepts_menu_item():
    site = Site.objects.get(is_default_site=True)
    nav = NavigationSettings.for_site(site)
    nav.primary_menu = [
        {"type": "item", "value": {"label": "Kontakt", "page": None, "url": "/kontakt/", "nav_key": "kontakt", "columns": []}}
    ]
    nav.save()
    reloaded = NavigationSettings.for_site(site)
    assert reloaded.primary_menu[0].value["label"] == "Kontakt"


@pytest.mark.django_db
def test_portals_accepts_entry():
    site = Site.objects.get(is_default_site=True)
    p = PortalsSettings.for_site(site)
    p.portals = [
        {"type": "portal", "value": {"label": "Strefa członka", "description": "Portal", "url": "https://portal.example/"}}
    ]
    p.save()
    assert PortalsSettings.for_site(site).portals[0].value["url"] == "https://portal.example/"


@pytest.mark.django_db
def test_footer_defaults():
    site = Site.objects.get(is_default_site=True)
    f = FooterSettings.for_site(site)
    assert f.newsletter_heading == "Newsletter"
```

Dodaj na górze pliku brakujący import (jeśli go nie ma): `import pytest`.

- [ ] **Step 4: Uruchom test — ma przejść**

Run: `uv run pytest apps/shared/tests/test_navigation.py -v`
Expected: 6 PASSED (3 z Task 3 + 3 nowe).

- [ ] **Step 5: Commit**

```bash
git add apps/shared/models.py apps/shared/migrations/ apps/shared/tests/test_navigation.py
git commit -m "feat(faza-0): NavigationSettings + FooterSettings + PortalsSettings

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: robots.txt + sitemap.xml

**Files:**
- Create: `apps/shared/views.py`
- Modify: `klastergoz/urls.py`
- Test: `apps/shared/tests/test_robots_sitemap.py`

- [ ] **Step 1: Napisz widok robots w `apps/shared/views.py`**

Create `apps/shared/views.py`:

```python
"""Widoki współdzielone — robots.txt."""
from django.conf import settings
from django.http import HttpResponse


def robots_txt(request) -> HttpResponse:
    """robots.txt zależne od środowiska.

    Prod (SEO_ALLOW_INDEXING=True): pełne indeksowanie + sitemap.
    Staging/dev domyślnie blokuje crawlerów (SEO_ALLOW_INDEXING=False).
    """
    if getattr(settings, "SEO_ALLOW_INDEXING", False):
        lines = [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /django-admin/",
            f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
        ]
    else:
        lines = ["User-agent: *", "Disallow: /"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
```

- [ ] **Step 2: Podepnij URL-e w `klastergoz/urls.py`**

Modify `klastergoz/urls.py` — dodaj importy i ścieżki sitemap/robots PRZED `path("", include(wagtail_urls))` (wagtail przechwytuje wszystko):

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.shared.views import robots_txt

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path("robots.txt", robots_txt),
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 3: Napisz test robots + sitemap**

Create `apps/shared/tests/test_robots_sitemap.py`:

```python
import pytest
from django.test import Client, override_settings


@pytest.mark.django_db
@override_settings(SEO_ALLOW_INDEXING=True)
def test_robots_allows_indexing_in_prod_mode():
    resp = Client().get("/robots.txt")
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "Disallow: /admin/" in body
    assert "Sitemap:" in body
    assert "Disallow: /\n" not in body


@pytest.mark.django_db
@override_settings(SEO_ALLOW_INDEXING=False)
def test_robots_blocks_all_when_indexing_off():
    resp = Client().get("/robots.txt")
    assert resp.status_code == 200
    assert "Disallow: /" in resp.content.decode()


@pytest.mark.django_db
def test_sitemap_returns_xml():
    resp = Client().get("/sitemap.xml")
    assert resp.status_code == 200
    assert "urlset" in resp.content.decode()
```

- [ ] **Step 4: Uruchom test — ma przejść**

Run: `uv run pytest apps/shared/tests/test_robots_sitemap.py -v`
Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add apps/shared/views.py klastergoz/urls.py apps/shared/tests/test_robots_sitemap.py
git commit -m "feat(faza-0): robots.txt (env-aware) + sitemap.xml

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7: Szablon bazowy + header/footer/meta/cookie (sterowane Settings)

Tu powstaje chrome strony. Header/footer odtwarzają strukturę z `mockup/assets/header.html` i `footer.html`, ale linki/menu/portale/dane idą z Settings (zero hardkodu). Statyczny markup (SVG ikony, klasy CSS) przepisujemy z mockupu 1:1.

**Files:**
- Create: `templates/base.html`, `templates/includes/meta_tags.html`, `templates/includes/header.html`, `templates/includes/footer.html`, `templates/includes/cookie_banner.html`, `templates/includes/_picture.html`
- Create: `static/js/main.js`
- Test: weryfikacja renderu w Task 8/9 (po powstaniu konkretnych stron)

- [ ] **Step 1: Napisz `templates/includes/meta_tags.html`**

Create `templates/includes/meta_tags.html`:

```django
{% load static wagtailimages_tags %}
{% comment %}Meta SEO/OG. Oczekuje obiektu `page` z metodami SeoMixin (może być None).{% endcomment %}
<title>{% block meta_title %}{% if page %}{{ page.get_meta_title }}{% else %}{{ settings.shared.GeneralSettings.organization_name }}{% endif %}{% endblock %}</title>
{% if page %}<meta name="description" content="{{ page.get_meta_description }}">{% endif %}
<link rel="canonical" href="{{ request.scheme }}://{{ request.get_host }}{{ request.path }}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{{ settings.shared.GeneralSettings.organization_name }}">
<meta property="og:title" content="{% if page %}{{ page.get_meta_title }}{% else %}{{ settings.shared.GeneralSettings.organization_name }}{% endif %}">
{% if page and page.get_meta_description %}<meta property="og:description" content="{{ page.get_meta_description }}">{% endif %}
{% if page %}{% with og_img=page.get_meta_image %}{% if og_img %}{% image og_img width-1200 as og_rendition %}<meta property="og:image" content="{{ request.scheme }}://{{ request.get_host }}{{ og_rendition.url }}">{% endif %}{% endwith %}{% endif %}
<meta name="twitter:card" content="summary_large_image">
```

- [ ] **Step 2: Napisz `templates/includes/_picture.html` (responsywny obraz / renditions)**

Create `templates/includes/_picture.html`:

```django
{% load wagtailimages_tags %}
{% comment %}
Responsywny obraz z renditions + WebP. Użycie:
  {% include "includes/_picture.html" with image=page.cover alt="opis" loading="lazy" %}
{% endcomment %}
{% if image %}
  {% image image width-800 format-webp as webp_img %}
  {% image image width-800 as fallback_img %}
  <picture>
    <source srcset="{{ webp_img.url }}" type="image/webp">
    <img src="{{ fallback_img.url }}" alt="{{ alt|default:'' }}" loading="{{ loading|default:'lazy' }}" width="{{ fallback_img.width }}" height="{{ fallback_img.height }}">
  </picture>
{% endif %}
```

- [ ] **Step 3: Napisz `templates/includes/header.html` (sterowany NavigationSettings + PortalsSettings + GeneralSettings)**

Odtwórz strukturę z `mockup/assets/header.html` (utility bar, nav, login-zone, burger), ale:
- telefon/e-mail → z `GeneralSettings`,
- logo → z `GeneralSettings.logo` lub statyczne `img/logo.svg`,
- menu główne → pętla po `NavigationSettings.primary_menu`,
- portale → pętla po `PortalsSettings.portals`.

Create `templates/includes/header.html`:

```django
{% load static wagtailimages_tags %}
<header class="site-header">
  <div class="utility">
    <div class="utility-inner">
      <div class="utility-left">
        {% if settings.shared.GeneralSettings.phone %}
        <a href="tel:{{ settings.shared.GeneralSettings.phone|cut:' ' }}" class="util-item">{{ settings.shared.GeneralSettings.phone }}</a>
        {% endif %}
        {% if settings.shared.GeneralSettings.email %}
        <a href="mailto:{{ settings.shared.GeneralSettings.email }}" class="util-item">{{ settings.shared.GeneralSettings.email }}</a>
        {% endif %}
      </div>
      <div class="utility-right">
        <div class="lang-switch">
          <button class="lang active" aria-pressed="true">PL</button>
        </div>
      </div>
    </div>
  </div>

  <nav class="nav">
    <a href="/" class="brand">
      {% if settings.shared.GeneralSettings.logo %}
        {% image settings.shared.GeneralSettings.logo width-260 class="brand-logo" alt=settings.shared.GeneralSettings.organization_name %}
      {% else %}
        <img src="{% static 'img/logo.svg' %}" alt="{{ settings.shared.GeneralSettings.organization_name }}" class="brand-logo">
      {% endif %}
    </a>

    <ul class="nav-list">
      {% for item in settings.shared.NavigationSettings.primary_menu %}
        {% with v=item.value cols=item.value.columns %}
        <li class="{% if cols %}has-sub{% endif %}{% if cols|length > 1 %} has-mega{% endif %}">
          <a href="{{ item.block.get_url|default_if_none:'#' }}{% if not item.block.get_url %}{% endif %}"
             {% if v.page %}href="{{ v.page.url }}"{% elif v.url %}href="{{ v.url }}"{% else %}href="#"{% endif %}
             {% if v.nav_key %}data-nav="{{ v.nav_key }}"{% endif %}>{{ v.label }}</a>
          {% if cols %}
          <div class="dropdown {% if cols|length > 1 %}dropdown--mega{% else %}dropdown--simple dropdown--wide{% endif %}">
            {% if cols|length > 1 %}<div class="mega-grid mega-grid--2">{% endif %}
            {% for col in cols %}
              <div class="mega-col">
                {% if col.heading %}<span class="mega-head"><strong>{{ col.heading }}</strong></span>{% endif %}
                <ul>
                  {% for link in col.links %}
                  <li><a href="{% if link.page %}{{ link.page.url }}{% elif link.url %}{{ link.url }}{% else %}#{% endif %}">
                    <strong>{{ link.label }}</strong>{% if link.description %}<small>{{ link.description }}</small>{% endif %}
                  </a></li>
                  {% endfor %}
                </ul>
              </div>
            {% endfor %}
            {% if cols|length > 1 %}</div>{% endif %}
          </div>
          {% endif %}
        </li>
        {% endwith %}
      {% endfor %}
    </ul>

    <div class="nav-right">
      <button class="icon-btn" aria-label="Szukaj">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      </button>

      {% if settings.shared.PortalsSettings.portals %}
      <div class="login-zone has-sub">
        <button class="btn btn--primary login-btn">Strefa logowania
          <svg class="chev" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="dropdown dropdown--login">
          <div class="login-head"><h4>Zaloguj się do platformy</h4></div>
          <ul class="portal-list">
            {% for portal in settings.shared.PortalsSettings.portals %}
            <li><a href="{{ portal.value.url }}" target="_blank" rel="noopener">
              <span class="portal-txt"><strong>{{ portal.value.label }}</strong>
              {% if portal.value.description %}<small>{{ portal.value.description }}</small>{% endif %}</span>
            </a></li>
            {% endfor %}
          </ul>
        </div>
      </div>
      {% endif %}

      <button class="burger" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </nav>
</header>
```

> Uwaga: powyżej zostawiono uproszczony render pozycji menu i ikon (bez pełnego zestawu SVG z utility bara). Pełne ikony SVG telefonu/maila/użytkownika można przekopiować z `mockup/assets/header.html:8-15` i `:151` jeśli projektant ich wymaga — są czysto dekoracyjne i nie wpływają na funkcję. Klasy CSS (`utility`, `nav`, `dropdown--mega`, `login-zone` itd.) pochodzą ze skopiowanego `styles.css`.

- [ ] **Step 4: Napisz `templates/includes/footer.html`**

Odtwórz `mockup/assets/footer.html`: top CTA strip, grid kolumn (brand+newsletter + kolumny z FooterSettings + portale + kontakt + social), footer-bottom z linkami prawnymi. Rok przez `{% now "Y" %}`.

Create `templates/includes/footer.html`:

```django
{% load static %}
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a href="/" class="brand brand--footer">
          <img src="{% static 'img/logo-white.svg' %}" alt="{{ settings.shared.GeneralSettings.organization_name }}" class="brand-logo brand-logo--footer">
        </a>
        {% if settings.shared.GeneralSettings.footer_description %}
        <p style="color: rgba(255,255,255,0.65); font-size: 14.5px; margin-top: 18px; max-width: 320px;">{{ settings.shared.GeneralSettings.footer_description }}</p>
        {% endif %}
        <h4 style="margin-top: 28px; margin-bottom: 8px;">{{ settings.shared.FooterSettings.newsletter_heading }}</h4>
        <p style="font-size: 13px; color: rgba(255,255,255,0.55); margin: 0;">{{ settings.shared.FooterSettings.newsletter_subtext }}</p>
        {# Newsletter — pełna integracja Brevo w Fazie 4. Tu placeholder bez akcji. #}
        <form class="footer-newsletter" onsubmit="event.preventDefault();">
          <input type="email" placeholder="twoj@email.pl" required>
          <button type="submit">Zapisz się</button>
        </form>
      </div>

      {% for column in settings.shared.FooterSettings.columns %}
      <div>
        <h4>{{ column.value.heading }}</h4>
        <ul>
          {% for link in column.value.links %}
          <li><a href="{% if link.page %}{{ link.page.url }}{% elif link.url %}{{ link.url }}{% else %}#{% endif %}">{{ link.label }}</a></li>
          {% endfor %}
        </ul>
      </div>
      {% endfor %}

      <div>
        {% if settings.shared.PortalsSettings.portals %}
        <h4>Portale</h4>
        <ul>
          {% for portal in settings.shared.PortalsSettings.portals %}
          <li><a href="{{ portal.value.url }}" target="_blank" rel="noopener">{{ portal.value.label }}</a></li>
          {% endfor %}
        </ul>
        {% endif %}
        <h4 style="margin-top: 28px;">Kontakt</h4>
        <ul>
          {% if settings.shared.GeneralSettings.address %}<li style="color: rgba(255,255,255,0.7);">{{ settings.shared.GeneralSettings.address|linebreaksbr }}</li>{% endif %}
          {% if settings.shared.GeneralSettings.email %}<li><a href="mailto:{{ settings.shared.GeneralSettings.email }}">{{ settings.shared.GeneralSettings.email }}</a></li>{% endif %}
          {% if settings.shared.GeneralSettings.phone %}<li><a href="tel:{{ settings.shared.GeneralSettings.phone|cut:' ' }}">{{ settings.shared.GeneralSettings.phone }}</a></li>{% endif %}
        </ul>
        <div style="display:flex; gap: 10px; margin-top: 22px;">
          {% if settings.shared.SocialMediaSettings.linkedin %}<a href="{{ settings.shared.SocialMediaSettings.linkedin }}" target="_blank" rel="noopener" style="width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,0.08);display:grid;place-items:center;font-weight:700;font-size:13px;">in</a>{% endif %}
          {% if settings.shared.SocialMediaSettings.facebook %}<a href="{{ settings.shared.SocialMediaSettings.facebook }}" target="_blank" rel="noopener" style="width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,0.08);display:grid;place-items:center;font-weight:700;font-size:13px;">fb</a>{% endif %}
          {% if settings.shared.SocialMediaSettings.youtube %}<a href="{{ settings.shared.SocialMediaSettings.youtube }}" target="_blank" rel="noopener" style="width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,0.08);display:grid;place-items:center;font-weight:700;font-size:13px;">yt</a>{% endif %}
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <span>© {% now "Y" %} {{ settings.shared.GeneralSettings.organization_name }}</span>
    </div>
  </div>
</footer>
```

- [ ] **Step 5: Napisz `templates/includes/cookie_banner.html`**

Create `templates/includes/cookie_banner.html`:

```django
{% if settings.shared.AnalyticsSettings.ga4_measurement_id %}
<div class="cookie-banner" id="cookieBanner" hidden
     data-ga-id="{{ settings.shared.AnalyticsSettings.ga4_measurement_id }}">
  <p>{{ settings.shared.AnalyticsSettings.cookie_banner_text }}</p>
  <div class="cookie-actions">
    <button type="button" class="btn btn--primary" data-cookie="accept">Akceptuję</button>
    <button type="button" class="btn btn--light" data-cookie="reject">Odrzucam</button>
  </div>
</div>
{% endif %}
```

- [ ] **Step 6: Napisz `static/js/main.js` (nawigacja mobilna + cookie consent + GA4)**

Create `static/js/main.js`:

```javascript
// Nawigacja mobilna + zgoda na cookies + warunkowy GA4. Vanilla, bez zależności.
(function () {
  "use strict";

  // --- Burger (menu mobilne) ---
  document.addEventListener("click", function (e) {
    if (e.target.closest(".burger")) {
      document.body.classList.toggle("menu-open");
    }
  });

  // --- Cookie consent + GA4 ---
  var STORAGE_KEY = "kg_cookie_consent"; // "accepted" | "rejected"
  var banner = document.getElementById("cookieBanner");

  function loadGA(gaId) {
    if (!gaId || window.__gaLoaded) return;
    window.__gaLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + gaId;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", gaId);
  }

  if (banner) {
    var gaId = banner.getAttribute("data-ga-id");
    var consent = localStorage.getItem(STORAGE_KEY);
    if (consent === "accepted") {
      loadGA(gaId);
    } else if (consent !== "rejected") {
      banner.hidden = false;
    }
    banner.addEventListener("click", function (e) {
      var action = e.target.getAttribute("data-cookie");
      if (!action) return;
      if (action === "accept") {
        localStorage.setItem(STORAGE_KEY, "accepted");
        loadGA(gaId);
      } else {
        localStorage.setItem(STORAGE_KEY, "rejected");
      }
      banner.hidden = true;
    });
  }
})();
```

- [ ] **Step 7: Napisz `templates/base.html`**

Create `templates/base.html`:

```django
{% load static wagtailcore_tags %}
<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {% include "includes/meta_tags.html" %}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/styles.css' %}">
  {% block extra_head %}{% endblock %}
</head>
<body {% block body_attrs %}{% endblock %}>
  {% include "includes/header.html" %}
  <main>
    {% block content %}{% endblock %}
  </main>
  {% include "includes/footer.html" %}
  {% include "includes/cookie_banner.html" %}
  <script src="{% static 'js/main.js' %}" defer></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

- [ ] **Step 8: Sanity check — Django renderuje szablony bez błędu składni**

Run: `uv run python manage.py check`
Expected: brak błędów. (Pełny render zweryfikujemy testem w Task 8.)

- [ ] **Step 9: Commit**

```bash
git add templates/ static/js/main.js
git commit -m "feat(faza-0): szablon bazowy + header/footer/meta/cookie sterowane Settings

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 8: LegalPage (RODO / Regulamin / Cookies)

Jeden typ strony, wiele instancji. Body = StreamField (RichText + obrazy), żeby redaktor swobodnie redagował dokumenty prawne.

**Files:**
- Create: `apps/pages/models.py`
- Create: `apps/pages/templates/pages/legal_page.html`
- Test: `apps/pages/tests/__init__.py`, `apps/pages/tests/test_legal_page.py`

- [ ] **Step 1: Napisz `LegalPage` w `apps/pages/models.py`**

Create `apps/pages/models.py`:

```python
"""Statyczne typy stron: LegalPage (dokumenty prawne); ContactPage dodawany w Task 9."""
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

from apps.shared.models import BasePage


class LegalPage(BasePage):
    """Dokument prawny (RODO / Regulamin / Cookies). Jeden typ, wiele instancji."""

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title", label="Nagłówek sekcji")),
            ("paragraph", blocks.RichTextBlock(label="Tekst")),
            ("image", ImageChooserBlock(label="Obraz")),
        ],
        blank=True,
        help_text="Treść dokumentu — nagłówki, akapity, obrazy.",
    )

    content_panels = BasePage.content_panels + [FieldPanel("body")]
    promote_panels = BasePage.promote_panels
    template = "pages/legal_page.html"

    class Meta:
        verbose_name = "Strona prawna"
        verbose_name_plural = "Strony prawne"
```

- [ ] **Step 2: Napisz szablon `apps/pages/templates/pages/legal_page.html`**

Odtwarza strukturę `mockup/rodo.html` (page-header + article), body z StreamField.

Create `apps/pages/templates/pages/legal_page.html`:

```django
{% extends "base.html" %}
{% load static wagtailcore_tags wagtailimages_tags %}

{% block body_attrs %}data-page="legal"{% endblock %}

{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li><li>{{ page.title }}</li></ul>
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.search_description %}<p class="lead">{{ page.search_description }}</p>{% endif %}
  </div>
</section>

<section class="section">
  <div class="container">
    <article class="article">
      {% for block in page.body %}
        {% if block.block_type == "heading" %}<h2>{{ block.value }}</h2>
        {% elif block.block_type == "paragraph" %}{{ block.value|richtext }}
        {% elif block.block_type == "image" %}{% image block.value width-900 %}
        {% endif %}
      {% endfor %}
    </article>
  </div>
</section>
{% endblock %}
```

- [ ] **Step 3: Wygeneruj migracje**

Run: `uv run python manage.py makemigrations pages`
Expected: migracja tworząca `LegalPage`.

- [ ] **Step 4: Napisz failing test renderu LegalPage**

Create `apps/pages/tests/__init__.py`:

```python
# (pusty plik)
```

Create `apps/pages/tests/test_legal_page.py`:

```python
import pytest
from django.test import Client
from wagtail.models import Site

from apps.pages.models import LegalPage


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.mark.django_db
def test_legal_page_renders_title_and_body(root_page):
    page = LegalPage(
        title="Polityka prywatności i RODO",
        slug="rodo",
        body=[
            {"type": "heading", "value": "1. Administrator danych"},
            {"type": "paragraph", "value": "<p>Administratorem jest Klaster GOZ.</p>"},
        ],
    )
    root_page.add_child(instance=page)
    page.save_revision().publish()

    resp = Client().get("/rodo/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Polityka prywatności i RODO" in html
    assert "1. Administrator danych" in html
    assert "Administratorem jest Klaster GOZ." in html


@pytest.mark.django_db
def test_legal_page_in_sitemap(root_page):
    page = LegalPage(title="Regulamin", slug="regulamin", body=[])
    root_page.add_child(instance=page)
    page.save_revision().publish()

    resp = Client().get("/sitemap.xml")
    assert resp.status_code == 200
    assert "/regulamin/" in resp.content.decode()
```

- [ ] **Step 5: Uruchom test — ma przejść**

Run: `uv run pytest apps/pages/tests/test_legal_page.py -v`
Expected: 2 PASSED.

- [ ] **Step 6: Commit**

```bash
git add apps/pages/models.py apps/pages/migrations/ apps/pages/templates/pages/legal_page.html apps/pages/tests/__init__.py apps/pages/tests/test_legal_page.py
git commit -m "feat(faza-0): LegalPage (RODO/Regulamin/Cookies) + szablon + testy

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 9: ContactPage (Wagtail Form Builder + dane kontaktowe + honeypot)

Strona kontaktu z edytowalnym formularzem (Form Builder zapisuje zgłoszenia w DB i wysyła e-mail), kartami kontaktowymi (InlinePanel) i polem mapy. Honeypot anti-spam. Zgoda RODO jako wymagane pole formularza.

**Files:**
- Modify: `apps/pages/models.py` (ContactPage, ContactFormField, ContactPageContactCard)
- Create: `apps/pages/forms.py` (honeypot form)
- Create: `apps/pages/templates/pages/contact_page.html`, `apps/pages/templates/pages/contact_page_landing.html`
- Test: `apps/pages/tests/test_contact_page.py`

- [ ] **Step 1: Napisz formularz z honeypotem w `apps/pages/forms.py`**

Create `apps/pages/forms.py`:

```python
"""Formularz ContactPage z honeypotem anti-spam."""
from django import forms
from wagtail.contrib.forms.forms import FormBuilder


class HoneypotFormBuilder(FormBuilder):
    """Dokłada ukryte pole-pułapkę. Boty je wypełniają, ludzie nie."""

    @property
    def formfields(self):
        fields = super().formfields
        fields["hp_website"] = forms.CharField(
            required=False,
            label="Nie wypełniaj tego pola",
            widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
        )
        return fields
```

- [ ] **Step 2: Dopisz modele ContactPage do `apps/pages/models.py`**

Rozszerz importy na górze `apps/pages/models.py`:

```python
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock

from apps.pages.forms import HoneypotFormBuilder
from apps.shared.models import BasePage, SeoMixin
```

Na końcu pliku dodaj:

```python
class ContactFormField(AbstractFormField):
    """Pole formularza kontaktowego (konfigurowalne przez redaktora)."""

    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactPageContactCard(models.Model):
    """Karta z danymi kontaktowymi (biuro, sekretariat, koordynator...)."""

    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="contact_cards")
    heading = models.CharField("Nagłówek", max_length=120)
    body = RichTextField("Treść", features=["bold", "link"])
    sort_order = models.IntegerField(default=0, blank=True)

    panels = [FieldPanel("heading"), FieldPanel("body")]

    class Meta:
        ordering = ["sort_order"]


class ContactPage(SeoMixin, AbstractEmailForm):
    """Strona kontaktu: Form Builder + karty kontaktowe + mapa. Jedna instancja."""

    form_builder = HoneypotFormBuilder

    intro = RichTextField("Wstęp nad formularzem", blank=True, features=["bold", "italic", "link"])
    thank_you_text = RichTextField(
        "Tekst podziękowania", blank=True, features=["bold", "link"]
    )
    map_embed = models.TextField(
        "Mapa (embed HTML / iframe)",
        blank=True,
        help_text="Wklej kod iframe z Google Maps. Puste = brak mapy.",
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("contact_cards", label="Karty kontaktowe"),
        InlinePanel("form_fields", label="Pola formularza"),
        FieldPanel("thank_you_text"),
        FieldPanel("map_embed"),
        MultiFieldPanel(
            [
                FieldPanel("to_address"),
                FieldPanel("from_address"),
                FieldPanel("subject"),
            ],
            heading="Powiadomienie e-mail o zgłoszeniu",
        ),
    ]
    promote_panels = SeoMixin.promote_panels

    template = "pages/contact_page.html"
    landing_page_template = "pages/contact_page_landing.html"

    def process_form_submission(self, form):
        """Odrzuca zgłoszenia z wypełnionym honeypotem (cicho — bot nie wie)."""
        if form.cleaned_data.get("hp_website"):
            return None
        return super().process_form_submission(form)

    class Meta:
        verbose_name = "Strona kontaktu"
```

> Uwaga o SEO: `AbstractEmailForm` (przez `Page`) ma już `seo_title`/`search_description`; `SeoMixin` dokłada `og_image` i metody. Dlatego `ContactPage(SeoMixin, AbstractEmailForm)` — mixin pierwszy.

- [ ] **Step 3: Napisz szablony ContactPage**

Create `apps/pages/templates/pages/contact_page.html` (odtwarza `mockup/kontakt.html`: page-header, grid dane+formularz, sekcja mapy):

```django
{% extends "base.html" %}
{% load static wagtailcore_tags %}

{% block body_attrs %}data-page="kontakt"{% endblock %}

{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li><li>{{ page.title }}</li></ul>
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.intro %}<div class="lead">{{ page.intro|richtext }}</div>{% endif %}
  </div>
</section>

<section class="section">
  <div class="container" style="display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 60px;">
    <div>
      <h2 style="margin-bottom: 24px;">Dane kontaktowe</h2>
      <div style="display: grid; gap: 24px;">
        {% for card in page.contact_cards.all %}
        <div style="background:#fff; border:1px solid var(--ink-100); border-radius:18px; padding:28px;">
          <h4 style="margin:0 0 8px;">{{ card.heading }}</h4>
          <div style="color: var(--ink-700);">{{ card.body|richtext }}</div>
        </div>
        {% endfor %}
      </div>
    </div>

    <div id="formularz">
      <h2 style="margin-bottom: 8px;">Formularz kontaktowy</h2>
      <form class="consult-form" action="{% pageurl page %}" method="post">
        {% csrf_token %}
        {% for field in form.visible_fields %}
          <div class="form-row">
            <div class="field">
              <label for="{{ field.id_for_label }}">{{ field.label }}</label>
              {{ field }}
              {% if field.help_text %}<small>{{ field.help_text }}</small>{% endif %}
              {% for error in field.errors %}<small class="error">{{ error }}</small>{% endfor %}
            </div>
          </div>
        {% endfor %}
        {% for field in form.hidden_fields %}{{ field }}{% endfor %}
        <button type="submit" class="btn btn--primary" style="width: 100%; justify-content: center;">Wyślij wiadomość <span class="arr">→</span></button>
      </form>
    </div>
  </div>
</section>

{% if page.map_embed %}
<section class="section--tight">
  <div class="container">{{ page.map_embed|safe }}</div>
</section>
{% endif %}
{% endblock %}
```

Create `apps/pages/templates/pages/contact_page_landing.html` (ekran po wysłaniu):

```django
{% extends "base.html" %}
{% load wagtailcore_tags %}

{% block content %}
<section class="page-header">
  <div class="container">
    <h1 style="margin-top: 16px;">Dziękujemy.</h1>
    {% if page.thank_you_text %}<div class="lead">{{ page.thank_you_text|richtext }}</div>
    {% else %}<p class="lead">Skontaktujemy się w ciągu 24 godzin roboczych.</p>{% endif %}
  </div>
</section>
{% endblock %}
```

- [ ] **Step 4: Wygeneruj migracje**

Run: `uv run python manage.py makemigrations pages`
Expected: migracja z `ContactPage`, `ContactFormField`, `ContactPageContactCard`.

- [ ] **Step 5: Napisz testy ContactPage (GET render, POST tworzy submission, honeypot odrzuca)**

Create `apps/pages/tests/test_contact_page.py`:

```python
import pytest
from django.test import Client
from wagtail.contrib.forms.models import FormSubmission
from wagtail.models import Site

from apps.pages.models import ContactPage, ContactFormField


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.fixture
def contact_page(root_page):
    page = ContactPage(
        title="Kontakt",
        slug="kontakt",
        to_address="biuro@klastergoz.pl",
        from_address="noreply@klastergoz.pl",
        subject="Nowe zgłoszenie kontaktowe",
        intro="<p>Napisz do nas.</p>",
    )
    root_page.add_child(instance=page)
    page.form_fields.add(
        ContactFormField(label="Imię i nazwisko", field_type="singleline", required=True),
        ContactFormField(label="E-mail", field_type="email", required=True),
        ContactFormField(label="Wiadomość", field_type="multiline", required=True),
    )
    page.save_revision().publish()
    return page


@pytest.mark.django_db
def test_contact_page_renders_form_and_cards(contact_page):
    resp = Client().get("/kontakt/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Formularz kontaktowy" in html
    assert "Imię i nazwisko" in html


@pytest.mark.django_db
def test_contact_form_submission_creates_record(contact_page):
    resp = Client().post(
        "/kontakt/",
        {
            "imie-i-nazwisko": "Anna Kowalska",
            "e-mail": "anna@firma.pl",
            "wiadomosc": "Dzień dobry, mam pytanie.",
        },
    )
    assert resp.status_code == 200
    assert FormSubmission.objects.filter(page=contact_page).count() == 1


@pytest.mark.django_db
def test_honeypot_blocks_spam(contact_page):
    Client().post(
        "/kontakt/",
        {
            "imie-i-nazwisko": "Bot",
            "e-mail": "bot@spam.ru",
            "wiadomosc": "spam",
            "hp_website": "http://spam.example",
        },
    )
    assert FormSubmission.objects.filter(page=contact_page).count() == 0
```

> Uwaga: Wagtail tworzy `clean_name` pól z etykiet (np. „Imię i nazwisko" → `imie-i-nazwisko`). Jeśli wersja Wagtaila wygeneruje inne nazwy, wypisz je: w teście dodaj tymczasowo `print(form.fields.keys())` albo sprawdź `page.form_fields.all()` → `field.clean_name`. Dostosuj klucze POST do faktycznych `clean_name`.

- [ ] **Step 6: Uruchom testy — mają przejść**

Run: `uv run pytest apps/pages/tests/test_contact_page.py -v`
Expected: 3 PASSED. (Jeśli `test_contact_form_submission_creates_record` failuje na kluczach POST — popraw nazwy pól wg uwagi powyżej.)

- [ ] **Step 7: Commit**

```bash
git add apps/pages/models.py apps/pages/forms.py apps/pages/migrations/ apps/pages/templates/pages/contact_page.html apps/pages/templates/pages/contact_page_landing.html apps/pages/tests/test_contact_page.py
git commit -m "feat(faza-0): ContactPage (Form Builder + honeypot + karty kontaktowe)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 10: Dane startowe — seed Settings + strony (data migration)

Żeby świeża baza dawała działającą stronę (nawigacja, stopka, 4 strony), tworzymy idempotentny seed. Treść pozostaje w pełni edytowalna w adminie (DoD — to tylko punkt startowy, nie hardcode w szablonach).

**Files:**
- Create: `apps/pages/migrations/0002_seed_initial_pages.py` (numer dostosuj do faktycznego)
- Test: `apps/pages/tests/test_seed.py`

- [ ] **Step 1: Napisz data migration tworzącą strony i wypełniającą Settings**

Sprawdź numer ostatniej migracji `pages` (`ls apps/pages/migrations/`). Create `apps/pages/migrations/0002_seed_initial_pages.py` (zależność = poprzednia migracja pages + ostatnia shared):

```python
"""Seed: 3 strony prawne + strona kontaktu + podstawowe Settings. Idempotentne."""
from django.db import migrations


def seed(apps, schema_editor):
    from wagtail.models import Page, Site

    from apps.pages.models import ContactPage, LegalPage
    from apps.shared.models import (
        FooterSettings,
        GeneralSettings,
        NavigationSettings,
        PortalsSettings,
    )

    site = Site.objects.filter(is_default_site=True).first()
    if not site:
        return
    root = site.root_page

    # --- Strony prawne ---
    legal = {
        "rodo": "Polityka prywatności i RODO",
        "regulamin": "Regulamin",
        "cookies": "Polityka cookies",
    }
    for slug, title in legal.items():
        if not Page.objects.filter(slug=slug).exists():
            root.add_child(instance=LegalPage(title=title, slug=slug, body=[
                {"type": "paragraph", "value": "<p>Treść do uzupełnienia w panelu administracyjnym.</p>"}
            ])).save_revision().publish()

    # --- Strona kontaktu ---
    if not Page.objects.filter(slug="kontakt").exists():
        contact = ContactPage(
            title="Kontakt",
            slug="kontakt",
            to_address="biuro@klastergoz.pl",
            from_address="noreply@klastergoz.pl",
            subject="Nowe zgłoszenie kontaktowe",
            intro="<p>Pytania ogólne, członkostwo, doradztwo, szkolenia — wybierz kanał.</p>",
        )
        root.add_child(instance=contact)
        contact.save_revision().publish()

    # --- Settings ---
    gs = GeneralSettings.for_site(site)
    if not gs.email:
        gs.organization_name = "Klaster Gospodarki Cyrkularnej i Recyklingu"
        gs.phone = "+48 22 123 45 67"
        gs.email = "biuro@klastergoz.pl"
        gs.address = "ul. Przykładowa 12\n00-001 Warszawa"
        gs.footer_description = (
            "Klaster Gospodarki Cyrkularnej i Recyklingu — od 2012 roku łączymy firmy, "
            "naukę i instytucje wokół transformacji cyrkularnej polskiego przemysłu."
        )
        gs.save()

    nav = NavigationSettings.for_site(site)
    if not nav.primary_menu:
        nav.primary_menu = [
            {"type": "item", "value": {"label": "Kontakt", "page": None, "url": "/kontakt/", "nav_key": "kontakt", "columns": []}},
        ]
        nav.save()

    footer = FooterSettings.for_site(site)
    if not footer.columns:
        footer.columns = [
            {"type": "column", "value": {"heading": "O klastrze", "links": [
                {"label": "Kontakt", "page": None, "url": "/kontakt/", "description": ""},
                {"label": "RODO", "page": None, "url": "/rodo/", "description": ""},
                {"label": "Regulamin", "page": None, "url": "/regulamin/", "description": ""},
                {"label": "Cookies", "page": None, "url": "/cookies/", "description": ""},
            ]}},
        ]
        footer.save()

    PortalsSettings.for_site(site)  # utwórz pusty rekord


def unseed(apps, schema_editor):
    # Nieodwracalne czyszczenie pomijamy — seed jest idempotentny.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),
        ("shared", "0002_navigation_footer_portals"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
```

> Dostosuj nazwy w `dependencies` do faktycznych nazw plików migracji (sprawdź `apps/shared/migrations/` i `apps/pages/migrations/`). Importy modeli przez bezpośredni import (nie `apps.get_model`), bo używamy metod Wagtaila (`add_child`, `for_site`) niedostępnych na modelach historycznych — to akceptowalne w seedach Wagtaila.

- [ ] **Step 2: Uruchom migracje na czystej bazie testowej i sprawdź seed**

Create `apps/pages/tests/test_seed.py`:

```python
import pytest
from wagtail.models import Page

from apps.shared.models import GeneralSettings
from wagtail.models import Site


@pytest.mark.django_db
def test_seed_created_legal_and_contact_pages():
    for slug in ["rodo", "regulamin", "cookies", "kontakt"]:
        assert Page.objects.filter(slug=slug).exists(), f"brak strony {slug}"


@pytest.mark.django_db
def test_seed_filled_general_settings():
    site = Site.objects.get(is_default_site=True)
    gs = GeneralSettings.for_site(site)
    assert gs.email == "biuro@klastergoz.pl"
```

> Uwaga: testy z `--reuse-db` wymagają zastosowania migracji. Jeśli baza testowa była utworzona wcześniej, uruchom raz `uv run pytest --create-db apps/pages/tests/test_seed.py -v`, by przeładować migracje.

- [ ] **Step 3: Uruchom test — ma przejść**

Run: `uv run pytest --create-db apps/pages/tests/test_seed.py -v`
Expected: 2 PASSED.

- [ ] **Step 4: Commit**

```bash
git add apps/pages/migrations/0002_seed_initial_pages.py apps/pages/tests/test_seed.py
git commit -m "feat(faza-0): seed startowych stron i Settings (idempotentny)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 11: Render end-to-end + smoke test całej Fazy 0

Weryfikacja, że strona renderuje się z chrome'em (header/footer/cookie) i całość przechodzi.

**Files:**
- Test: `apps/pages/tests/test_chrome_render.py`

- [ ] **Step 1: Napisz test, że strony zawierają header/footer/cookie z danymi z Settings**

Create `apps/pages/tests/test_chrome_render.py`:

```python
import pytest
from django.test import Client, override_settings
from wagtail.models import Site

from apps.shared.models import AnalyticsSettings


@pytest.mark.django_db
def test_legal_page_includes_footer_contact_from_settings():
    # seed wypełnił GeneralSettings → e-mail powinien być w stopce
    resp = Client().get("/rodo/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "biuro@klastergoz.pl" in html  # stopka (kontakt z GeneralSettings)
    assert "site-header" in html
    assert "site-footer" in html


@pytest.mark.django_db
def test_cookie_banner_appears_only_with_ga_id():
    # bez GA4 ID — brak bannera
    resp = Client().get("/rodo/")
    assert "cookieBanner" not in resp.content.decode()

    # z GA4 ID — banner obecny
    site = Site.objects.get(is_default_site=True)
    a = AnalyticsSettings.for_site(site)
    a.ga4_measurement_id = "G-TEST12345"
    a.save()
    resp2 = Client().get("/rodo/")
    html = resp2.content.decode()
    assert "cookieBanner" in html
    assert "G-TEST12345" in html
```

- [ ] **Step 2: Uruchom test — ma przejść**

Run: `uv run pytest --create-db apps/pages/tests/test_chrome_render.py -v`
Expected: 2 PASSED.

- [ ] **Step 3: Uruchom CAŁY zestaw testów**

Run: `uv run pytest --create-db -v`
Expected: wszystkie testy PASSED (shared: seo/settings/navigation/robots_sitemap; pages: legal/contact/seed/chrome).

- [ ] **Step 4: Smoke test ręczny (serwer + admin)**

Run:
```bash
uv run python manage.py migrate
uv run python manage.py runserver
```
Sprawdź ręcznie:
- `http://localhost:8000/rodo/` — renderuje się z headerem i stopką
- `http://localhost:8000/kontakt/` — formularz widoczny, wysłanie tworzy zgłoszenie
- `http://localhost:8000/sitemap.xml` — zawiera /rodo/, /kontakt/
- `http://localhost:8000/admin/settings/` — wszystkie 6 grup Settings edytowalne
- `http://localhost:8000/admin/` — można dodać/edytować LegalPage i ContactPage

- [ ] **Step 5: Commit**

```bash
git add apps/pages/tests/test_chrome_render.py
git commit -m "test(faza-0): smoke test renderu chrome + cookie banner

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 12: Dokumentacja (DoD — README per app)

**Files:**
- Create: `apps/shared/README.md`, `apps/pages/README.md`
- Modify: `README.md` (link do faz / statusu)

- [ ] **Step 1: Napisz `apps/shared/README.md`**

Create `apps/shared/README.md`:

```markdown
# apps.shared

Współdzielone fundamenty portalu.

## Co robi
- `SeoMixin` / `BasePage` — wspólne pola i kontekst SEO (meta, OG, canonical) dla wszystkich typów stron.
- Site Settings (edytowalne w `/admin/settings/`):
  - `GeneralSettings` — dane kontaktowe, logo, opis stopki.
  - `SocialMediaSettings` — linki social.
  - `AnalyticsSettings` — GA4 ID + treść bannera cookies.
  - `NavigationSettings` — menu główne (StreamField pozycji + kolumny dropdownów).
  - `FooterSettings` — kolumny linków stopki + newsletter (placeholder).
  - `PortalsSettings` — zewnętrzne portale logowania.
- `blocks.py` — bloki StreamField nawigacji/stopki/portali.
- `views.py` — `robots.txt` (zależny od `SEO_ALLOW_INDEXING`).

## Jak używać
Nowe typy stron dziedziczą z `BasePage` (`from apps.shared.models import BasePage`).
W szablonach Settings dostępne przez `{{ settings.shared.<Nazwa>.<pole> }}`
(context processor `wagtail.contrib.settings`).

## Zależności
Wagtail (`contrib.settings`, `contrib.sitemaps`, `images`), Django `contrib.sitemaps`.
```

- [ ] **Step 2: Napisz `apps/pages/README.md`**

Create `apps/pages/README.md`:

```markdown
# apps.pages

Statyczne typy stron portalu.

## Co robi
- `LegalPage` — dokument prawny (RODO / Regulamin / Cookies). Jeden typ, wiele instancji. Body = StreamField (nagłówek / akapit / obraz).
- `ContactPage` — strona kontaktu oparta o Wagtail Form Builder:
  - edytowalne pola formularza (`form_fields`), zgłoszenia zapisywane w DB + e-mail do biura,
  - honeypot anti-spam (`HoneypotFormBuilder` w `forms.py`),
  - karty kontaktowe (`contact_cards`), wstęp, tekst podziękowania, embed mapy.

## Jak używać
Strony tworzy/edytuje redaktor w `/admin/`. Seed (`migrations/0002_seed_initial_pages.py`)
zakłada startowe instancje (/rodo, /regulamin, /cookies, /kontakt) — treść do uzupełnienia w panelu.

## Zależności
`apps.shared` (BasePage/SeoMixin), `wagtail.contrib.forms`.

## Uwaga (sekwencja faz)
W Fazie 0 strony są dziećmi root page domyślnego Site. Faza 1 wprowadzi `HomePage`
jako root i przeniesie te strony pod nią (URL-e najwyższego poziomu pozostają: /rodo/, /kontakt/).
```

- [ ] **Step 3: Zaktualizuj główny `README.md`**

Modify `README.md` — w sekcji „Dokumentacja projektu" dodaj odnośnik do planu faz:

```markdown
## Dokumentacja projektu

- Spec: `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md` (sekcja 2.1 — fazy, 2.2 — Definition of Done)
- Plany: `docs/superpowers/plans/`
  - Faza 0 (Fundament): `docs/superpowers/plans/2026-06-10-faza-0-fundament.md`
- Status: Faza 0 w realizacji.
```

- [ ] **Step 4: Lint + pełne testy (DoD)**

Run:
```bash
uv run ruff check .
uv run black --check .
uv run pytest --create-db -v
```
Expected: ruff/black czyste, wszystkie testy PASSED. (Jeśli black zgłasza formatowanie — uruchom `uv run black .` i dodaj zmiany do commita.)

- [ ] **Step 5: Commit końcowy Fazy 0**

```bash
git add apps/shared/README.md apps/pages/README.md README.md
git commit -m "docs(faza-0): README aplikacji shared/pages + status faz

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (wypełnione przez autora planu)

**1. Pokrycie zakresu Fazy 0 (spec 2.1):**
- Design system z mockupu (base.html, header/footer, styles.css) → Task 1 (kopia CSS), Task 7 (szablony) ✅
- Renditions obrazów → Task 7 (`_picture.html`, `{% image %}` + WebP), SVG enabled w Task 1 ✅
- Site Settings (General/Navigation/Footer/Portals/Social) → Task 4 + Task 5 ✅ (Analytics dodatkowo)
- Nawigacja (dropdowny + footer 5 kolumn) → Task 5 (modele), Task 7 (render) ✅
- Podstawy SEO (sitemap, robots, meta) → Task 2 (meta mixin), Task 6 (sitemap+robots), Task 7 (meta_tags) ✅ (wagtail-seo świadomie zastąpione — patrz nagłówek)
- Strony statyczne (LegalPage ×3, ContactPage z formularzem) → Task 8, Task 9, Task 10 (seed instancji) ✅
- Cookie banner (GA4) → Task 4 (AnalyticsSettings), Task 7 (banner + JS) ✅

**2. Definition of Done (spec 2.2):**
- Pełne zarządzanie treścią w Wagtailu → cała treść chrome z Settings, strony jako Page types; weryfikacja w Task 11 Step 4 ✅
- Przechodzące testy → testy w każdym tasku + pełny run Task 11/12 ✅
- Commit do Git → commit kończy każdy task ✅
- Dokumentacja → docstringi w kodzie + README per app (Task 12) ✅

**3. Skan placeholderów:** brak TBD/TODO/„implement later". Każdy krok kodu zawiera pełny, gotowy kod. Komentarze typu „placeholder" dotyczą wyłącznie świadomie odłożonych funkcji (newsletter → Faza 4), nie braków w planie.

**4. Spójność typów/nazw:** `BasePage`/`SeoMixin` (shared) używane w `LegalPage`/`ContactPage`; `get_url` zdefiniowane w `LinkBlock`/`MenuItemBlock` i używane w szablonach; nazwy Settings (`GeneralSettings`, `NavigationSettings`...) spójne między modelami, seedem i szablonami (`settings.shared.<Nazwa>`); `HoneypotFormBuilder` z `forms.py` użyty w `ContactPage.form_builder`.

**Znane punkty wymagające uwagi przy wykonaniu (oznaczone w planie):**
- Nazwy plików migracji w `dependencies` seeda (Task 10) — dostosować do faktycznych.
- Klucze POST w teście formularza (Task 9) — dostosować do `clean_name` generowanych przez Wagtaila.
- Render mega-menu w header.html (Task 7) jest świadomie uproszczony względem bogatego mockupu — pełny 2-kolumnowy mega-dropdown Edukacji dojdzie wraz z treścią filaru w Fazie 1/3.
