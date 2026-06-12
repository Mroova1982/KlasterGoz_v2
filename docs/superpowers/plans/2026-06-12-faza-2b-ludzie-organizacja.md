# Faza 2b — Ludzie i organizacja (filar Klaster) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dodać pod `/klaster` cztery strony filaru Klaster — `AboutClusterPage` (`/o-klastrze`), `MembersIndexPage` (`/czlonkowie`), `TeamPage` (`/zespol`), `PartnersPage` (`/partnerzy`) — wraz ze snippetami `Member`, `TeamMember`, `Partner`, w pełni edytowalne w panelu Wagtail.

**Architecture:** Nowy app `apps/cluster`. Snippety `Member`/`TeamMember`/`Partner` (reużywalne — w 2c użyje ich Showroom). Strony dziedziczą `BasePage`. `AboutClusterPage` = hero + StreamField `body` z małą paletą bloków (`text_section`, `cards`, `steps`, każdy z opcjonalnym tłem) — long-form, pełna kontrola redaktora. `MembersIndexPage` listuje/ filtruje `Member` (po sektorze, alfabetycznie) w `get_context`; `TeamPage` grupuje `TeamMember` po `group`; `PartnersPage` grupuje `Partner` po `type`. Treść startową dokłada idempotentny seed.

**Tech Stack:** Wagtail 6.3 / Django 5.1 / Python 3.13. Testy: pytest + pytest-django (SQLite, static non-manifest). uv: `C:\Users\tmrow\.local\bin\uv.exe` (PowerShell, `Set-Location C:\Programer\Projekty\KlasterGoz_v2` najpierw; benign Postgres timeout w makemigrations/check OK).

> **Carry-over z 2a (naprawiane w Task 5):** w szablonach `apps/services` `data-page="doradztwo"` → `"klaster"` (poprawny active-nav highlight, bo usługi są pod filarem Klaster).

---

## Mapa plików
- Modify: `klastergoz/settings/base.py` (+`apps.cluster`)
- Create: `apps/cluster/__init__.py`, `apps.py`, `models.py`, `blocks.py`
- Create: `apps/cluster/migrations/`
- Create: `apps/cluster/templates/cluster/{about_cluster_page,members_index_page,team_page,partners_page}.html`
- Create: `apps/cluster/tests/__init__.py`, `test_snippets.py`, `test_models.py`, `test_render.py`
- Create: `apps/cluster/README.md`
- Modify: `apps/pages/management/commands/seed_initial_content.py` (seed 4 stron + przykładowe snippety)
- Modify: `apps/pages/tests/test_seed.py`
- Modify (carry-over): `apps/services/templates/services/service_page.html`, `services_index_page.html`
- Create: `docs/przewodnik-moderatora/12-o-klastrze.md` (rozdział przewodnika — DoD #5)

Drzewo: `PillarPage(/klaster)` → `AboutClusterPage`, `MembersIndexPage`, `TeamPage`, `PartnersPage`.

---

## Konwencje testów
Fixture rodzica (PillarPage):
```python
import pytest
from wagtail.models import Site
from apps.home.models import PillarPage

@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    p = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=p)
    p.save_revision().publish()
    return p
```

---

## Task 1: App `apps/cluster` + snippety Member / TeamMember / Partner

**Files:** Modify `klastergoz/settings/base.py`; Create `apps/cluster/__init__.py`, `apps.py`, `models.py`, `apps/cluster/tests/__init__.py`, `test_snippets.py`.

- [ ] **Step 1: Scaffold.** `apps/cluster/__init__.py` (empty). `apps/cluster/apps.py`:
```python
from django.apps import AppConfig


class ClusterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cluster"
    verbose_name = "Klaster — ludzie i organizacja"
```
Add `"apps.cluster"` to `INSTALLED_APPS` (after `"apps.services"`).

- [ ] **Step 2: `apps/cluster/models.py`** (snippets only this task):
```python
"""Filar Klaster: snippety (Member, TeamMember, Partner) + strony (dalej w kolejnych zadaniach)."""
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Member(models.Model):
    """Członek klastra (firma/instytucja)."""

    SECTOR_CHOICES = [
        ("recykling", "Recykling"),
        ("produkcja", "Produkcja"),
        ("technologie", "Technologie"),
        ("nauka", "Nauka"),
        ("doradztwo", "Doradztwo"),
        ("finanse", "Finanse"),
        ("administracja", "Administracja"),
    ]
    name = models.CharField("Nazwa", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True)
    sector = models.CharField("Sektor", max_length=20, choices=SECTOR_CHOICES, default="recykling")
    description = models.TextField("Opis", blank=True)
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    website = models.URLField("Strona WWW", blank=True)
    is_featured = models.BooleanField("Wyróżniony", default=False)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("sector"),
        FieldPanel("description"),
        FieldPanel("logo"),
        FieldPanel("website"),
        FieldPanel("is_featured"),
    ]

    def initials(self) -> str:
        parts = [w for w in self.name.replace("|", " ").split() if w]
        return "".join(w[0] for w in parts[:2]).upper()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Członek"
        verbose_name_plural = "Członkowie"


@register_snippet
class TeamMember(models.Model):
    """Osoba z zespołu klastra."""

    GROUP_CHOICES = [
        ("zarzad", "Zarząd i koordynator"),
        ("biuro", "Biuro klastra"),
        ("rada", "Rada klastra"),
    ]
    name = models.CharField("Imię i nazwisko", max_length=160)
    role = models.CharField("Rola", max_length=160, blank=True)
    group = models.CharField("Grupa", max_length=20, choices=GROUP_CHOICES, default="biuro")
    photo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    bio = models.TextField("Bio", blank=True)
    email = models.EmailField("E-mail", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    sort_order = models.IntegerField("Kolejność", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("group"),
        FieldPanel("photo"),
        FieldPanel("bio"),
        FieldPanel("email"),
        FieldPanel("linkedin"),
        FieldPanel("sort_order"),
    ]

    def initials(self) -> str:
        parts = [w for w in self.name.split() if w]
        return "".join(w[0] for w in parts[:2]).upper()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Osoba zespołu"
        verbose_name_plural = "Zespół"


@register_snippet
class Partner(models.Model):
    """Partner klastra (instytucja / uczelnia / klaster UE / branżowy)."""

    TYPE_CHOICES = [
        ("instytucja", "Instytucja publiczna"),
        ("uczelnia", "Uczelnia / jednostka naukowa"),
        ("klaster_ue", "Klaster partnerski w UE"),
        ("branzowy", "Partner branżowy"),
    ]
    name = models.CharField("Nazwa", max_length=200)
    type = models.CharField("Typ", max_length=20, choices=TYPE_CHOICES, default="instytucja")
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    link = models.URLField("Link", blank=True)
    sort_order = models.IntegerField("Kolejność", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("type"),
        FieldPanel("logo"),
        FieldPanel("link"),
        FieldPanel("sort_order"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Partner"
        verbose_name_plural = "Partnerzy"
```

- [ ] **Step 3: Migracja** — `& C:\Users\tmrow\.local\bin\uv.exe run python manage.py makemigrations cluster` → `0001_initial.py` (Member, TeamMember, Partner).

- [ ] **Step 4: `apps/cluster/tests/__init__.py`** (empty) + `test_snippets.py`:
```python
import pytest

from apps.cluster.models import Member, TeamMember, Partner


@pytest.mark.django_db
def test_member_initials_and_str():
    m = Member.objects.create(name="Stena Recycling", slug="stena", sector="recykling")
    assert m.initials() == "SR"
    assert str(m) == "Stena Recycling"


@pytest.mark.django_db
def test_member_ordering_alphabetical():
    Member.objects.create(name="Zeta", slug="zeta")
    Member.objects.create(name="Alfa", slug="alfa")
    assert list(Member.objects.values_list("name", flat=True)) == ["Alfa", "Zeta"]


@pytest.mark.django_db
def test_teammember_group_and_order():
    TeamMember.objects.create(name="Jan Kowalski", group="zarzad", sort_order=1)
    TeamMember.objects.create(name="Anna Nowak", group="zarzad", sort_order=0)
    first = TeamMember.objects.filter(group="zarzad").first()
    assert first.name == "Anna Nowak"
    assert first.initials() == "AN"


@pytest.mark.django_db
def test_partner_type_choices():
    p = Partner.objects.create(name="PARP", type="instytucja")
    assert p.get_type_display() == "Instytucja publiczna"
```

- [ ] **Step 5: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/cluster/tests/test_snippets.py -v` → 4 PASSED. check clean. Full suite no regression.

- [ ] **Step 6: Commit**
```
git add klastergoz/settings/base.py apps/cluster/__init__.py apps/cluster/apps.py apps/cluster/models.py apps/cluster/migrations/ apps/cluster/tests/__init__.py apps/cluster/tests/test_snippets.py
git commit -m "feat(faza-2b): snippety Member + TeamMember + Partner (apps/cluster)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Strony MembersIndexPage / TeamPage / PartnersPage (modele)

**Files:** Modify `apps/cluster/models.py` (append); Create `apps/cluster/tests/test_models.py`.

- [ ] **Step 1: Rozszerz importy** na górze `apps/cluster/models.py`:
```python
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from apps.shared.models import BasePage
```

- [ ] **Step 2: Append na końcu `apps/cluster/models.py`:**
```python
class MembersIndexPage(BasePage):
    """Lista członków pod /klaster/czlonkowie — filtrowalna po sektorze."""

    eyebrow = models.CharField(max_length=80, blank=True, default="Społeczność klastra")
    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [FieldPanel("eyebrow"), FieldPanel("intro")]
    promote_panels = BasePage.promote_panels
    template = "cluster/members_index_page.html"
    parent_page_types = ["home.PillarPage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request):
        from apps.cluster.models import Member
        ctx = super().get_context(request)
        active = request.GET.get("sektor", "")
        members = Member.objects.all()
        if active:
            members = members.filter(sector=active)
        ctx["members"] = members
        ctx["active_sector"] = active
        ctx["sectors"] = Member.SECTOR_CHOICES
        return ctx

    class Meta:
        verbose_name = "Lista członków"


class TeamPage(BasePage):
    """Zespół pod /klaster/zespol — osoby pogrupowane (zarząd / biuro / rada)."""

    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [FieldPanel("intro")]
    promote_panels = BasePage.promote_panels
    template = "cluster/team_page.html"
    parent_page_types = ["home.PillarPage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request):
        from apps.cluster.models import TeamMember
        ctx = super().get_context(request)
        groups = []
        for value, label in TeamMember.GROUP_CHOICES:
            people = TeamMember.objects.filter(group=value)
            if people:
                groups.append({"label": label, "people": people})
        ctx["groups"] = groups
        return ctx

    class Meta:
        verbose_name = "Zespół"


class PartnersPage(BasePage):
    """Partnerzy pod /klaster/partnerzy — pogrupowani po typie."""

    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [FieldPanel("intro")]
    promote_panels = BasePage.promote_panels
    template = "cluster/partners_page.html"
    parent_page_types = ["home.PillarPage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request):
        from apps.cluster.models import Partner
        ctx = super().get_context(request)
        groups = []
        for value, label in Partner.TYPE_CHOICES:
            items = Partner.objects.filter(type=value)
            if items:
                groups.append({"label": label, "items": items})
        ctx["groups"] = groups
        return ctx

    class Meta:
        verbose_name = "Partnerzy"
```

- [ ] **Step 3: Migracja** — `makemigrations cluster` → migracja z MembersIndexPage, TeamPage, PartnersPage.

- [ ] **Step 4: `apps/cluster/tests/test_models.py`:**
```python
import pytest
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.cluster.models import MembersIndexPage, TeamPage, PartnersPage, Member, TeamMember, Partner


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    p = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=p)
    p.save_revision().publish()
    return p


@pytest.mark.django_db
def test_members_index_filters_by_sector(klaster, rf):
    idx = MembersIndexPage(title="Członkowie", slug="czlonkowie")
    klaster.add_child(instance=idx)
    Member.objects.create(name="RecFirma", slug="rec", sector="recykling")
    Member.objects.create(name="ProdFirma", slug="prod", sector="produkcja")
    req = rf.get("/klaster/czlonkowie/?sektor=recykling")
    ctx = idx.get_context(req)
    names = [m.name for m in ctx["members"]]
    assert names == ["RecFirma"]
    assert ctx["active_sector"] == "recykling"


@pytest.mark.django_db
def test_team_groups(klaster, rf):
    page = TeamPage(title="Zespół", slug="zespol")
    klaster.add_child(instance=page)
    TeamMember.objects.create(name="Jan", group="zarzad")
    ctx = page.get_context(rf.get("/"))
    labels = [g["label"] for g in ctx["groups"]]
    assert "Zarząd i koordynator" in labels


@pytest.mark.django_db
def test_partners_groups(klaster, rf):
    page = PartnersPage(title="Partnerzy", slug="partnerzy")
    klaster.add_child(instance=page)
    Partner.objects.create(name="PARP", type="instytucja")
    ctx = page.get_context(rf.get("/"))
    labels = [g["label"] for g in ctx["groups"]]
    assert "Instytucja publiczna" in labels
```
(`rf` to wbudowany fixture pytest-django = RequestFactory.)

- [ ] **Step 5: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/cluster/tests/test_models.py -v` → 3 PASSED. check clean. Full suite no regression.

- [ ] **Step 6: Commit**
```
git add apps/cluster/models.py apps/cluster/migrations/ apps/cluster/tests/test_models.py
git commit -m "feat(faza-2b): MembersIndexPage + TeamPage + PartnersPage (modele + grupowanie/filtr)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: AboutClusterPage — bloki + model

**Files:** Create `apps/cluster/blocks.py`; Modify `apps/cluster/models.py`; Modify `apps/cluster/tests/test_models.py` (append).

- [ ] **Step 1: `apps/cluster/blocks.py`:**
```python
"""Bloki StreamField dla AboutClusterPage (sekcje long-form 'O klastrze')."""
from wagtail import blocks

BACKGROUNDS = [("none", "Białe"), ("green", "Zielone"), ("dark", "Ciemne")]


class TextSectionBlock(blocks.StructBlock):
    """Sekcja tekstowa: nadtytuł + nagłówek + treść."""

    eyebrow = blocks.CharBlock(required=False, label="Nadtytuł")
    heading = blocks.CharBlock(required=False, label="Nagłówek")
    body = blocks.RichTextBlock(label="Treść", features=["bold", "italic", "link", "ul", "ol"])
    background = blocks.ChoiceBlock(choices=BACKGROUNDS, default="none", label="Tło")

    class Meta:
        icon = "doc-full"
        label = "Sekcja tekstowa"
        template = "cluster/blocks/text_section.html"


class CardBlock(blocks.StructBlock):
    number = blocks.CharBlock(required=False, label="Numer")
    title = blocks.CharBlock(label="Tytuł")
    text = blocks.TextBlock(required=False, label="Opis")


class CardsBlock(blocks.StructBlock):
    """Siatka kart (np. obszary działań / korzyści)."""

    eyebrow = blocks.CharBlock(required=False, label="Nadtytuł")
    heading = blocks.CharBlock(required=False, label="Nagłówek")
    cards = blocks.ListBlock(CardBlock(), label="Karty")
    background = blocks.ChoiceBlock(choices=BACKGROUNDS, default="none", label="Tło")

    class Meta:
        icon = "list-ul"
        label = "Siatka kart"
        template = "cluster/blocks/cards.html"


class StepsBlock(blocks.StructBlock):
    """Numerowane kroki (np. droga do klastra)."""

    eyebrow = blocks.CharBlock(required=False, label="Nadtytuł")
    heading = blocks.CharBlock(required=False, label="Nagłówek")
    steps = blocks.ListBlock(CardBlock(), label="Kroki")
    background = blocks.ChoiceBlock(choices=BACKGROUNDS, default="none", label="Tło")

    class Meta:
        icon = "list-ol"
        label = "Kroki"
        template = "cluster/blocks/steps.html"
```

- [ ] **Step 2: Append AboutClusterPage** do `apps/cluster/models.py`. Najpierw dodaj importy `StreamField` i `blocks` na górze (rozszerz blok importów):
```python
from wagtail.fields import RichTextField, StreamField
from apps.cluster import blocks as cluster_blocks
```
Następnie na końcu pliku:
```python
class AboutClusterPage(BasePage):
    """O klastrze pod /klaster/o-klastrze — long-form (StreamField)."""

    eyebrow = models.CharField(max_length=120, blank=True, default="Krajowy Klaster Kluczowy · od 2012")
    hero_lead = models.TextField("Lead w hero", blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    body = StreamField(
        [
            ("text_section", cluster_blocks.TextSectionBlock()),
            ("cards", cluster_blocks.CardsBlock()),
            ("steps", cluster_blocks.StepsBlock()),
        ],
        blank=True,
        help_text="Sekcje strony O klastrze.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("eyebrow"),
        FieldPanel("hero_lead"),
        FieldPanel("hero_image"),
        FieldPanel("body"),
    ]
    promote_panels = BasePage.promote_panels
    template = "cluster/about_cluster_page.html"
    parent_page_types = ["home.PillarPage"]
    subpage_types = ["cluster.TeamPage", "cluster.PartnersPage"]
    max_count = 1

    class Meta:
        verbose_name = "O klastrze"
```
> Uwaga: `subpage_types` AboutClusterPage zawiera TeamPage+PartnersPage, bo w mockupie breadcrumbs `O klastrze → Zespół/Partnerzy`. ALE `TeamPage.parent_page_types`/`PartnersPage.parent_page_types` z Task 2 to `["home.PillarPage"]`. Aby zespół/partnerzy mogły być pod `/klaster` (a nie pod /o-klastrze), ZOSTAW ich parent jako PillarPage i USUŃ TeamPage/PartnersPage z `subpage_types` AboutClusterPage (ustaw `subpage_types = []`). Czyli finalnie:
```python
    subpage_types = []
```
(Wszystkie 4 strony są bezpośrednio pod `/klaster`. Breadcrumb „O klastrze" w zespole/partnerach to tylko wizualny ślad z mockupu — nie wymusza hierarchii.)

- [ ] **Step 3: Migracja** — `makemigrations cluster` → migracja z AboutClusterPage.

- [ ] **Step 4: Append test do `apps/cluster/tests/test_models.py`:**
```python
@pytest.mark.django_db
def test_about_page_body_streamfield(klaster):
    from apps.cluster.models import AboutClusterPage
    page = AboutClusterPage(title="O klastrze", slug="o-klastrze", hero_lead="...")
    page.body = [
        {"type": "text_section", "value": {"eyebrow": "Misja", "heading": "Współpraca", "body": "<p>Tekst.</p>", "background": "none"}},
        {"type": "steps", "value": {"heading": "Droga", "steps": [{"number": "01", "title": "Deklaracja", "text": "..."}], "background": "dark"}},
    ]
    klaster.add_child(instance=page)
    page.save_revision().publish()
    reloaded = AboutClusterPage.objects.get(slug="o-klastrze")
    assert reloaded.body[0].block_type == "text_section"
    assert reloaded.body[1].value["steps"][0]["title"] == "Deklaracja"
```

- [ ] **Step 5: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/cluster/tests/test_models.py -v` → 4 PASSED. check clean. Full suite no regression.

- [ ] **Step 6: Commit**
```
git add apps/cluster/blocks.py apps/cluster/models.py apps/cluster/migrations/ apps/cluster/tests/test_models.py
git commit -m "feat(faza-2b): AboutClusterPage (StreamField body + bloki)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Szablony (about / members / team / partners + bloki) + render testy

**Files:** Create `apps/cluster/templates/cluster/*.html` + `apps/cluster/templates/cluster/blocks/*.html`; Create `apps/cluster/tests/test_render.py`.

- [ ] **Step 1: Bloki — `apps/cluster/templates/cluster/blocks/text_section.html`:**
```django
{% load wagtailcore_tags %}
<section class="section{% if value.background == 'green' %} bg-green{% elif value.background == 'dark' %} bg-dark{% endif %}">
  <div class="container">
    {% if value.eyebrow or value.heading %}<div class="section-head"><div>{% if value.eyebrow %}<span class="eyebrow">{{ value.eyebrow }}</span>{% endif %}{% if value.heading %}<h2 style="margin-top:14px;">{{ value.heading }}</h2>{% endif %}</div></div>{% endif %}
    <div class="article">{{ value.body|richtext }}</div>
  </div>
</section>
```
`apps/cluster/templates/cluster/blocks/cards.html`:
```django
<section class="section{% if value.background == 'green' %} bg-green{% elif value.background == 'dark' %} bg-dark{% endif %}">
  <div class="container">
    {% if value.eyebrow or value.heading %}<div class="section-head"><div>{% if value.eyebrow %}<span class="eyebrow">{{ value.eyebrow }}</span>{% endif %}{% if value.heading %}<h2 style="margin-top:14px;">{{ value.heading }}</h2>{% endif %}</div></div>{% endif %}
    <div class="policies-grid">
      {% for c in value.cards %}
      <div class="policy">{% if c.number %}<span class="num">{{ c.number }}</span>{% endif %}<h3>{{ c.title }}</h3>{% if c.text %}<p>{{ c.text }}</p>{% endif %}</div>
      {% endfor %}
    </div>
  </div>
</section>
```
`apps/cluster/templates/cluster/blocks/steps.html`:
```django
<section class="section{% if value.background == 'green' %} bg-green{% elif value.background == 'dark' %} bg-dark{% endif %}">
  <div class="container">
    {% if value.eyebrow or value.heading %}<div class="section-head"><div>{% if value.eyebrow %}<span class="eyebrow">{{ value.eyebrow }}</span>{% endif %}{% if value.heading %}<h2 style="margin-top:14px;">{{ value.heading }}</h2>{% endif %}</div></div>{% endif %}
    <ol class="steps">
      {% for s in value.steps %}
      <li><span class="step-num">{{ s.number }}</span><h4>{{ s.title }}</h4>{% if s.text %}<p>{{ s.text }}</p>{% endif %}</li>
      {% endfor %}
    </ol>
  </div>
</section>
```

- [ ] **Step 2: `apps/cluster/templates/cluster/about_cluster_page.html`:**
```django
{% extends "base.html" %}
{% load wagtailcore_tags wagtailimages_tags %}
{% block body_attrs %}data-page="klaster"{% endblock %}
{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li>{% if page.get_parent %}<li><a href="{% pageurl page.get_parent %}">{{ page.get_parent.title }}</a></li>{% endif %}<li>{{ page.title }}</li></ul>
    {% if page.eyebrow %}<span class="eyebrow">{{ page.eyebrow }}</span>{% endif %}
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.hero_lead %}<p class="lead">{{ page.hero_lead }}</p>{% endif %}
  </div>
</section>
{% for block in page.body %}{% include_block block %}{% endfor %}
{% endblock %}
```

- [ ] **Step 3: `apps/cluster/templates/cluster/members_index_page.html`:**
```django
{% extends "base.html" %}
{% load wagtailcore_tags wagtailimages_tags %}
{% block body_attrs %}data-page="klaster"{% endblock %}
{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li><li>{{ page.title }}</li></ul>
    {% if page.eyebrow %}<span class="eyebrow">{{ page.eyebrow }}</span>{% endif %}
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.intro %}<div class="lead">{{ page.intro|richtext }}</div>{% endif %}
  </div>
</section>
<section class="section--tight">
  <div class="container">
    <div class="tab-row">
      <a href="{{ page.url }}" class="{% if not active_sector %}active{% endif %}">Wszyscy</a>
      {% for value, label in sectors %}<a href="{{ page.url }}?sektor={{ value }}" class="{% if active_sector == value %}active{% endif %}">{{ label }}</a>{% endfor %}
    </div>
  </div>
</section>
<section class="section" style="padding-top: 0;">
  <div class="container">
    <div class="member-grid">
      {% for m in members %}
      <a class="member" href="{{ m.website|default:'#' }}"{% if m.website %} target="_blank" rel="noopener"{% endif %}>
        <div class="member-logo">{% if m.logo %}{% image m.logo height-48 %}{% else %}{{ m.initials }}{% endif %}</div>
        <small>{{ m.get_sector_display }}</small>
        <h4>{{ m.name }}</h4>
        {% if m.description %}<p style="margin:0; font-size:13.5px; color: var(--ink-500);">{{ m.description }}</p>{% endif %}
      </a>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
```

- [ ] **Step 4: `apps/cluster/templates/cluster/team_page.html`:**
```django
{% extends "base.html" %}
{% load wagtailimages_tags wagtailcore_tags %}
{% block body_attrs %}data-page="klaster"{% endblock %}
{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li><li>{{ page.title }}</li></ul>
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.intro %}<div class="lead">{{ page.intro|richtext }}</div>{% endif %}
  </div>
</section>
<section class="section">
  <div class="container">
    {% for g in groups %}
    <div class="section-head"{% if not forloop.first %} style="margin-top: 80px;"{% endif %}><div><span class="eyebrow">{{ g.label }}</span></div></div>
    <div class="team-grid">
      {% for p in g.people %}
      <div class="person"><div class="person-photo">{% if p.photo %}{% image p.photo fill-160x160 %}{% else %}{{ p.initials }}{% endif %}</div><h4>{{ p.name }}</h4>{% if p.role %}<small>{{ p.role }}</small>{% endif %}</div>
      {% endfor %}
    </div>
    {% endfor %}
  </div>
</section>
{% endblock %}
```

- [ ] **Step 5: `apps/cluster/templates/cluster/partners_page.html`:**
```django
{% extends "base.html" %}
{% load wagtailimages_tags wagtailcore_tags %}
{% block body_attrs %}data-page="klaster"{% endblock %}
{% block content %}
<section class="page-header">
  <div class="container">
    <ul class="crumbs"><li><a href="/">Strona główna</a></li><li>{{ page.title }}</li></ul>
    <h1 style="margin-top: 16px;">{{ page.title }}</h1>
    {% if page.intro %}<div class="lead">{{ page.intro|richtext }}</div>{% endif %}
  </div>
</section>
<section class="section">
  <div class="container">
    {% for g in groups %}
    <div class="section-head"{% if not forloop.first %} style="margin-top: 80px;"{% endif %}><div><span class="eyebrow">{{ g.label }}</span></div></div>
    <div class="logos">
      {% for p in g.items %}<div>{% if p.logo %}{% image p.logo height-40 alt=p.name %}{% else %}{{ p.name }}{% endif %}</div>{% endfor %}
    </div>
    {% endfor %}
  </div>
</section>
{% endblock %}
```

- [ ] **Step 6: `apps/cluster/tests/test_render.py`:**
```python
import pytest
from django.test import Client
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.cluster.models import (
    MembersIndexPage, TeamPage, PartnersPage, AboutClusterPage,
    Member, TeamMember, Partner,
)


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    p = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=p)
    p.save_revision().publish()
    return p


@pytest.mark.django_db
def test_members_page_renders_and_filters(klaster):
    idx = MembersIndexPage(title="Członkowie", slug="czlonkowie")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    Member.objects.create(name="RecFirma", slug="rec", sector="recykling")
    Member.objects.create(name="ProdFirma", slug="prod", sector="produkcja")
    html = Client().get("/klaster/czlonkowie/").content.decode()
    assert "RecFirma" in html and "ProdFirma" in html and "site-header" in html
    filtered = Client().get("/klaster/czlonkowie/?sektor=recykling").content.decode()
    assert "RecFirma" in filtered and "ProdFirma" not in filtered


@pytest.mark.django_db
def test_team_page_renders_groups(klaster):
    page = TeamPage(title="Zespół", slug="zespol")
    klaster.add_child(instance=page)
    page.save_revision().publish()
    TeamMember.objects.create(name="Jan Kowalski", role="Prezes", group="zarzad")
    html = Client().get("/klaster/zespol/").content.decode()
    assert "Jan Kowalski" in html and "Zarząd i koordynator" in html


@pytest.mark.django_db
def test_partners_page_renders_groups(klaster):
    page = PartnersPage(title="Partnerzy", slug="partnerzy")
    klaster.add_child(instance=page)
    page.save_revision().publish()
    Partner.objects.create(name="PARP", type="instytucja")
    html = Client().get("/klaster/partnerzy/").content.decode()
    assert "PARP" in html and "Instytucja publiczna" in html


@pytest.mark.django_db
def test_about_page_renders_blocks(klaster):
    page = AboutClusterPage(title="O klastrze", slug="o-klastrze", hero_lead="Lead")
    page.body = [{"type": "text_section", "value": {"heading": "Misja klastra", "body": "<p>Tekst.</p>", "background": "green", "eyebrow": ""}}]
    klaster.add_child(instance=page)
    page.save_revision().publish()
    html = Client().get("/klaster/o-klastrze/").content.decode()
    assert "Misja klastra" in html and "bg-green" in html and "site-header" in html
```

- [ ] **Step 7: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/cluster/tests/ -v` → all PASSED. check clean. Full suite no regression.

- [ ] **Step 8: Commit**
```
git add apps/cluster/templates/ apps/cluster/tests/test_render.py
git commit -m "feat(faza-2b): szablony about/members/team/partners + bloki + render testy" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Seed 4 stron + przykładowe snippety + carry-over fix

**Files:** Modify `apps/pages/management/commands/seed_initial_content.py`, `apps/pages/tests/test_seed.py`, `apps/services/templates/services/*.html`.

- [ ] **Step 1: Carry-over fix** — w `apps/services/templates/services/service_page.html` i `services_index_page.html` zmień `{% block body_attrs %}data-page="doradztwo"{% endblock %}` → `{% block body_attrs %}data-page="klaster"{% endblock %}` (usługi są pod filarem Klaster → poprawne podświetlenie menu).

- [ ] **Step 2: Rozszerz importy** w `seed_initial_content.py`:
```python
from apps.cluster.models import (
    AboutClusterPage, MembersIndexPage, TeamPage, PartnersPage,
    Member, TeamMember, Partner,
)
```

- [ ] **Step 3: Po seedzie usług (blok `uslugi`), dodaj seed stron Klaster** (wewnątrz `transaction.atomic()`):
```python
        # --- Strony filaru Klaster: o-klastrze / czlonkowie / zespol / partnerzy ---
        klaster_pillar = Page.objects.filter(slug="klaster").first()
        if klaster_pillar:
            if not Page.objects.filter(slug="o-klastrze").exists():
                about = AboutClusterPage(
                    title="O klastrze", slug="o-klastrze",
                    hero_lead="Platforma kooperacji firm, nauki, instytucji i samorządów wokół GOZ.",
                    body=[{"type": "text_section", "value": {"eyebrow": "Misja", "heading": "Tworzymy środowisko współpracy.", "body": "<p>Treść do uzupełnienia w panelu administracyjnym.</p>", "background": "none"}}],
                )
                klaster_pillar.add_child(instance=about)
                about.save_revision().publish()
            if not Page.objects.filter(slug="czlonkowie").exists():
                m = MembersIndexPage(title="Członkowie", slug="czlonkowie", intro="<p>150+ firm i instytucji w polskim ekosystemie GOZ.</p>")
                klaster_pillar.add_child(instance=m)
                m.save_revision().publish()
            if not Page.objects.filter(slug="zespol").exists():
                t = TeamPage(title="Zespół", slug="zespol", intro="<p>Koordynator, biuro i rada klastra.</p>")
                klaster_pillar.add_child(instance=t)
                t.save_revision().publish()
            if not Page.objects.filter(slug="partnerzy").exists():
                p = PartnersPage(title="Partnerzy", slug="partnerzy", intro="<p>Instytucje, uczelnie i klastry partnerskie.</p>")
                klaster_pillar.add_child(instance=p)
                p.save_revision().publish()
        # przykładowe snippety (raz)
        if not Member.objects.exists():
            for name, slug, sector in [("Stena Recycling", "stena-recycling", "recykling"), ("BioPaper Polska", "biopaper", "produkcja"), ("CyrkulaTech", "cyrkulatech", "technologie")]:
                Member.objects.create(name=name, slug=slug, sector=sector)
        if not TeamMember.objects.exists():
            TeamMember.objects.create(name="dr Jan Kowalski", role="Prezes Zarządu, Koordynator", group="zarzad", sort_order=0)
            TeamMember.objects.create(name="Anna Wójcik", role="Specjalista ds. członkostwa", group="biuro", sort_order=0)
        if not Partner.objects.exists():
            Partner.objects.create(name="PARP", type="instytucja", sort_order=0)
            Partner.objects.create(name="Politechnika Warszawska", type="uczelnia", sort_order=0)
```

- [ ] **Step 4: Test do `apps/pages/tests/test_seed.py`:**
```python
@pytest.mark.django_db
def test_seed_creates_cluster_pages():
    from wagtail.models import Page
    from apps.cluster.models import Member
    call_command("seed_initial_content")
    for slug in ["o-klastrze", "czlonkowie", "zespol", "partnerzy"]:
        assert Page.objects.filter(slug=slug).exists(), f"brak strony {slug}"
    assert Member.objects.exists()


@pytest.mark.django_db
def test_seed_cluster_idempotent():
    from wagtail.models import Page
    from apps.cluster.models import Member
    call_command("seed_initial_content")
    call_command("seed_initial_content")
    assert Page.objects.filter(slug="o-klastrze").count() == 1
    assert Member.objects.filter(slug="stena-recycling").count() == 1
```

- [ ] **Step 5: Run** `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/pages/tests/test_seed.py -v` → all PASSED (existing + 2 new). Full suite no regression.

- [ ] **Step 6: Commit**
```
git add apps/pages/management/commands/seed_initial_content.py apps/pages/tests/test_seed.py apps/services/templates/services/
git commit -m "feat(faza-2b): seed stron Klaster + przykladowe snippety; fix data-page uslug" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: Dokumentacja (przewodnik + README) + DoD lint/testy

**Files:** Create `docs/przewodnik-moderatora/12-o-klastrze.md`, `apps/cluster/README.md`; guide test.

- [ ] **Step 1: `docs/przewodnik-moderatora/12-o-klastrze.md`:**
```markdown
# Klaster — o klastrze, członkowie, zespół, partnerzy

Strony filaru Klaster, pod **/klaster** w drzewie Pages.

## O klastrze
**Co steruje:** stronę `/klaster/o-klastrze` — hero (nadtytuł, lead, obraz) + dowolne sekcje treści.
**Gdzie edytujesz:** Pages → Klaster → O klastrze. Treść budujesz z bloków: „Sekcja tekstowa", „Siatka kart", „Kroki" — każdy z wyborem tła (białe/zielone/ciemne).

## Członkowie
**Co steruje:** stronę `/klaster/czlonkowie` — listę członków z filtrem po sektorze.
**Gdzie edytujesz:** strona (nadtytuł, wstęp) w Pages → Klaster → Członkowie; samych członków w Snippets → Członkowie (nazwa, sektor, logo, opis, WWW). Lista i zakładki sektorów budują się automatycznie.

## Zespół
**Co steruje:** stronę `/klaster/zespol` — osoby pogrupowane (Zarząd / Biuro / Rada).
**Gdzie edytujesz:** wstęp na stronie; osoby w Snippets → Zespół (imię, rola, grupa, zdjęcie, kolejność). Grupy pojawiają się automatycznie, jeśli mają osoby.

## Partnerzy
**Co steruje:** stronę `/klaster/partnerzy` — logotypy pogrupowane po typie (instytucje / uczelnie / klastry UE / branżowi).
**Gdzie edytujesz:** wstęp na stronie; partnerów w Snippets → Partnerzy (nazwa, typ, logo, link, kolejność).
```

- [ ] **Step 2: `apps/cluster/README.md`:**
```markdown
# apps.cluster

Filar Klaster — ludzie i organizacja.

## Co robi
- Snippety (reużywalne): `Member` (członek; sektor, logo, WWW, initials()), `TeamMember` (osoba; grupa zarzad/biuro/rada), `Partner` (typ instytucja/uczelnia/klaster_ue/branzowy).
- Strony pod `/klaster`: `AboutClusterPage` (StreamField body: text_section/cards/steps), `MembersIndexPage` (filtr po sektorze przez `?sektor=`), `TeamPage` (grupowanie po `group`), `PartnersPage` (grupowanie po `type`). Każda `max_count=1`, parent = `home.PillarPage`.

## Zależności
`apps.shared` (BasePage), `apps.home` (PillarPage jako rodzic). Snippet `Member` używany też przez Showroom/B2B w Fazie 2c.
```

- [ ] **Step 3: Guide test** — append do `apps/guide/tests/test_handbook.py`:
```python
@pytest.mark.django_db
def test_handbook_includes_cluster_chapter():
    User = get_user_model()
    User.objects.create_superuser("mod4", "mod4@example.com", "pass12345")
    c = Client()
    c.force_login(User.objects.get(username="mod4"))
    html = c.get(reverse("guide_handbook")).content.decode()
    assert "o klastrze, członkowie, zespół, partnerzy" in html
```

- [ ] **Step 4: DoD lint + tests:**
```
& C:\Users\tmrow\.local\bin\uv.exe run ruff check --fix .
& C:\Users\tmrow\.local\bin\uv.exe run black .
& C:\Users\tmrow\.local\bin\uv.exe run ruff check .
& C:\Users\tmrow\.local\bin\uv.exe run black --check .
& C:\Users\tmrow\.local\bin\uv.exe run python manage.py check
& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db -q
```
Expected: ruff „All checks passed!", black clean, check clean, all tests PASSED (poprzednie 48 + ~14 nowych ≈ 62).

- [ ] **Step 5: Commit**
```
git add docs/przewodnik-moderatora/12-o-klastrze.md apps/cluster/README.md apps/guide/tests/test_handbook.py
git add -A
git commit -m "docs(faza-2b): rozdzial przewodnika 'Klaster' + README apps/cluster + lint" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
(Jeśli `git add -A` złapałby stray `similf44-master.zip` — NIE dodawaj go.)

---

## Self-Review (autor planu)

**1. Pokrycie 2b (spec 4 + 5.1/5.2):** AboutClusterPage (Task 3+4) ✅; MembersIndexPage + filtr (Task 2+4) ✅; TeamPage + grupowanie (Task 2+4) ✅; PartnersPage + grupowanie (Task 2+4) ✅; snippety Member/TeamMember/Partner (Task 1) ✅; seed (Task 5) ✅; DoD #5 przewodnik (Task 6) ✅; carry-over data-page (Task 5) ✅.

**2. Placeholdery:** brak; cały kod/treść podane. „Treść do uzupełnienia w panelu" w seedzie = celowy placeholder treści edytowalnej.

**3. Spójność nazw:** snippety Member/TeamMember/Partner spójne w modelach, get_context, szablonach, seedzie, testach; `members`/`groups`/`sectors`/`active_sector` z get_context użyte w szablonach; `initials`/`get_sector_display`/`get_type_display` poprawne; bloki text_section/cards/steps mają `template` Meta i pliki w `templates/cluster/blocks/`; parent_page_types wszystkich 4 stron = `home.PillarPage`, każda max_count=1.

**Punkty uwagi:** (a) `include_block` w about wymaga `{% load wagtailcore_tags %}` — jest. (b) TeamPage/PartnersPage `get_context` używają `if people:`/`if items:` — pomijają puste grupy. (c) Member.website jako href; gdy puste → `#`. (d) AboutClusterPage.subpage_types=[] (wszystkie strony bezpośrednio pod /klaster). (e) testy modeli używają fixture `rf` (RequestFactory z pytest-django).
