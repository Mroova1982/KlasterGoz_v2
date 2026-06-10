# Faza 1 — Home + 3 filary — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zbudować stronę główną (`/`) odwzorowującą `mockup/index.html` oraz trzy strony-filary (`/klaster`, `/edukacja`, `/doradztwo`) jako landingi — wszystko w pełni edytowalne w panelu Wagtail (zero hardkodu), z `HomePage` ustawioną jako root portalu.

**Architecture:** `HomePage` i `PillarPage` dziedziczą z `BasePage` (SEO z Fazy 0). Treść powtarzalna (slajdy hero, filary, kroki, kafelki usług, logosy, teasery aktualności, korzyści) to **Orderable inline children**; sekcje nagłówkowe to pola strukturalne; statystyki to reużywalny snippet `Statistic` (grupowany), a `HeroSlide`/`Pillar` to snippety wybierane na HomePage. Re-rooting (HomePage jako `Site.root_page` + przeniesienie stron prawnych/kontaktu z Fazy 0 pod nią) realizuje rozszerzona komenda `seed_initial_content`. Slider hero = wydzielony vanilla JS.

**Tech Stack:** Wagtail 6.3 / Django 5.1 / Python 3.13 / PostgreSQL / Redis. Testy: pytest + pytest-django (SQLite in-memory, `--create-db`). Brak nowych zależności.

---

## Decyzje implementacyjne (do potwierdzenia przy review planu)

1. **Jeden typ `PillarPage` zamiast trzech** (spec 5.1 wymienia osobne `KlasterPillarPage`/`AkademiaPillarPage`/`DoradztwoPillarPage`). Trzy landingi filarów dzielą tę samą strukturę (hero + korzyści + blok „jak działamy" + kroki procesu + CTA + auto-listing dzieci), różnią się treścią pól i dziećmi. Jeden parametryzowany typ = DRY i mniej kodu; specjalizacje (np. teaser trenerów Akademii) dochodzą w Fazie 3, gdy istnieje ich treść. Jeśli wolisz trzy osobne typy — zgłoś.

2. **Sekcje home odwołujące się do treści z późniejszych faz** (kafelki usług, logosy członków, teasery aktualności) modelujemy **teraz jako edytowalne Orderable inline children** na `HomePage` (spełnia DoD „zero hardkodu"). W Fazach 2/4 mogą zostać zastąpione auto-pobieraniem z prawdziwych modeli (ServicePage / Member / ArticlePage), ale w Fazie 1 redaktor zarządza nimi ręcznie. Flaga: to świadomy tymczasowy duplikat danych.

3. **Statystyki** = snippet `Statistic` z polem `group` (`home_strip` / `home_section`), pobierane w `get_context` HomePage i renderowane w odpowiednich paskach. Edytowalne raz, reużywalne.

4. **Re-rooting przez komendę `seed_initial_content`** (nie migrację): tworzy `HomePage` pod korzeniem drzewa, ustawia ją jako `Site.root_page`, przenosi strony prawne/kontakt z Fazy 0 pod `HomePage`, usuwa domyślną stronę „Welcome" Wagtaila. Idempotentne. Spójne z decyzją z Fazy 0 (seed = komenda, nie migracja → brak kolizji w testach).

5. **Snippety i strony Fazy 1 w `apps/home/models.py`** (jeden plik, spójnie z istniejącym wzorcem `apps/shared/models.py` / `apps/pages/models.py`). HeroSlide/Pillar/Statistic to snippety; HomePage/PillarPage to strony.

---

## Mapa plików

- Modify: `apps/home/models.py` — snippety (HeroSlide, Pillar, Statistic) + HomePage (+ orderable children) + PillarPage (+ orderable children)
- Create: `apps/home/migrations/` (przez makemigrations)
- Create: `apps/home/templates/home/home_page.html`
- Create: `apps/home/templates/home/pillar_page.html`
- Create: `static/js/hero-slider.js` (wydzielony z `mockup/index.html`)
- Modify: `templates/base.html` — dodać blok `{% block body_class %}` (już jest `body_attrs`) — NIE; użyjemy istniejącego `extra_js` do dołączenia slidera tylko na home
- Modify: `apps/pages/management/commands/seed_initial_content.py` — re-rooting + HomePage + 3 PillarPages + wiring
- Modify: `apps/home/tests/` — testy (snippety, PillarPage, HomePage, re-rooting, render)
- Create: `apps/home/tests/__init__.py`, `test_snippets.py`, `test_pillar_page.py`, `test_home_page.py`
- Modify: `apps/pages/tests/test_seed.py` — rozszerzyć o re-rooting
- Create: `apps/home/README.md`

---

## Konwencje testów (jak w Fazie 0)

- Uruchamianie: `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db <ścieżka> -v` (uv nie jest na PATH; settings testowe w pyproject → SQLite in-memory).
- DB: `@pytest.mark.django_db`.
- `makemigrations`/`check` mogą wypisać benignny warning Postgres connection timeout (dev DB nie działa w testach) — to normalne, exit 0.
- Tworzenie stron pod korzeniem domyślnego Site:
```python
import pytest
from wagtail.models import Page, Site

@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page
```

---

## Task 1: Snippety — HeroSlide, Pillar, Statistic

**Files:**
- Modify: `apps/home/models.py`
- Create: `apps/home/tests/__init__.py`, `apps/home/tests/test_snippets.py`

- [ ] **Step 1: Napisz snippety w `apps/home/models.py`**

Create/replace `apps/home/models.py` with:
```python
"""Modele strony głównej i filarów: snippety (HeroSlide, Pillar, Statistic), HomePage, PillarPage."""
from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField


@register_snippet
class HeroSlide(models.Model):
    """Slajd hero na stronie głównej (3 sztuki wg mockupu)."""

    eyebrow = models.CharField("Nadtytuł (eyebrow)", max_length=120, blank=True)
    headline = RichTextField(
        "Nagłówek",
        features=["italic"],
        help_text="Użyj kursywy (em) dla akcentu, jak w mockupie.",
    )
    lead = models.TextField("Lead", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Tło slajdu.",
    )
    primary_cta_label = models.CharField("CTA główne — tekst", max_length=60, blank=True)
    primary_cta_url = models.CharField("CTA główne — URL", max_length=255, blank=True)
    secondary_cta_label = models.CharField("CTA drugie — tekst", max_length=60, blank=True)
    secondary_cta_url = models.CharField("CTA drugie — URL", max_length=255, blank=True)

    panels = [
        FieldPanel("eyebrow"),
        FieldPanel("headline"),
        FieldPanel("lead"),
        FieldPanel("image"),
        FieldPanel("primary_cta_label"),
        FieldPanel("primary_cta_url"),
        FieldPanel("secondary_cta_label"),
        FieldPanel("secondary_cta_url"),
    ]

    def __str__(self):
        return self.eyebrow or (self.lead[:40] if self.lead else "Slajd hero")

    class Meta:
        verbose_name = "Slajd hero"
        verbose_name_plural = "Slajdy hero"


@register_snippet
class Pillar(models.Model):
    """Filar (3 sztuki) — kafelek na home, linkuje do strony-filaru."""

    number = models.CharField("Numer", max_length=12, help_text="np. '01 / FILAR'")
    title = models.CharField("Tytuł", max_length=120)
    lead = models.TextField("Opis")
    bullets = models.TextField("Punkty (jeden na linię)", blank=True)
    icon_svg = models.TextField(
        "Ikona (inline SVG)", blank=True, help_text="Wklej kod <svg>…</svg>."
    )
    link = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Strona-filar docelowa.",
    )
    cta_label = models.CharField("Tekst linku", max_length=60, blank=True)
    is_dark = models.BooleanField("Wariant ciemny", default=False)

    panels = [
        FieldPanel("number"),
        FieldPanel("title"),
        FieldPanel("lead"),
        FieldPanel("bullets"),
        FieldPanel("icon_svg"),
        FieldPanel("link"),
        FieldPanel("cta_label"),
        FieldPanel("is_dark"),
    ]

    def bullet_list(self) -> list[str]:
        return [b.strip() for b in self.bullets.splitlines() if b.strip()]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Filar"
        verbose_name_plural = "Filary"


@register_snippet
class Statistic(models.Model):
    """Statystyka liczbowa (paski na home)."""

    GROUP_CHOICES = [
        ("home_strip", "Home — pasek pod hero"),
        ("home_section", "Home — sekcja statystyk"),
        ("about_klastra", "O klastrze"),
    ]
    value = models.CharField("Wartość", max_length=40, help_text="np. '150+' lub '240 mln zł'")
    label = models.CharField("Opis", max_length=160)
    group = models.CharField("Grupa", max_length=20, choices=GROUP_CHOICES, default="home_strip")
    sort_order = models.IntegerField("Kolejność", default=0)

    panels = [FieldPanel("value"), FieldPanel("label"), FieldPanel("group"), FieldPanel("sort_order")]

    def __str__(self):
        return f"{self.value} — {self.label}"

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Statystyka"
        verbose_name_plural = "Statystyki"
```

- [ ] **Step 2: Migracja** — `& C:\Users\tmrow\.local\bin\uv.exe run python manage.py makemigrations home` → `0001_initial.py` (HeroSlide, Pillar, Statistic).

- [ ] **Step 3: Testy** — Create `apps/home/tests/__init__.py` (pusty) i `apps/home/tests/test_snippets.py`:
```python
import pytest

from apps.home.models import HeroSlide, Pillar, Statistic


@pytest.mark.django_db
def test_heroslide_str_uses_eyebrow():
    s = HeroSlide.objects.create(eyebrow="Platforma KLASTERBOX", headline="<p>X</p>")
    assert str(s) == "Platforma KLASTERBOX"


@pytest.mark.django_db
def test_pillar_bullet_list_splits_lines():
    p = Pillar.objects.create(number="01 / FILAR", title="Klaster", lead="...", bullets="A\nB\n\nC")
    assert p.bullet_list() == ["A", "B", "C"]


@pytest.mark.django_db
def test_statistic_str_and_ordering():
    Statistic.objects.create(value="12", label="lat", group="home_strip", sort_order=1)
    Statistic.objects.create(value="150+", label="firm", group="home_strip", sort_order=0)
    first = Statistic.objects.filter(group="home_strip").first()
    assert first.value == "150+"
    assert str(first) == "150+ — firm"
```

- [ ] **Step 4: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/home/tests/test_snippets.py -v` → 3 PASSED. `manage.py check` clean.

- [ ] **Step 5: Commit**
```
git add apps/home/models.py apps/home/migrations/ apps/home/tests/__init__.py apps/home/tests/test_snippets.py
git commit -m "feat(faza-1): snippety HeroSlide + Pillar + Statistic" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: PillarPage (landing filaru)

Wspólny typ dla `/klaster`, `/edukacja`, `/doradztwo`. Struktura wg `mockup/klaster.html`: hero (eyebrow filaru + h1 + lead + 2 CTA), sekcja korzyści (kafelki), blok „jak działamy" (tekst + punkty), kroki procesu (4), CTA strip, auto-listing dzieci.

**Files:**
- Modify: `apps/home/models.py` (append PillarPage + orderables)
- Create: `apps/home/templates/home/pillar_page.html`
- Create: `apps/home/tests/test_pillar_page.py`

- [ ] **Step 1: Rozszerz importy na górze `apps/home/models.py`** (dodaj do istniejących):
```python
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable

from apps.shared.models import BasePage
```

- [ ] **Step 2: Append PillarPage + orderables na końcu `apps/home/models.py`:**
```python
class PillarBenefit(Orderable):
    """Kafelek korzyści na stronie-filarze."""

    page = ParentalKey("PillarPage", on_delete=models.CASCADE, related_name="benefits")
    tag = models.CharField("Tag", max_length=40, blank=True)
    title = models.CharField("Tytuł", max_length=120)
    description = models.TextField("Opis", blank=True)

    panels = [FieldPanel("tag"), FieldPanel("title"), FieldPanel("description")]


class PillarStep(Orderable):
    """Krok procesu (np. jak dołączyć)."""

    page = ParentalKey("PillarPage", on_delete=models.CASCADE, related_name="steps")
    number = models.CharField("Numer", max_length=4, help_text="np. '01'")
    title = models.CharField("Tytuł", max_length=80)
    description = models.TextField("Opis", blank=True)

    panels = [FieldPanel("number"), FieldPanel("title"), FieldPanel("description")]


class PillarPage(BasePage):
    """Landing filaru (Klaster / Edukacja / Doradztwo). Jeden typ, 3 instancje."""

    eyebrow = models.CharField("Nadtytuł (np. 'Filar 01 · Klaster')", max_length=120, blank=True)
    hero_lead = models.TextField("Lead w hero", blank=True)
    primary_cta_label = models.CharField("CTA główne — tekst", max_length=60, blank=True)
    primary_cta_url = models.CharField("CTA główne — URL", max_length=255, blank=True)
    secondary_cta_label = models.CharField("CTA drugie — tekst", max_length=60, blank=True)
    secondary_cta_url = models.CharField("CTA drugie — URL", max_length=255, blank=True)

    benefits_heading = models.CharField("Nagłówek sekcji korzyści", max_length=160, blank=True)

    feature_heading = models.CharField("Blok 'jak działamy' — nagłówek", max_length=160, blank=True)
    feature_lead = models.TextField("Blok 'jak działamy' — lead", blank=True)
    feature_bullets = models.TextField("Blok 'jak działamy' — punkty (jeden na linię)", blank=True)

    steps_heading = models.CharField("Nagłówek sekcji procesu", max_length=160, blank=True)

    cta_heading = models.CharField("CTA strip — nagłówek", max_length=200, blank=True)
    cta_lead = models.TextField("CTA strip — lead", blank=True)
    cta_button_label = models.CharField("CTA strip — przycisk", max_length=60, blank=True)
    cta_button_url = models.CharField("CTA strip — URL", max_length=255, blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("eyebrow"),
                FieldPanel("hero_lead"),
                FieldPanel("primary_cta_label"),
                FieldPanel("primary_cta_url"),
                FieldPanel("secondary_cta_label"),
                FieldPanel("secondary_cta_url"),
            ],
            heading="Hero",
        ),
        FieldPanel("benefits_heading"),
        InlinePanel("benefits", label="Korzyści"),
        MultiFieldPanel(
            [FieldPanel("feature_heading"), FieldPanel("feature_lead"), FieldPanel("feature_bullets")],
            heading="Blok 'jak działamy'",
        ),
        FieldPanel("steps_heading"),
        InlinePanel("steps", label="Kroki procesu"),
        MultiFieldPanel(
            [
                FieldPanel("cta_heading"),
                FieldPanel("cta_lead"),
                FieldPanel("cta_button_label"),
                FieldPanel("cta_button_url"),
            ],
            heading="CTA strip",
        ),
    ]
    promote_panels = BasePage.promote_panels
    template = "home/pillar_page.html"

    def feature_bullet_list(self) -> list[str]:
        return [b.strip() for b in self.feature_bullets.splitlines() if b.strip()]

    def get_context(self, request):
        ctx = super().get_context(request)
        # Żywe dzieci strony-filaru (puste w Fazie 1 — podstrony dochodzą w Fazach 2–4).
        ctx["children"] = self.get_children().live().specific()
        return ctx

    class Meta:
        verbose_name = "Strona filaru"
        verbose_name_plural = "Strony filarów"
```

- [ ] **Step 3: Szablon `apps/home/templates/home/pillar_page.html`:**
```django
{% extends "base.html" %}
{% load static wagtailcore_tags %}

{% block body_attrs %}data-page="{{ page.slug }}"{% endblock %}

{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li><li>{{ page.title }}</li></ul>
    {% if page.eyebrow %}<span class="eyebrow">{{ page.eyebrow }}</span>{% endif %}
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.hero_lead %}<p class="lead">{{ page.hero_lead }}</p>{% endif %}
    <div style="display: flex; gap: 12px; margin-top: 28px; flex-wrap: wrap;">
      {% if page.primary_cta_label %}<a href="{{ page.primary_cta_url|default:'#' }}" class="btn btn--primary">{{ page.primary_cta_label }} <span class="arr">→</span></a>{% endif %}
      {% if page.secondary_cta_label %}<a href="{{ page.secondary_cta_url|default:'#' }}" class="btn btn--ghost">{{ page.secondary_cta_label }}</a>{% endif %}
    </div>
  </div>
</section>

{% if page.benefits.all %}
<section class="section">
  <div class="container">
    {% if page.benefits_heading %}<div class="section-head"><div><h2>{{ page.benefits_heading }}</h2></div></div>{% endif %}
    <div class="offerings">
      {% for b in page.benefits.all %}
      <div class="offering">
        {% if b.tag %}<span class="tag">{{ b.tag }}</span>{% endif %}
        <h3>{{ b.title }}</h3>
        {% if b.description %}<p>{{ b.description }}</p>{% endif %}
      </div>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.feature_heading %}
<section class="section bg-green">
  <div class="container feature">
    <div class="feature-img"><span>{{ page.feature_heading }}</span></div>
    <div class="feature-text">
      <h2 style="margin-top: 14px;">{{ page.feature_heading }}</h2>
      {% if page.feature_lead %}<p class="lead muted">{{ page.feature_lead }}</p>{% endif %}
      {% if page.feature_bullet_list %}<ul>{% for li in page.feature_bullet_list %}<li>{{ li }}</li>{% endfor %}</ul>{% endif %}
    </div>
  </div>
</section>
{% endif %}

{% if page.steps.all %}
<section class="section">
  <div class="container">
    {% if page.steps_heading %}<div class="section-head"><div><h2>{{ page.steps_heading }}</h2></div></div>{% endif %}
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px;">
      {% for s in page.steps.all %}
      <div style="background: var(--white); border: 1px solid var(--ink-100); border-radius: 18px; padding: 28px;">
        <strong style="font-family: var(--font-display); font-size: 32px; color: var(--green-700); display: block;">{{ s.number }}</strong>
        <h4 style="margin: 12px 0 8px;">{{ s.title }}</h4>
        <p style="margin: 0; font-size: 14.5px; color: var(--ink-500);">{{ s.description }}</p>
      </div>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if children %}
<section class="section--tight">
  <div class="container">
    <div class="offerings">
      {% for child in children %}
      <a href="{% pageurl child %}" class="offering"><h3>{{ child.title }}</h3>{% if child.search_description %}<p>{{ child.search_description }}</p>{% endif %}<span class="more">Zobacz →</span></a>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.cta_heading %}
<section class="section--tight">
  <div class="container">
    <div class="cta-strip">
      <div>
        <h2>{{ page.cta_heading }}</h2>
        {% if page.cta_lead %}<p>{{ page.cta_lead }}</p>{% endif %}
      </div>
      {% if page.cta_button_label %}<div style="display:flex; gap:12px; flex-wrap:wrap;"><a href="{{ page.cta_button_url|default:'#' }}" class="btn btn--accent">{{ page.cta_button_label }} <span class="arr">→</span></a></div>{% endif %}
    </div>
  </div>
</section>
{% endif %}
{% endblock %}
```

- [ ] **Step 4: Migracja** — `makemigrations home` → migracja z PillarPage, PillarBenefit, PillarStep.

- [ ] **Step 5: Test `apps/home/tests/test_pillar_page.py`:**
```python
import pytest
from django.test import Client
from wagtail.models import Site

from apps.home.models import PillarPage, PillarBenefit


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.mark.django_db
def test_pillar_page_renders(root_page):
    page = PillarPage(
        title="Klaster ogólnokrajowy",
        slug="klaster",
        eyebrow="Filar 01 · Klaster",
        hero_lead="150+ firm i instytucji.",
        benefits_heading="Konkretne korzyści członkostwa.",
        feature_bullets="Przedsiębiorstwa\nUczelnie\nSamorząd",
    )
    root_page.add_child(instance=page)
    page.benefits.add(PillarBenefit(tag="Networking", title="150+ partnerów", description="..."))
    page.save_revision().publish()

    resp = Client().get("/klaster/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Klaster ogólnokrajowy" in html
    assert "Filar 01 · Klaster" in html
    assert "150+ partnerów" in html
    assert "site-header" in html  # chrome z Fazy 0


@pytest.mark.django_db
def test_feature_bullet_list(root_page):
    page = PillarPage(title="X", slug="x", feature_bullets="A\n\nB")
    root_page.add_child(instance=page)
    assert page.feature_bullet_list() == ["A", "B"]
```

- [ ] **Step 6: Run** `pytest --create-db apps/home/tests/test_pillar_page.py -v` → 2 PASSED. `manage.py check` clean.

- [ ] **Step 7: Commit**
```
git add apps/home/models.py apps/home/migrations/ apps/home/templates/home/pillar_page.html apps/home/tests/test_pillar_page.py
git commit -m "feat(faza-1): PillarPage (landing filaru) + szablon + testy" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: HomePage — model

Bogata strona główna. Sekcje nagłówkowe = pola; powtarzalne = Orderable children; slajdy hero i filary = wybór snippetów; statystyki = z `Statistic` w `get_context`.

**Files:**
- Modify: `apps/home/models.py` (append HomePage + orderables)
- Create: `apps/home/tests/test_home_page.py`

- [ ] **Step 1: Append na końcu `apps/home/models.py`:**
```python
class HomeHeroSlide(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="hero_slides")
    slide = models.ForeignKey("home.HeroSlide", on_delete=models.CASCADE, related_name="+")
    panels = [FieldPanel("slide")]


class HomePillar(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="home_pillars")
    pillar = models.ForeignKey("home.Pillar", on_delete=models.CASCADE, related_name="+")
    panels = [FieldPanel("pillar")]


class HomeConsultStep(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="consult_steps")
    text = models.CharField("Krok", max_length=200)
    panels = [FieldPanel("text")]


class HomeOffering(Orderable):
    """Kafelek usługi (sekcja 'Usługi klastra'). W Fazie 2 może zostać zastąpiony auto-listą ServicePage."""

    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="offerings")
    tag = models.CharField("Tag", max_length=40, blank=True)
    title = models.CharField("Tytuł", max_length=120)
    description = models.TextField("Opis", blank=True)
    link_label = models.CharField("Tekst linku", max_length=60, blank=True, default="Dowiedz się więcej →")
    url = models.CharField("URL", max_length=255, blank=True)
    panels = [FieldPanel("tag"), FieldPanel("title"), FieldPanel("description"), FieldPanel("link_label"), FieldPanel("url")]


class HomeMemberLogo(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="member_logos")
    name = models.CharField("Nazwa", max_length=80)
    logo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    panels = [FieldPanel("name"), FieldPanel("logo")]


class HomeNewsTeaser(Orderable):
    """Teaser aktualności. W Fazie 4 może zostać zastąpiony auto-listą ArticlePage."""

    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="news_teasers")
    category = models.CharField("Kategoria", max_length=40, blank=True)
    reading_time = models.CharField("Czas czytania", max_length=20, blank=True)
    date = models.CharField("Data", max_length=20, blank=True)
    title = models.CharField("Tytuł", max_length=200)
    excerpt = models.TextField("Zajawka", blank=True)
    url = models.CharField("URL", max_length=255, blank=True)
    panels = [FieldPanel("category"), FieldPanel("reading_time"), FieldPanel("date"), FieldPanel("title"), FieldPanel("excerpt"), FieldPanel("url")]


class HomePage(BasePage):
    """Strona główna portalu (root Site)."""

    # Pasek pod hero + sekcja stats korzystają z Statistic (grupy), reszta to pola.
    pillars_eyebrow = models.CharField(max_length=80, blank=True, default="Co robimy")
    pillars_heading = models.CharField(max_length=200, blank=True)
    pillars_lead = models.TextField(blank=True)

    consult_eyebrow = models.CharField(max_length=80, blank=True, default="Bezpłatna konsultacja")
    consult_heading = models.CharField(max_length=200, blank=True)
    consult_lead = models.TextField(blank=True)
    consult_cta_label = models.CharField(max_length=60, blank=True, default="Wyślij zgłoszenie")
    consult_cta_url = models.CharField(max_length=255, blank=True)

    services_eyebrow = models.CharField(max_length=80, blank=True, default="Usługi klastra")
    services_heading = models.CharField(max_length=200, blank=True)
    services_cta_label = models.CharField(max_length=60, blank=True, default="Cała oferta")
    services_cta_url = models.CharField(max_length=255, blank=True)

    members_eyebrow = models.CharField(max_length=80, blank=True, default="Zaufali nam")
    members_heading = models.CharField(max_length=200, blank=True)

    about_eyebrow = models.CharField(max_length=80, blank=True, default="O klastrze")
    about_heading = models.CharField(max_length=200, blank=True)
    about_lead = models.TextField(blank=True)
    about_bullets = models.TextField("Punkty (jeden na linię)", blank=True)
    about_cta_label = models.CharField(max_length=60, blank=True)
    about_cta_url = models.CharField(max_length=255, blank=True)
    about_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    news_eyebrow = models.CharField(max_length=80, blank=True, default="Aktualności")
    news_heading = models.CharField(max_length=200, blank=True)
    news_cta_label = models.CharField(max_length=60, blank=True, default="Wszystkie wpisy")
    news_cta_url = models.CharField(max_length=255, blank=True)

    cta_chip = models.CharField(max_length=60, blank=True, default="Krajowy Klaster Kluczowy")
    cta_heading = models.CharField(max_length=200, blank=True)
    cta_lead = models.TextField(blank=True)
    cta_primary_label = models.CharField(max_length=60, blank=True)
    cta_primary_url = models.CharField(max_length=255, blank=True)
    cta_secondary_label = models.CharField(max_length=60, blank=True)
    cta_secondary_url = models.CharField(max_length=255, blank=True)

    content_panels = BasePage.content_panels + [
        InlinePanel("hero_slides", label="Slajdy hero"),
        MultiFieldPanel([FieldPanel("pillars_eyebrow"), FieldPanel("pillars_heading"), FieldPanel("pillars_lead")], heading="Sekcja: Filary — nagłówek"),
        InlinePanel("home_pillars", label="Filary (kafelki)"),
        MultiFieldPanel([FieldPanel("consult_eyebrow"), FieldPanel("consult_heading"), FieldPanel("consult_lead"), FieldPanel("consult_cta_label"), FieldPanel("consult_cta_url")], heading="Sekcja: Konsultacja"),
        InlinePanel("consult_steps", label="Kroki konsultacji"),
        MultiFieldPanel([FieldPanel("services_eyebrow"), FieldPanel("services_heading"), FieldPanel("services_cta_label"), FieldPanel("services_cta_url")], heading="Sekcja: Usługi — nagłówek"),
        InlinePanel("offerings", label="Kafelki usług"),
        MultiFieldPanel([FieldPanel("members_eyebrow"), FieldPanel("members_heading")], heading="Sekcja: Członkowie — nagłówek"),
        InlinePanel("member_logos", label="Logosy członków"),
        MultiFieldPanel([FieldPanel("about_eyebrow"), FieldPanel("about_heading"), FieldPanel("about_lead"), FieldPanel("about_bullets"), FieldPanel("about_cta_label"), FieldPanel("about_cta_url"), FieldPanel("about_image")], heading="Sekcja: O klastrze"),
        MultiFieldPanel([FieldPanel("news_eyebrow"), FieldPanel("news_heading"), FieldPanel("news_cta_label"), FieldPanel("news_cta_url")], heading="Sekcja: Aktualności — nagłówek"),
        InlinePanel("news_teasers", label="Teasery aktualności"),
        MultiFieldPanel([FieldPanel("cta_chip"), FieldPanel("cta_heading"), FieldPanel("cta_lead"), FieldPanel("cta_primary_label"), FieldPanel("cta_primary_url"), FieldPanel("cta_secondary_label"), FieldPanel("cta_secondary_url")], heading="Sekcja: CTA strip"),
    ]
    promote_panels = BasePage.promote_panels
    template = "home/home_page.html"

    # Tylko jedna instancja HomePage (root); nie zezwalaj na tworzenie pod inne strony.
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    def about_bullet_list(self) -> list[str]:
        return [b.strip() for b in self.about_bullets.splitlines() if b.strip()]

    def get_context(self, request):
        from apps.home.models import Statistic
        ctx = super().get_context(request)
        ctx["stats_strip"] = Statistic.objects.filter(group="home_strip")
        ctx["stats_section"] = Statistic.objects.filter(group="home_section")
        return ctx

    class Meta:
        verbose_name = "Strona główna"
```

- [ ] **Step 2: Migracja** — `makemigrations home`.

- [ ] **Step 3: Test `apps/home/tests/test_home_page.py`** (model + stats context; render w Task 5):
```python
import pytest
from wagtail.models import Site

from apps.home.models import HomePage, HeroSlide, HomeHeroSlide, Statistic


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.mark.django_db
def test_homepage_about_bullets(root_page):
    hp = HomePage(title="Klaster GOZ", slug="home-test", about_bullets="A\nB\nC")
    root_page.add_child(instance=hp)
    assert hp.about_bullet_list() == ["A", "B", "C"]


@pytest.mark.django_db
def test_homepage_hero_slides_relation(root_page):
    hp = HomePage(title="Klaster GOZ", slug="home-test2")
    root_page.add_child(instance=hp)
    slide = HeroSlide.objects.create(eyebrow="X", headline="<p>H</p>")
    hp.hero_slides.add(HomeHeroSlide(slide=slide))
    hp.save_revision().publish()
    assert hp.hero_slides.count() == 1
    assert hp.hero_slides.first().slide.eyebrow == "X"


@pytest.mark.django_db
def test_homepage_max_count_one(root_page):
    # max_count nie blokuje na poziomie ORM, ale eksponuje limit w adminie; sprawdzamy atrybut
    assert HomePage.max_count == 1
```

- [ ] **Step 4: Run** `pytest --create-db apps/home/tests/test_home_page.py -v` → 3 PASSED. `manage.py check` clean.

- [ ] **Step 5: Commit**
```
git add apps/home/models.py apps/home/migrations/ apps/home/tests/test_home_page.py
git commit -m "feat(faza-1): model HomePage (sekcje + orderable children + stats context)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Hero slider — wydzielony JS

**Files:**
- Create: `static/js/hero-slider.js`

- [ ] **Step 1: Create `static/js/hero-slider.js`** — przenieś logikę z `mockup/index.html` (inline `<script>` od `// HERO SLIDER`), opakowaną w guard (działa tylko gdy slider istnieje):
```javascript
// Hero slider strony głównej. Vanilla, bez zależności. Aktywuje się tylko gdy na stronie jest #heroSlider.
(function () {
  "use strict";
  var root = document.getElementById("heroSlider");
  if (!root) return;

  var slides = root.querySelectorAll(".slide");
  var dots = document.querySelectorAll(".dot");
  var counter = document.getElementById("curSlide");
  var progress = document.querySelector(".slide-progress-bar");
  var pauseBtn = document.getElementById("pauseBtn");
  if (!slides.length) return;

  var idx = 0, timer = null, paused = false;
  var DURATION = 6000;

  function go(n, manual) {
    idx = (n + slides.length) % slides.length;
    slides.forEach(function (s, i) { s.classList.toggle("is-active", i === idx); });
    dots.forEach(function (d, i) { d.classList.toggle("is-active", i === idx); });
    if (counter) counter.textContent = String(idx + 1).padStart(2, "0");
    if (progress) {
      progress.style.animation = "none";
      void progress.offsetHeight; // reflow
      if (!paused) progress.style.animation = "slideProgress " + DURATION + "ms linear forwards";
    }
    if (manual) restart();
  }
  function tick() { go(idx + 1); }
  function start() { timer = setInterval(tick, DURATION); }
  function stop() { clearInterval(timer); }
  function restart() { stop(); if (!paused) start(); }

  document.querySelectorAll("[data-dir]").forEach(function (b) {
    b.addEventListener("click", function () { go(idx + parseInt(b.dataset.dir, 10), true); });
  });
  dots.forEach(function (d) {
    d.addEventListener("click", function () { go(parseInt(d.dataset.go, 10), true); });
  });
  if (pauseBtn) {
    pauseBtn.addEventListener("click", function () {
      paused = !paused;
      pauseBtn.classList.toggle("is-paused", paused);
      pauseBtn.innerHTML = paused
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20"></polygon></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>';
      if (paused) { stop(); if (progress) progress.style.animationPlayState = "paused"; }
      else { restart(); if (progress) progress.style.animationPlayState = "running"; }
    });
  }

  go(0);
  start();
})();
```

- [ ] **Step 2: Sprawdź** `manage.py check` clean (brak zmian modeli). Plik zostanie dołączony w szablonie home (Task 5).

- [ ] **Step 3: Commit**
```
git add static/js/hero-slider.js
git commit -m "feat(faza-1): wydzielony hero-slider.js (z mockupu, z guardem)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: HomePage — szablon (port mockup/index.html)

**Files:**
- Create: `apps/home/templates/home/home_page.html`
- Test: `apps/home/tests/test_home_page.py` (dopisanie render testu)

- [ ] **Step 1: Create `apps/home/templates/home/home_page.html`** — odwzorowanie 10 sekcji z `mockup/index.html`, sterowane polami/relacjami. Hero slajdy z `page.hero_slides.all` (każdy `.slide`), nawigacja slidera statyczna, stats z kontekstu, filary z `page.home_pillars.all`, itd. Dołącz slider JS w `extra_js`.
```django
{% extends "base.html" %}
{% load static wagtailcore_tags wagtailimages_tags %}

{% block body_attrs %}data-page="home"{% endblock %}

{% block content %}
{% if page.hero_slides.all %}
<section class="hero-slider" id="heroSlider">
  <div class="slider-track">
    {% for item in page.hero_slides.all %}{% with s=item.slide %}
    <article class="slide{% if forloop.first %} is-active{% endif %}" data-slide="{{ forloop.counter0 }}">
      {% if s.image %}{% image s.image fill-1920x1080 as bg %}<div class="slide-bg" style="background-image: url('{{ bg.url }}');"></div>{% else %}<div class="slide-bg"></div>{% endif %}
      <div class="slide-overlay"></div>
      <div class="container slide-inner">
        {% if s.eyebrow %}<span class="eyebrow" style="color: var(--lime-300);">{{ s.eyebrow }}</span>{% endif %}
        <h1>{{ s.headline|richtext }}</h1>
        {% if s.lead %}<p class="hero-lead">{{ s.lead }}</p>{% endif %}
        <div class="hero-ctas">
          {% if s.primary_cta_label %}<a href="{{ s.primary_cta_url|default:'#' }}" class="btn btn--accent">{{ s.primary_cta_label }} <span class="arr">→</span></a>{% endif %}
          {% if s.secondary_cta_label %}<a href="{{ s.secondary_cta_url|default:'#' }}" class="btn btn--light">{{ s.secondary_cta_label }}</a>{% endif %}
        </div>
      </div>
    </article>
    {% endwith %}{% endfor %}
  </div>
  <div class="slider-nav container">
    <div class="slider-meta">
      <span class="slide-counter"><span id="curSlide">01</span><span class="of">/</span><span>{{ page.hero_slides.all|length|stringformat:"02d" }}</span></span>
      <span class="slide-progress"><span class="slide-progress-bar"></span></span>
    </div>
    <div class="slider-controls">
      <button class="slider-btn" data-dir="-1" aria-label="Poprzedni"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg></button>
      <button class="slider-btn slider-btn--pause" id="pauseBtn" aria-label="Pauza"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg></button>
      <button class="slider-btn" data-dir="1" aria-label="Następny"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg></button>
    </div>
    <div class="slider-dots">
      {% for item in page.hero_slides.all %}<button class="dot{% if forloop.first %} is-active{% endif %}" data-go="{{ forloop.counter0 }}" aria-label="Slajd {{ forloop.counter }}"></button>{% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if stats_strip %}
<section class="hero-stats-strip">
  <div class="container">
    {% for st in stats_strip %}<div class="hsm"><strong>{{ st.value }}</strong><span>{{ st.label }}</span></div>{% endfor %}
  </div>
</section>
{% endif %}

{% if page.home_pillars.all %}
<section class="section">
  <div class="container">
    <div class="pillars-head">
      <div>{% if page.pillars_eyebrow %}<span class="eyebrow">{{ page.pillars_eyebrow }}</span>{% endif %}{% if page.pillars_heading %}<h2 style="margin-top: 14px;">{{ page.pillars_heading }}</h2>{% endif %}</div>
      {% if page.pillars_lead %}<p class="lead muted">{{ page.pillars_lead }}</p>{% endif %}
    </div>
    <div class="pillars-grid">
      {% for item in page.home_pillars.all %}{% with p=item.pillar %}
      <a href="{% if p.link %}{{ p.link.url }}{% else %}#{% endif %}" class="pillar{% if p.is_dark %} pillar--dark{% endif %}">
        <span class="num">{{ p.number }}</span>
        {% if p.icon_svg %}<span class="ico">{{ p.icon_svg|safe }}</span>{% endif %}
        <h3>{{ p.title }}</h3>
        <p>{{ p.lead }}</p>
        {% if p.bullet_list %}<ul>{% for li in p.bullet_list %}<li>{{ li }}</li>{% endfor %}</ul>{% endif %}
        {% if p.cta_label %}<span class="pill-link">{{ p.cta_label }}</span>{% endif %}
      </a>
      {% endwith %}{% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.consult_heading %}
<section class="section bg-green">
  <div class="container consult">
    <div>
      {% if page.consult_eyebrow %}<span class="eyebrow">{{ page.consult_eyebrow }}</span>{% endif %}
      <h2 style="margin-top: 14px;">{{ page.consult_heading }}</h2>
      {% if page.consult_lead %}<p class="lead muted" style="max-width: 520px;">{{ page.consult_lead }}</p>{% endif %}
      {% if page.consult_steps.all %}
      <ul style="list-style: none; padding: 0; margin: 28px 0 0; display: grid; gap: 12px;">
        {% for step in page.consult_steps.all %}
        <li style="display: flex; gap: 12px; align-items: center; font-size: 15px;"><span style="width: 28px; height: 28px; background: var(--green-700); color: #fff; border-radius: 50%; display: grid; place-items: center; font-weight: 700; font-size: 13px;">{{ forloop.counter }}</span>{{ step.text }}</li>
        {% endfor %}
      </ul>
      {% endif %}
    </div>
    <div class="consult-form-wrap">
      <p class="muted">Formularz konsultacji — pełna obsługa w Fazie 2. Tymczasowo skontaktuj się przez <a href="{{ page.consult_cta_url|default:'/kontakt/' }}" style="text-decoration:underline;">stronę kontaktu</a>.</p>
      <a href="{{ page.consult_cta_url|default:'/kontakt/' }}" class="btn btn--primary" style="margin-top:16px;">{{ page.consult_cta_label }} <span class="arr">→</span></a>
    </div>
  </div>
</section>
{% endif %}

{% if stats_section %}
<section class="section--tight">
  <div class="container">
    <div class="stats">
      {% for st in stats_section %}<div class="stat-item"><strong>{{ st.value }}</strong><span>{{ st.label }}</span></div>{% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.offerings.all %}
<section class="section">
  <div class="container">
    <div class="section-head">
      <div>{% if page.services_eyebrow %}<span class="eyebrow">{{ page.services_eyebrow }}</span>{% endif %}{% if page.services_heading %}<h2 style="margin-top: 14px;">{{ page.services_heading }}</h2>{% endif %}</div>
      {% if page.services_cta_label %}<a href="{{ page.services_cta_url|default:'#' }}" class="btn btn--ghost">{{ page.services_cta_label }} <span class="arr">→</span></a>{% endif %}
    </div>
    <div class="offerings">
      {% for o in page.offerings.all %}
      <a href="{{ o.url|default:'#' }}" class="offering">{% if o.tag %}<span class="tag">{{ o.tag }}</span>{% endif %}<h3>{{ o.title }}</h3><p>{{ o.description }}</p>{% if o.link_label %}<span class="more">{{ o.link_label }}</span>{% endif %}</a>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.member_logos.all %}
<section class="section--tight">
  <div class="container">
    <div style="text-align: center; margin-bottom: 36px;">{% if page.members_eyebrow %}<span class="eyebrow">{{ page.members_eyebrow }}</span>{% endif %}{% if page.members_heading %}<h3 style="margin-top: 12px; font-size: 24px;">{{ page.members_heading }}</h3>{% endif %}</div>
    <div class="logos">
      {% for m in page.member_logos.all %}<div>{% if m.logo %}{% image m.logo height-40 alt=m.name %}{% else %}{{ m.name }}{% endif %}</div>{% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.about_heading %}
<section class="section">
  <div class="container feature feature--reverse">
    <div class="feature-text">
      {% if page.about_eyebrow %}<span class="eyebrow">{{ page.about_eyebrow }}</span>{% endif %}
      <h2 style="margin-top: 14px;">{{ page.about_heading }}</h2>
      {% if page.about_lead %}<p class="lead muted">{{ page.about_lead }}</p>{% endif %}
      {% if page.about_bullet_list %}<ul>{% for li in page.about_bullet_list %}<li>{{ li }}</li>{% endfor %}</ul>{% endif %}
      {% if page.about_cta_label %}<div style="display: flex; gap: 12px;"><a href="{{ page.about_cta_url|default:'#' }}" class="btn btn--primary">{{ page.about_cta_label }} <span class="arr">→</span></a></div>{% endif %}
    </div>
    <div class="feature-img">{% if page.about_image %}{% image page.about_image fill-800x600 %}{% else %}<span>Zdjęcie / wideo</span>{% endif %}</div>
  </div>
</section>
{% endif %}

{% if page.news_teasers.all %}
<section class="section bg-green">
  <div class="container">
    <div class="section-head">
      <div>{% if page.news_eyebrow %}<span class="eyebrow">{{ page.news_eyebrow }}</span>{% endif %}{% if page.news_heading %}<h2 style="margin-top: 14px;">{{ page.news_heading }}</h2>{% endif %}</div>
      {% if page.news_cta_label %}<a href="{{ page.news_cta_url|default:'#' }}" class="btn btn--ghost">{{ page.news_cta_label }} <span class="arr">→</span></a>{% endif %}
    </div>
    <div class="cards">
      {% for n in page.news_teasers.all %}
      <a href="{{ n.url|default:'#' }}" class="card">
        <div class="card-img" data-color="{{ forloop.counter }}"><span>okładka</span></div>
        <div class="card-body">
          <div class="card-meta">{% if n.category %}<span>{{ n.category }}</span><span class="dot"></span>{% endif %}{% if n.reading_time %}<span>{{ n.reading_time }}</span><span class="dot"></span>{% endif %}{% if n.date %}<span>{{ n.date }}</span>{% endif %}</div>
          <h3>{{ n.title }}</h3>{% if n.excerpt %}<p>{{ n.excerpt }}</p>{% endif %}<span class="read">Czytaj →</span>
        </div>
      </a>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.cta_heading %}
<section class="section--tight">
  <div class="container">
    <div class="cta-strip">
      <div>{% if page.cta_chip %}<span class="chip chip--lime">{{ page.cta_chip }}</span>{% endif %}<h2 style="margin-top: 14px;">{{ page.cta_heading }}</h2>{% if page.cta_lead %}<p>{{ page.cta_lead }}</p>{% endif %}</div>
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        {% if page.cta_primary_label %}<a href="{{ page.cta_primary_url|default:'#' }}" class="btn btn--accent">{{ page.cta_primary_label }} <span class="arr">→</span></a>{% endif %}
        {% if page.cta_secondary_label %}<a href="{{ page.cta_secondary_url|default:'#' }}" class="btn btn--light">{{ page.cta_secondary_label }}</a>{% endif %}
      </div>
    </div>
  </div>
</section>
{% endif %}
{% endblock %}

{% block extra_js %}<script src="{% static 'js/hero-slider.js' %}" defer></script>{% endblock %}
```

> Uwaga: sekcja konsultacji renderuje teraz CTA do `/kontakt/` zamiast działającego formularza inline (pełny formularz konsultacji = Faza 2, model `ConsultationRequest`). To świadomy placeholder — opisany w treści, nie hardkod treści biznesowej.

- [ ] **Step 2: Dopisz render test do `apps/home/tests/test_home_page.py`:**
```python
from django.test import Client
from apps.home.models import HomePillar, Pillar, Statistic


@pytest.mark.django_db
def test_homepage_renders_at_root(root_page):
    hp = HomePage(title="Klaster GOZ", slug="home-root", pillars_heading="Trzy filary")
    root_page.add_child(instance=hp)
    slide = HeroSlide.objects.create(eyebrow="KLASTERBOX", headline="<p>Najnowsza <em>platforma</em></p>", lead="Lead hero")
    hp.hero_slides.add(HomeHeroSlide(slide=slide))
    pillar = Pillar.objects.create(number="01 / FILAR", title="Klaster ogólnokrajowy", lead="...")
    hp.home_pillars.add(HomePillar(pillar=pillar))
    hp.save_revision().publish()
    Statistic.objects.create(value="150+", label="firm", group="home_strip", sort_order=0)

    # uczyń HomePage rootem Site, żeby URL = /
    site = Site.objects.get(is_default_site=True)
    site.root_page = hp
    site.save()

    resp = Client().get("/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "heroSlider" in html
    assert "KLASTERBOX" in html
    assert "Klaster ogólnokrajowy" in html   # filar
    assert "150+" in html                     # stats strip
    assert "hero-slider.js" in html           # slider JS dołączony
    assert "site-header" in html              # chrome
```

- [ ] **Step 3: Run** `pytest --create-db apps/home/tests/test_home_page.py -v` → 4 PASSED. `manage.py check` clean.

- [ ] **Step 4: Commit**
```
git add apps/home/templates/home/home_page.html apps/home/tests/test_home_page.py
git commit -m "feat(faza-1): szablon HomePage (10 sekcji z mockupu, sterowane CMS) + render test" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: Re-rooting + seed treści Fazy 1

Rozszerz `seed_initial_content`: utwórz `HomePage` jako root Site, 3 `PillarPage`, podepnij strony prawne/kontakt pod HomePage, ustaw filary/hero/staty na home. Idempotentne.

**Files:**
- Modify: `apps/pages/management/commands/seed_initial_content.py`
- Modify: `apps/pages/tests/test_seed.py`

- [ ] **Step 1: Dodaj funkcję re-rootingu do komendy.** Na początku `seed_initial_content.py` rozszerz importy:
```python
from apps.home.models import (
    HomePage, PillarPage, PillarBenefit, PillarStep,
    HeroSlide, Pillar, Statistic, HomeHeroSlide, HomePillar,
    HomeConsultStep, HomeOffering, HomeMemberLogo, HomeNewsTeaser,
)
```
W `handle()`, WEWNĄTRZ `transaction.atomic()`, PRZED tworzeniem stron prawnych, wstaw blok tworzący HomePage jako root i zwracający ją:
```python
        # --- HomePage jako root Site ---
        home = HomePage.objects.first()
        if home is None:
            tree_root = Page.get_first_root_node()  # niewidoczny korzeń drzewa (depth=1)
            home = HomePage(title="Klaster GOZ", slug="home", pillars_heading="Trzy filary cyrkularnej transformacji.")
            tree_root.add_child(instance=home)
            home.save_revision().publish()
            old_root = site.root_page
            # przenieś istniejące strony (prawne/kontakt) pod HomePage
            for child in list(old_root.get_children()):
                child.move(home, pos="last-child")
            site.root_page = home
            site.save()
            # usuń domyślną stronę powitalną Wagtaila, jeśli to nie HomePage
            if old_root.pk != home.pk and old_root.specific_class is not HomePage:
                old_root.delete()
        # odśwież referencję root po ewentualnym przeniesieniu
        root = HomePage.objects.first()
```
Następnie ZASTĄP użycia `root` (parent stron prawnych/kontaktu) tak, by używały `home`/`root` = HomePage (już ustawione powyżej). Strony prawne/kontakt tworzymy jako dzieci `root` (= HomePage) — jeśli już istnieją (przeniesione), guard `Page.objects.filter(slug=...).exists()` je pominie.

- [ ] **Step 2: Po utworzeniu 3 stron prawnych i kontaktu, dodaj tworzenie 3 PillarPage** (idempotentnie), pod HomePage:
```python
        # --- Strony filarów ---
        pillars_data = [
            ("klaster", "Klaster ogólnokrajowy", "Filar 01 · Klaster ogólnokrajowy"),
            ("edukacja", "Edukacja — Akademia GOZ", "Filar 02 · Akademia GOZ"),
            ("doradztwo", "Doradztwo", "Filar 03 · Doradztwo"),
        ]
        for slug, title, eyebrow in pillars_data:
            if not Page.objects.filter(slug=slug).exists():
                pp = PillarPage(
                    title=title, slug=slug, eyebrow=eyebrow,
                    hero_lead="Treść do uzupełnienia w panelu administracyjnym.",
                    cta_heading="Porozmawiajmy o Twojej transformacji.",
                    cta_button_label="Skontaktuj się", cta_button_url="/kontakt/",
                )
                home.add_child(instance=pp)
                pp.save_revision().publish()
```

- [ ] **Step 3: Po utworzeniu filarów, ustaw treść HomePage** (hero, filary, statystyki) idempotentnie:
```python
        # --- Treść HomePage (raz) ---
        if not home.hero_slides.exists():
            slide = HeroSlide.objects.create(
                eyebrow="Krajowy Klaster Kluczowy",
                headline="<p>Cyrkularna gospodarka — <em>nasza wspólna</em> przewaga.</p>",
                lead="Łączymy firmy, naukę i instytucje wokół zamykania obiegów surowcowych.",
                primary_cta_label="Poznaj klaster", primary_cta_url="/klaster/",
                secondary_cta_label="Bezpłatna konsultacja", secondary_cta_url="/kontakt/",
            )
            home.hero_slides.add(HomeHeroSlide(slide=slide))
        if not home.home_pillars.exists():
            klaster = Page.objects.filter(slug="klaster").first()
            edukacja = Page.objects.filter(slug="edukacja").first()
            doradztwo = Page.objects.filter(slug="doradztwo").first()
            p1 = Pillar.objects.create(number="01 / FILAR", title="Klaster ogólnokrajowy", lead="Platforma kooperacji 150+ firm.", bullets="Członkostwo i networking\nWspólne projekty B+R\nReprezentacja branży", link=klaster, cta_label="Dołącz do klastra")
            p2 = Pillar.objects.create(number="02 / FILAR", title="Edukacja — Akademia GOZ", lead="Szkolenia i programy rozwojowe.", bullets="ATB / ATB-VIP / ATT\nSzkolenia GOZ, ESG, AI\nHarmonogram otwarty", link=edukacja, cta_label="Zobacz harmonogram", is_dark=True)
            p3 = Pillar.objects.create(number="03 / FILAR", title="Doradztwo", lead="Indywidualne wsparcie firm.", bullets="PRO GOZ\nGO GREEN\nKNR Green", link=doradztwo, cta_label="Umów konsultację")
            home.home_pillars.add(HomePillar(pillar=p1), HomePillar(pillar=p2), HomePillar(pillar=p3))
        home.save_revision().publish()
        if not Statistic.objects.filter(group="home_strip").exists():
            for i, (v, l) in enumerate([("150+", "firm i instytucji członkowskich"), ("12", "lat działalności klastra"), ("19", "krajowych klastrów kluczowych"), ("240 mln zł", "pozyskanego finansowania")]):
                Statistic.objects.create(value=v, label=l, group="home_strip", sort_order=i)
```

- [ ] **Step 4: Zaktualizuj `NavigationSettings` seed** w tej samej komendzie — menu główne ma teraz linkować do filarów (PageChooser) zamiast tylko Kontakt. Zamień blok `nav.primary_menu` na:
```python
        nav = NavigationSettings.for_site(site)
        if not nav.primary_menu:
            klaster = Page.objects.filter(slug="klaster").first()
            edukacja = Page.objects.filter(slug="edukacja").first()
            doradztwo = Page.objects.filter(slug="doradztwo").first()
            kontakt = Page.objects.filter(slug="kontakt").first()
            def item(label, pg, key):
                return {"type": "item", "value": {"label": label, "page": pg.id if pg else None, "url": "", "nav_key": key, "columns": []}}
            nav.primary_menu = [item("Klaster", klaster, "klaster"), item("Edukacja", edukacja, "edukacja"), item("Doradztwo", doradztwo, "doradztwo"), item("Kontakt", kontakt, "kontakt")]
            nav.save()
```

- [ ] **Step 5: Rozszerz `apps/pages/tests/test_seed.py`** o re-rooting i filary:
```python
@pytest.mark.django_db
def test_seed_sets_homepage_as_root():
    from apps.home.models import HomePage
    call_command("seed_initial_content")
    site = Site.objects.get(is_default_site=True)
    assert isinstance(site.root_page.specific, HomePage)
    # strony prawne i filary są dziećmi HomePage
    home = site.root_page
    child_slugs = set(home.get_children().values_list("slug", flat=True))
    for slug in ["rodo", "regulamin", "cookies", "kontakt", "klaster", "edukacja", "doradztwo"]:
        assert slug in child_slugs, f"brak {slug} pod HomePage"


@pytest.mark.django_db
def test_seed_homepage_has_content_and_renders():
    call_command("seed_initial_content")
    resp = Client().get("/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "heroSlider" in html
    assert "Klaster ogólnokrajowy" in html
```
Dodaj `from django.test import Client` na górze pliku (jeśli go nie ma).

- [ ] **Step 6: Run** `pytest --create-db apps/pages/tests/test_seed.py -v` → wszystkie PASSED (stare + 2 nowe). Następnie pełny seed test ręczny niepotrzebny — sprawdza go test.

- [ ] **Step 7: Commit**
```
git add apps/pages/management/commands/seed_initial_content.py apps/pages/tests/test_seed.py
git commit -m "feat(faza-1): re-rooting (HomePage jako root) + seed filarow/hero/staty + menu do filarow" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7: Weryfikacja końcowa + dokumentacja (DoD)

**Files:**
- Create: `apps/home/README.md`
- Modify: `README.md` (status fazy)

- [ ] **Step 1: Create `apps/home/README.md`:**
```markdown
# apps.home

Strona główna portalu i landingi filarów.

## Co robi
- Snippety: `HeroSlide` (slajdy hero), `Pillar` (kafelki filarów z linkiem do strony), `Statistic` (statystyki, grupy home_strip/home_section/about_klastra).
- `HomePage` — root portalu. Sekcje z `mockup/index.html` jako pola + Orderable children (slajdy hero, filary, kroki konsultacji, kafelki usług, logosy członków, teasery aktualności). Statystyki pobierane z `Statistic` po grupie w `get_context`. `max_count=1`, `parent_page_types=["wagtailcore.Page"]`.
- `PillarPage` — wspólny landing filaru (Klaster/Edukacja/Doradztwo): hero, korzyści, blok „jak działamy", kroki procesu, CTA, auto-listing żywych dzieci (puste do Faz 2–4).
- `static/js/hero-slider.js` — slider hero (vanilla, aktywny tylko gdy `#heroSlider` istnieje).

## Tymczasowe (do zastąpienia w późniejszych fazach)
- Kafelki usług (`offerings`) → auto-lista ServicePage w Fazie 2.
- Logosy członków (`member_logos`) → Member snippets w Fazie 2.
- Teasery aktualności (`news_teasers`) → ArticlePage w Fazie 4.
- Sekcja konsultacji renderuje CTA do /kontakt/; pełny formularz konsultacji = Faza 2.

## Re-rooting
`manage.py seed_initial_content` ustawia HomePage jako `Site.root_page` i przenosi pod nią strony prawne/kontakt z Fazy 0.

## Zależności
`apps.shared` (BasePage/SeoMixin), Wagtail snippets/images.
```

- [ ] **Step 2: Zaktualizuj `README.md`** — w „Dokumentacja projektu" dodaj plan Fazy 1 i zaktualizuj status:
```markdown
  - Faza 1 (Home + filary): `docs/superpowers/plans/2026-06-10-faza-1-home-filary.md`
- Status: Faza 1 (Home + 3 filary) — ukończona.
```

- [ ] **Step 3: Lint + pełne testy (DoD):**
```
& C:\Users\tmrow\.local\bin\uv.exe run ruff check .
& C:\Users\tmrow\.local\bin\uv.exe run black --check .
& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db -q
```
Expected: ruff „All checks passed!", black clean, wszystkie testy PASSED. Jeśli ruff zgłosi isort w nowych plikach → `ruff check --fix .`. Jeśli black → `black .` i dodaj do commita.

- [ ] **Step 4: Smoke ręczny** (jeśli Postgres dostępny): `docker compose -f docker-compose.dev.yml up -d` → `migrate` → `seed_initial_content` → `runserver` → otwórz `/` (home z hero/filarami), `/klaster/`, `/edukacja/`, `/doradztwo/` (landingi), sprawdź że `/rodo/`, `/kontakt/` nadal działają (teraz pod HomePage). Jeśli brak Postgresa — testy renderujące (Client) są automatycznym smoke.

- [ ] **Step 5: Commit końcowy**
```
git add apps/home/README.md README.md
git commit -m "docs(faza-1): README apps/home + status fazy + ewentualny lint/format" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (autor planu)

**1. Pokrycie zakresu Fazy 1 (spec 2.1 + 5.1/5.2):**
- HomePage 1:1 z mockupu (hero slider, pasek statystyk, 3 filary, konsultacja+kroki, statystyki, usługi, członkowie, o klastrze, aktualności, CTA) → Task 3 (model) + Task 5 (szablon, wszystkie 10 sekcji) ✅
- 3 PillarPage jako landingi z auto-listingiem podstron → Task 2 (model+szablon, `get_context` listuje żywe dzieci) + Task 6 (3 instancje) ✅
- Snippety HeroSlide/Pillar/Statistic → Task 1 ✅
- Hero slider (JS) → Task 4 ✅
- HomePage jako root + przeniesienie stron Fazy 0 → Task 6 (re-rooting) ✅

**2. Definition of Done (spec 2.2):**
- Zero hardkodu / pełne zarządzanie w Wagtailu → wszystkie sekcje to pola/orderables/snippety; weryfikacja render-testami i smoke (Task 5/6/7) ✅
- Przechodzące testy → testy w Task 1/2/3/5/6 + pełny run Task 7 ✅
- Commit per zadanie → tak ✅
- Dokumentacja → README apps/home + docstringi (Task 7) ✅

**3. Skan placeholderów:** brak TBD/TODO; cały kod podany wprost. „Placeholder" w planie dotyczy wyłącznie świadomie odłożonych funkcji (formularz konsultacji → Faza 2, auto-listy usług/członków/aktualności → Faza 2/4), nie braków planu.

**4. Spójność typów/nazw:** `BasePage` (z apps.shared) używany przez HomePage/PillarPage; relacje `hero_slides`/`home_pillars`/`offerings`/`member_logos`/`news_teasers`/`consult_steps`/`benefits`/`steps` spójne między modelami, szablonami i seedem; snippety HeroSlide/Pillar/Statistic spójne; `Pillar.bullet_list()` / `PillarPage.feature_bullet_list()` / `HomePage.about_bullet_list()` zdefiniowane i użyte w szablonach; `get_context` HomePage zwraca `stats_strip`/`stats_section` użyte w szablonie.

**Znane punkty uwagi przy wykonaniu:**
- Re-rooting (Task 6) operuje na drzewie Wagtaila — `Page.get_first_root_node()` to korzeń (depth=1); HomePage staje się jego dzieckiem i `Site.root_page`. Przenoszenie dzieci przez `.move(home, pos="last-child")`. Idempotencja: blok wykonuje się tylko gdy `HomePage.objects.first()` jest None.
- W testach seed (Task 6) HomePage staje się rootem w obrębie pojedynczego testu — nie koliduje z testami Fazy 0 (te tworzą strony pod aktualnym rootem niezależnie).
- Poprawny `get_context` w PillarPage — patrz korekta w Task 2 Step 2.
- `headline` HeroSlide to RichText (z `<em>`); w szablonie renderowane przez `|richtext` wewnątrz `<h1>`.
