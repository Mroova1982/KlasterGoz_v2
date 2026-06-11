# Faza 2a — Usługi klastra — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dodać sekcję usług klastra: `ServicesIndexPage` (`/klaster/uslugi`) z auto-katalogiem oraz 5× `ServicePage` (KNR Green, PRO GOZ, PRO INNO, GO GREEN, PRO EKO) — w pełni edytowalne w panelu Wagtail, pod istniejącą stroną filaru `/klaster`.

**Architecture:** Nowy app `apps/services`. `ServicesIndexPage` i `ServicePage` dziedziczą z `BasePage` (SEO z Fazy 0). Powtarzalne elementy ServicePage (korzyści, etapy procesu, FAQ) to Orderable inline children; sekcje nagłówkowe i hero to pola; sekcje renderują się warunkowo (`{% if %}`). Indeks listuje żywe dzieci w `get_context`. Treść startową dokłada idempotentny seed.

**Tech Stack:** Wagtail 6.3 / Django 5.1 / Python 3.13. Testy: pytest + pytest-django (SQLite, static non-manifest). uv: `C:\Users\tmrow\.local\bin\uv.exe` (PowerShell, `Set-Location C:\Programer\Projekty\KlasterGoz_v2` najpierw; benign Postgres timeout w makemigrations/check OK).

> **Świadome decyzje (do potwierdzenia):** (1) FAQ jako **per-page orderable** `ServiceFAQ`, nie globalny snippet `FAQItem` ze specu 5.2 — FAQ są specyficzne dla usługi, reużycie zbędne. (2) **POMIJAMY** `related_projects` (ProjectPage = Faza 4) i `AbstractServiceLikePage` (ConsultingAreaPage = Faza 4) — `ServicePage` jest konkretny; abstrakcję wydzielimy w Fazie 4, jeśli się opłaci. (3) Boczny „box" w hero (jak „7 branż" w KNR Green) modelujemy jako opcjonalne pola — usługi bez niego renderują samo hero.

---

## Mapa plików
- Modify: `klastergoz/settings/base.py` (dodać `apps.services`)
- Create: `apps/services/__init__.py`, `apps/services/apps.py`, `apps/services/models.py`
- Create: `apps/services/migrations/` (przez makemigrations)
- Create: `apps/services/templates/services/services_index_page.html`, `apps/services/templates/services/service_page.html`
- Create: `apps/services/tests/__init__.py`, `test_models.py`, `test_render.py`
- Create: `apps/services/README.md`
- Modify: `apps/pages/management/commands/seed_initial_content.py` (seed usług)
- Modify: `apps/pages/tests/test_seed.py` (testy seeda usług)
- Create: `docs/przewodnik-moderatora/15-uslugi.md` (rozdział przewodnika — DoD #5)

Parent w drzewie: `ServicesIndexPage` pod `home.PillarPage` (instancja `/klaster`); `ServicePage` pod `ServicesIndexPage`.

---

## Konwencje testów
- `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db <ścieżka> -v`. DB: `@pytest.mark.django_db`.
- Strony filaru tworzymy w testach pod root Site; ale `ServicesIndexPage.parent_page_types=["home.PillarPage"]` — w testach twórz najpierw `PillarPage` (z `apps.home.models`) jako rodzica, potem `ServicesIndexPage` jako jej dziecko. Fixture:
```python
import pytest
from wagtail.models import Site
from apps.home.models import PillarPage

@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    pillar = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=pillar)
    pillar.save_revision().publish()
    return pillar
```

---

## Task 1: Modele `ServicesIndexPage` + `ServicePage` (+ orderables)

**Files:**
- Modify: `klastergoz/settings/base.py`
- Create: `apps/services/__init__.py`, `apps/services/apps.py`, `apps/services/models.py`
- Create: `apps/services/tests/__init__.py`, `apps/services/tests/test_models.py`

- [ ] **Step 1: Scaffold app**

Create `apps/services/__init__.py` (empty). Create `apps/services/apps.py`:
```python
from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.services"
    verbose_name = "Usługi klastra"
```
Add `"apps.services"` to `INSTALLED_APPS` in `klastergoz/settings/base.py` (local apps block, after `"apps.guide"`).

- [ ] **Step 2: `apps/services/models.py`**
```python
"""Usługi klastra: ServicesIndexPage (katalog) + ServicePage (5 usług)."""
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable

from apps.shared.models import BasePage


class ServicesIndexPage(BasePage):
    """Katalog usług pod /klaster/uslugi — auto-lista stron ServicePage."""

    eyebrow = models.CharField("Nadtytuł", max_length=80, blank=True, default="Usługi klastra")
    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [
        FieldPanel("eyebrow"),
        FieldPanel("intro"),
    ]
    promote_panels = BasePage.promote_panels
    template = "services/services_index_page.html"

    parent_page_types = ["home.PillarPage"]
    subpage_types = ["services.ServicePage"]
    max_count = 1

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["services"] = self.get_children().live().specific()
        return ctx

    class Meta:
        verbose_name = "Katalog usług"


class ServiceBenefit(Orderable):
    """Kafelek 'dla kogo / korzyść' na stronie usługi."""

    page = ParentalKey("ServicePage", on_delete=models.CASCADE, related_name="benefits")
    tag = models.CharField("Tag", max_length=40, blank=True)
    title = models.CharField("Tytuł", max_length=160)
    description = models.TextField("Opis", blank=True)
    panels = [FieldPanel("tag"), FieldPanel("title"), FieldPanel("description")]


class ServiceStep(Orderable):
    """Etap procesu usługi."""

    page = ParentalKey("ServicePage", on_delete=models.CASCADE, related_name="steps")
    number = models.CharField("Numer", max_length=4, help_text="np. '01'")
    title = models.CharField("Tytuł", max_length=120)
    description = models.TextField("Opis", blank=True)
    panels = [FieldPanel("number"), FieldPanel("title"), FieldPanel("description")]


class ServiceFAQ(Orderable):
    """Pytanie FAQ na stronie usługi."""

    page = ParentalKey("ServicePage", on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField("Pytanie", max_length=255)
    answer = RichTextField("Odpowiedź", features=["bold", "italic", "link"])
    panels = [FieldPanel("question"), FieldPanel("answer")]


class ServicePage(BasePage):
    """Pojedyncza usługa (KNR Green / PRO GOZ / PRO INNO / GO GREEN / PRO EKO)."""

    tag = models.CharField("Tag (chip w hero)", max_length=40, blank=True)
    hero_lead = models.TextField("Lead w hero", blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    primary_cta_label = models.CharField("CTA główne — tekst", max_length=60, blank=True)
    primary_cta_url = models.CharField("CTA główne — URL", max_length=255, blank=True)
    secondary_cta_label = models.CharField("CTA drugie — tekst", max_length=60, blank=True)
    secondary_cta_url = models.CharField("CTA drugie — URL", max_length=255, blank=True)

    hero_box_chip = models.CharField("Box hero — etykieta", max_length=40, blank=True)
    hero_box_heading = models.CharField("Box hero — nagłówek", max_length=120, blank=True)
    hero_box_items = models.TextField("Box hero — pozycje (jedna na linię)", blank=True)

    intro = RichTextField("Opis usługi", blank=True, features=["bold", "italic", "link"])

    benefits_heading = models.CharField("Nagłówek sekcji korzyści", max_length=160, blank=True)
    process_heading = models.CharField("Nagłówek sekcji procesu", max_length=160, blank=True)

    pricing = RichTextField("Cennik / widełki", blank=True, features=["bold", "italic", "link"])

    faq_heading = models.CharField("Nagłówek sekcji FAQ", max_length=160, blank=True, default="Najczęściej zadawane pytania.")

    cta_heading = models.CharField("CTA strip — nagłówek", max_length=200, blank=True)
    cta_lead = models.TextField("CTA strip — lead", blank=True)
    cta_button_label = models.CharField("CTA strip — przycisk", max_length=60, blank=True)
    cta_button_url = models.CharField("CTA strip — URL", max_length=255, blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("tag"),
                FieldPanel("hero_lead"),
                FieldPanel("hero_image"),
                FieldPanel("primary_cta_label"),
                FieldPanel("primary_cta_url"),
                FieldPanel("secondary_cta_label"),
                FieldPanel("secondary_cta_url"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [FieldPanel("hero_box_chip"), FieldPanel("hero_box_heading"), FieldPanel("hero_box_items")],
            heading="Hero — boczny box (opcjonalny)",
        ),
        FieldPanel("intro"),
        FieldPanel("benefits_heading"),
        InlinePanel("benefits", label="Korzyści / dla kogo"),
        FieldPanel("process_heading"),
        InlinePanel("steps", label="Etapy procesu"),
        FieldPanel("pricing"),
        FieldPanel("faq_heading"),
        InlinePanel("faqs", label="FAQ"),
        MultiFieldPanel(
            [FieldPanel("cta_heading"), FieldPanel("cta_lead"), FieldPanel("cta_button_label"), FieldPanel("cta_button_url")],
            heading="CTA strip",
        ),
    ]
    promote_panels = BasePage.promote_panels
    template = "services/service_page.html"

    parent_page_types = ["services.ServicesIndexPage"]
    subpage_types = []

    def hero_box_item_list(self) -> list[str]:
        return [i.strip() for i in self.hero_box_items.splitlines() if i.strip()]

    class Meta:
        verbose_name = "Usługa"
        verbose_name_plural = "Usługi"
```

- [ ] **Step 3: Migracja** — `& C:\Users\tmrow\.local\bin\uv.exe run python manage.py makemigrations services` → `0001_initial.py` (ServicesIndexPage, ServicePage, ServiceBenefit, ServiceStep, ServiceFAQ).

- [ ] **Step 4: `apps/services/tests/__init__.py`** (empty) + `apps/services/tests/test_models.py`:
```python
import pytest
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.services.models import ServicesIndexPage, ServicePage, ServiceBenefit


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    pillar = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=pillar)
    pillar.save_revision().publish()
    return pillar


@pytest.mark.django_db
def test_index_lists_service_children(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    svc = ServicePage(title="KNR Green", slug="knr-green", tag="Certyfikacja", hero_lead="...")
    idx.add_child(instance=svc)
    svc.save_revision().publish()
    children = list(idx.get_children().live().specific())
    assert svc.pk in [c.pk for c in children]


@pytest.mark.django_db
def test_service_hero_box_item_list(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    svc = ServicePage(title="KNR Green", slug="knr-green", hero_box_items="Tekstylna\nMetalurgiczna\n\nPapiernicza")
    idx.add_child(instance=svc)
    assert svc.hero_box_item_list() == ["Tekstylna", "Metalurgiczna", "Papiernicza"]


@pytest.mark.django_db
def test_service_benefits_relation(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    svc = ServicePage(title="KNR Green", slug="knr-green")
    idx.add_child(instance=svc)
    svc.benefits.add(ServiceBenefit(tag="B2B", title="Duzi klienci", description="..."))
    svc.save_revision().publish()
    assert svc.benefits.count() == 1
```

- [ ] **Step 5: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/services/tests/test_models.py -v` → 3 PASSED. `manage.py check` clean. Full suite no regression.

- [ ] **Step 6: Commit**
```
git add klastergoz/settings/base.py apps/services/__init__.py apps/services/apps.py apps/services/models.py apps/services/migrations/ apps/services/tests/__init__.py apps/services/tests/test_models.py
git commit -m "feat(faza-2a): modele ServicesIndexPage + ServicePage (+ orderables)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Szablony usług (port mockup) + render testy

**Files:**
- Create: `apps/services/templates/services/service_page.html`, `services_index_page.html`
- Create: `apps/services/tests/test_render.py`

- [ ] **Step 1: `apps/services/templates/services/service_page.html`** (odwzorowuje `mockup/oferta/knr-green.html`):
```django
{% extends "base.html" %}
{% load static wagtailcore_tags wagtailimages_tags %}

{% block body_attrs %}data-page="doradztwo"{% endblock %}

{% block content %}
<section class="page-header">
  <div class="container" style="display: grid; grid-template-columns: 1.3fr 0.9fr; gap: 60px; align-items: center;">
    <div>
      <ul class="crumbs"><li><a href="/">Strona główna</a></li>{% if page.get_parent %}<li><a href="{% pageurl page.get_parent %}">{{ page.get_parent.title }}</a></li>{% endif %}<li>{{ page.title }}</li></ul>
      {% if page.tag %}<span class="chip chip--lime" style="margin-bottom: 16px;">{{ page.tag }}</span>{% endif %}
      <h1>{{ page.title }}</h1>
      {% if page.hero_lead %}<p class="lead">{{ page.hero_lead }}</p>{% endif %}
      <div style="display: flex; gap: 12px; margin-top: 28px; flex-wrap: wrap;">
        {% if page.primary_cta_label %}<a href="{{ page.primary_cta_url|default:'#' }}" class="btn btn--primary">{{ page.primary_cta_label }} <span class="arr">→</span></a>{% endif %}
        {% if page.secondary_cta_label %}<a href="{{ page.secondary_cta_url|default:'#' }}" class="btn btn--ghost">{{ page.secondary_cta_label }}</a>{% endif %}
      </div>
    </div>
    {% if page.hero_box_heading %}
    <div style="background: linear-gradient(160deg, var(--green-700), var(--green-900)); color:#fff; border-radius:28px; padding:40px; aspect-ratio:1/1.1; display:flex; flex-direction:column; justify-content:space-between; box-shadow: var(--shadow-lg);">
      <div>{% if page.hero_box_chip %}<span class="chip chip--dark">{{ page.hero_box_chip }}</span>{% endif %}<h3 style="color:#fff; margin-top:18px; font-size:28px;">{{ page.hero_box_heading }}</h3></div>
      {% if page.hero_box_item_list %}<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:13.5px; color:rgba(255,255,255,0.85);">{% for it in page.hero_box_item_list %}<span>· {{ it }}</span>{% endfor %}</div>{% endif %}
    </div>
    {% elif page.hero_image %}
    <div>{% image page.hero_image fill-560x620 %}</div>
    {% endif %}
  </div>
</section>

{% if page.intro %}
<section class="section"><div class="container"><div class="article">{{ page.intro|richtext }}</div></div></section>
{% endif %}

{% if page.benefits.all %}
<section class="section">
  <div class="container">
    {% if page.benefits_heading %}<div class="section-head"><div><h2>{{ page.benefits_heading }}</h2></div></div>{% endif %}
    <div class="offerings">
      {% for b in page.benefits.all %}
      <div class="offering">{% if b.tag %}<span class="tag">{{ b.tag }}</span>{% endif %}<h3>{{ b.title }}</h3>{% if b.description %}<p>{{ b.description }}</p>{% endif %}</div>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.steps.all %}
<section class="section bg-green">
  <div class="container">
    {% if page.process_heading %}<div class="section-head"><div><h2>{{ page.process_heading }}</h2></div></div>{% endif %}
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px;">
      {% for s in page.steps.all %}
      <div style="background:#fff; padding:28px 24px; border-radius:18px; border:1px solid var(--ink-100);">
        <strong style="font-family: var(--font-display); font-size:32px; color: var(--green-700); display:block;">{{ s.number }}</strong>
        <h4 style="margin:12px 0 8px;">{{ s.title }}</h4>
        <p style="margin:0; font-size:13.5px; color: var(--ink-500);">{{ s.description }}</p>
      </div>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.pricing %}
<section class="section"><div class="container"><div class="article"><h2>Cennik</h2>{{ page.pricing|richtext }}</div></div></section>
{% endif %}

{% if page.faqs.all %}
<section class="section">
  <div class="container" style="display: grid; grid-template-columns: 1fr 1.4fr; gap: 60px; align-items: start;">
    <div><span class="eyebrow">FAQ</span><h2 style="margin-top:14px;">{{ page.faq_heading }}</h2></div>
    <div class="faq">
      {% for f in page.faqs.all %}
      <details{% if forloop.first %} open{% endif %}><summary>{{ f.question }}</summary>{{ f.answer|richtext }}</details>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}

{% if page.cta_heading %}
<section class="section--tight">
  <div class="container">
    <div class="cta-strip">
      <div><h2>{{ page.cta_heading }}</h2>{% if page.cta_lead %}<p>{{ page.cta_lead }}</p>{% endif %}</div>
      {% if page.cta_button_label %}<a href="{{ page.cta_button_url|default:'#' }}" class="btn btn--accent">{{ page.cta_button_label }} <span class="arr">→</span></a>{% endif %}
    </div>
  </div>
</section>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: `apps/services/templates/services/services_index_page.html`** (port `mockup/oferta.html` — katalog):
```django
{% extends "base.html" %}
{% load wagtailcore_tags %}

{% block body_attrs %}data-page="doradztwo"{% endblock %}

{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li>{% if page.get_parent %}<li><a href="{% pageurl page.get_parent %}">{{ page.get_parent.title }}</a></li>{% endif %}<li>{{ page.title }}</li></ul>
    {% if page.eyebrow %}<span class="eyebrow">{{ page.eyebrow }}</span>{% endif %}
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.intro %}<div class="lead">{{ page.intro|richtext }}</div>{% endif %}
  </div>
</section>

{% if services %}
<section class="section bg-green">
  <div class="container">
    <div class="offerings">
      {% for s in services %}
      <a href="{% pageurl s %}" class="offering">{% if s.tag %}<span class="tag">{{ s.tag }}</span>{% endif %}<h3>{{ s.title }}</h3>{% if s.hero_lead %}<p>{{ s.hero_lead }}</p>{% elif s.search_description %}<p>{{ s.search_description }}</p>{% endif %}<span class="more">Dowiedz się więcej →</span></a>
      {% endfor %}
    </div>
  </div>
</section>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: `apps/services/tests/test_render.py`:**
```python
import pytest
from django.test import Client
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.services.models import ServicesIndexPage, ServicePage, ServiceBenefit, ServiceStep, ServiceFAQ


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    pillar = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=pillar)
    pillar.save_revision().publish()
    return pillar


@pytest.mark.django_db
def test_service_page_renders(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    svc = ServicePage(
        title="KNR Green", slug="knr-green", tag="Certyfikacja",
        hero_lead="Standard certyfikacji recyklingu.",
        hero_box_heading="7 branż", hero_box_items="Tekstylna\nMetalurgiczna",
        benefits_heading="Dla kogo", process_heading="Proces", cta_heading="Gotowy?",
    )
    idx.add_child(instance=svc)
    svc.benefits.add(ServiceBenefit(tag="B2B", title="Duzi klienci wymagają recyklatu"))
    svc.steps.add(ServiceStep(number="01", title="Zgłoszenie"))
    svc.faqs.add(ServiceFAQ(question="Ile trwa proces?", answer="<p>8–12 tygodni.</p>"))
    svc.save_revision().publish()

    resp = Client().get("/klaster/uslugi/knr-green/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "KNR Green" in html
    assert "Certyfikacja" in html             # chip
    assert "7 branż" in html                  # hero box
    assert "Duzi klienci wymagają recyklatu" in html  # benefit
    assert "Zgłoszenie" in html               # step
    assert "Ile trwa proces?" in html         # faq
    assert "site-header" in html              # chrome


@pytest.mark.django_db
def test_services_index_lists_services(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi", intro="<p>Katalog.</p>")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    for slug, title in [("knr-green", "KNR Green"), ("pro-goz", "PRO GOZ")]:
        s = ServicePage(title=title, slug=slug, tag="X", hero_lead="...")
        idx.add_child(instance=s)
        s.save_revision().publish()

    resp = Client().get("/klaster/uslugi/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "KNR Green" in html
    assert "PRO GOZ" in html
    assert "/klaster/uslugi/knr-green/" in html   # link do usługi
```

- [ ] **Step 4: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/services/tests/ -v` → all PASSED. Template parse via render. Full suite no regression.

- [ ] **Step 5: Commit**
```
git add apps/services/templates/ apps/services/tests/test_render.py
git commit -m "feat(faza-2a): szablony ServicePage + ServicesIndexPage (port mockupu) + render testy" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Seed — katalog + 5 usług pod /klaster

**Files:**
- Modify: `apps/pages/management/commands/seed_initial_content.py`
- Modify: `apps/pages/tests/test_seed.py`

- [ ] **Step 1: Rozszerz importy** w `seed_initial_content.py` o:
```python
from apps.services.models import ServicesIndexPage, ServicePage
```

- [ ] **Step 2: Po seedzie PillarPage (gdzie tworzone są klaster/edukacja/doradztwo), dodaj seed usług** — WEWNĄTRZ `transaction.atomic()`, po utworzeniu stron filarów:
```python
        # --- Usługi pod /klaster/uslugi ---
        klaster_pillar = Page.objects.filter(slug="klaster").first()
        if klaster_pillar and not Page.objects.filter(slug="uslugi").exists():
            idx = ServicesIndexPage(
                title="Usługi klastra", slug="uslugi", eyebrow="Usługi klastra",
                intro="<p>Pełen portfel narzędzi transformacji cyrkularnej. Treść do uzupełnienia w panelu.</p>",
            )
            klaster_pillar.add_child(instance=idx)
            idx.save_revision().publish()
            services_data = [
                ("knr-green", "KNR Green", "Certyfikacja", "Pierwszy polski standard certyfikacji recyklingu."),
                ("pro-goz", "PRO GOZ", "Doradztwo", "Model biznesowy cyrkularny — produkty i usługi zgodne z GOZ."),
                ("pro-inno", "PRO INNO", "Innowacje", "Transformacja innowacyjna i cyfrowa — od pomysłu po wdrożenie."),
                ("go-green", "GO GREEN", "ESG · CSRD", "Ślad węglowy, ESG, sprawozdawczość zgodna z taksonomią UE."),
                ("pro-eko", "PRO EKO", "Ekoprojektowanie", "Ekoprojektowanie i minimalizacja śladu w łańcuchu dostaw."),
            ]
            for slug, title, tag, lead in services_data:
                svc = ServicePage(
                    title=title, slug=slug, tag=tag, hero_lead=lead,
                    primary_cta_label="Skontaktuj się", primary_cta_url="/kontakt/",
                    cta_heading="Porozmawiajmy o Twojej transformacji.",
                    cta_button_label="Skontaktuj się", cta_button_url="/kontakt/",
                )
                idx.add_child(instance=svc)
                svc.save_revision().publish()
```

- [ ] **Step 3: Dopisz test do `apps/pages/tests/test_seed.py`:**
```python
@pytest.mark.django_db
def test_seed_creates_services():
    from wagtail.models import Page
    call_command("seed_initial_content")
    assert Page.objects.filter(slug="uslugi").exists()
    for slug in ["knr-green", "pro-goz", "pro-inno", "go-green", "pro-eko"]:
        assert Page.objects.filter(slug=slug).count() == 1, f"brak usługi {slug}"


@pytest.mark.django_db
def test_seed_services_idempotent():
    from wagtail.models import Page
    call_command("seed_initial_content")
    call_command("seed_initial_content")
    assert Page.objects.filter(slug="knr-green").count() == 1
    assert Page.objects.filter(slug="uslugi").count() == 1
```
(`call_command`, `pytest` już zaimportowane na górze pliku.)

- [ ] **Step 4: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/pages/tests/test_seed.py -v` → all PASSED. Pełny smoke: `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db -q` → bez regresji.

- [ ] **Step 5: Commit**
```
git add apps/pages/management/commands/seed_initial_content.py apps/pages/tests/test_seed.py
git commit -m "feat(faza-2a): seed katalogu uslug + 5 ServicePage pod /klaster" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Dokumentacja (przewodnik + README) + DoD lint/testy

**Files:**
- Create: `docs/przewodnik-moderatora/15-uslugi.md`
- Create: `apps/services/README.md`
- (Modify jeśli trzeba: nic poza tym)

- [ ] **Step 1: `docs/przewodnik-moderatora/15-uslugi.md`** (rozdział przewodnika — DoD #5):
```markdown
# Usługi klastra

Usługi to strony pod **/klaster/uslugi**. Katalog (`ServicesIndexPage`) automatycznie listuje wszystkie usługi-dzieci; każda usługa to `ServicePage`.

## Usługi → Katalog
**Co steruje:** stronę `/klaster/uslugi` (nadtytuł, wstęp) + automatyczną listę usług.
**Gdzie edytujesz:** Pages → Klaster → Usługi klastra (nadtytuł, wstęp). Lista usług buduje się sama z podstron.

## Usługa → Hero
**Co steruje:** nagłówek strony usługi: tag (chip), tytuł, lead, dwa przyciski; opcjonalny boczny box (etykieta, nagłówek, pozycje — jedna na linię).
**Gdzie edytujesz:** Pages → Klaster → Usługi → wybrana usługa → sekcja „Hero" i „Hero — boczny box".

## Usługa → Opis
**Co steruje:** akapit opisu pod hero.
**Gdzie edytujesz:** Pages → usługa → „Opis usługi".

## Usługa → Korzyści / dla kogo
**Co steruje:** kafelki „kiedy potrzebujesz / dla kogo".
**Gdzie edytujesz:** Pages → usługa → nagłówek + „Korzyści / dla kogo" (każdy: tag, tytuł, opis).

## Usługa → Etapy procesu
**Co steruje:** numerowane etapy realizacji usługi.
**Gdzie edytujesz:** Pages → usługa → nagłówek + „Etapy procesu" (numer, tytuł, opis).

## Usługa → Cennik
**Co steruje:** opcjonalną sekcję z cennikiem/widełkami.
**Gdzie edytujesz:** Pages → usługa → „Cennik / widełki".

## Usługa → FAQ
**Co steruje:** rozwijane pytania i odpowiedzi.
**Gdzie edytujesz:** Pages → usługa → nagłówek FAQ + „FAQ" (pytanie, odpowiedź).

## Usługa → CTA strip
**Co steruje:** pasek wezwania do działania na dole.
**Gdzie edytujesz:** Pages → usługa → „CTA strip".
```

- [ ] **Step 2: `apps/services/README.md`:**
```markdown
# apps.services

Usługi klastra (filar Klaster).

## Co robi
- `ServicesIndexPage` — katalog pod `/klaster/uslugi`; auto-listuje żywe podstrony `ServicePage` w `get_context`. `parent_page_types=["home.PillarPage"]`, `max_count=1`.
- `ServicePage` — pojedyncza usługa: hero (tag, lead, CTA, opcjonalny boczny box), opis, korzyści (`ServiceBenefit`), etapy procesu (`ServiceStep`), cennik, FAQ (`ServiceFAQ`), CTA strip. `parent_page_types=["services.ServicesIndexPage"]`.
- Sekcje renderują się warunkowo — puste znikają.

## Świadome uproszczenia
- FAQ jako per-page orderable (`ServiceFAQ`), nie globalny snippet FAQItem.
- Bez `related_projects` (ProjectPage = Faza 4) i bez `AbstractServiceLikePage` (ConsultingAreaPage = Faza 4).

## Zależności
`apps.shared` (BasePage), `apps.home` (PillarPage jako rodzic).
```

- [ ] **Step 3: Lint + pełne testy (DoD):**
```
& C:\Users\tmrow\.local\bin\uv.exe run ruff check .
& C:\Users\tmrow\.local\bin\uv.exe run black --check .
& C:\Users\tmrow\.local\bin\uv.exe run python manage.py check
& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db -q
```
Expected: ruff „All checks passed!" (jeśli isort → `ruff check --fix .`); black clean (jeśli nie → `black .` + dodaj do commita); check clean; wszystkie testy PASSED (poprzednie 40 + ~8 nowych ≈ 48).

- [ ] **Step 4: Commit**
```
git add docs/przewodnik-moderatora/15-uslugi.md apps/services/README.md
git add -A
git commit -m "docs(faza-2a): rozdzial przewodnika 'Uslugi' + README apps/services + lint" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (autor planu)

**1. Pokrycie zakresu 2a (spec 4 + 5.1):**
- ServicesIndexPage (hero/intro/auto-listing) → Task 1 (model) + Task 2 (szablon) ✅
- 5× ServicePage (tag/hero/opis/etapy/korzyści/cennik/faq/cta) → Task 1 (model + orderables) + Task 2 (szablon) ✅
- URL `/klaster/uslugi/*` (pod PillarPage) → parent_page_types + seed (Task 3) ✅
- Snippet FAQItem → świadomie zastąpiony per-page `ServiceFAQ` (flaga w nagłówku) ✅
- Pominięte related_projects / AbstractServiceLikePage → udokumentowane (Faza 4) ✅
- DoD #5 (przewodnik) → Task 4 (rozdział 15-uslugi.md) ✅

**2. Skan placeholderów:** brak TBD/TODO; cały kod/treść podane wprost. „Treść do uzupełnienia w panelu" w seedzie to celowy placeholder treści edytowalnej (jak w Fazach 0/1), nie luka planu.

**3. Spójność nazw:** related_names `benefits`/`steps`/`faqs` spójne w modelu, szablonie, seedzie i testach; `hero_box_item_list`/`hero_box_items` spójne; `services` w `get_context` użyte w szablonie indeksu; `ServicesIndexPage`/`ServicePage` spójne wszędzie; parent/subpage_types tworzą poprawny łańcuch PillarPage → ServicesIndexPage → ServicePage.

**Punkty uwagi przy wykonaniu:**
- Testy tworzą `PillarPage` jako rodzica (bo `ServicesIndexPage.parent_page_types=["home.PillarPage"]`) — fixture `klaster` to robi.
- Seed: katalog tworzony tylko gdy istnieje filar `klaster` i nie ma jeszcze `uslugi` (idempotencja). Strony usług pod katalogiem.
- `chip chip--lime` / `chip--dark`, `faq`, `offerings`, `offering` — klasy z istniejącego `styles.css` (sprawdzone w mockupie).
```
