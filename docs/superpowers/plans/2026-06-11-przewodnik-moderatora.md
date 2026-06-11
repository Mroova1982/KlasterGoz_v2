# Przewodnik moderatora — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dać moderatorowi „Przewodnik moderatora" dostępny wprost w panelu Wagtail (pozycja w menu głównym), renderowany z plików Markdown wersjonowanych w repo, opisujący per-sekcja co za co odpowiada — i rosnący wraz z kolejnymi fazami.

**Architecture:** Nowy app `apps/guide` z `wagtail_hooks.py` (rejestruje URL widoku + pozycję menu głównego) i `views.handbook`, który czyta `docs/przewodnik-moderatora/*.md`, skleja, konwertuje biblioteką `markdown` (z auto-spisem treści) i renderuje w szablonie panelu (`wagtailadmin/base.html`). Treść (źródło prawdy) żyje w `docs/`, nie w kodzie. Widok chroniony `require_admin_access`.

**Tech Stack:** Wagtail 6.3 / Django 5.1 / Python 3.13 / `markdown` (nowa zależność). Testy: pytest + pytest-django (SQLite, static non-manifest w test). uv: `C:\Users\tmrow\.local\bin\uv.exe` (PowerShell, `Set-Location C:\Programer\Projekty\KlasterGoz_v2` najpierw; benign Postgres timeout w makemigrations/check OK).

---

## Mapa plików
- Modify: `pyproject.toml` (dodać `markdown`)
- Modify: `klastergoz/settings/base.py` (dodać `apps.guide` do INSTALLED_APPS)
- Create: `apps/guide/__init__.py`, `apps/guide/apps.py`, `apps/guide/views.py`, `apps/guide/wagtail_hooks.py`
- Create: `apps/guide/templates/guide/handbook.html`
- Create: `apps/guide/tests/__init__.py`, `apps/guide/tests/test_handbook.py`
- Create: `apps/guide/README.md`
- Create: `docs/przewodnik-moderatora/00-wprowadzenie.md`, `10-strona-glowna.md`, `20-filary.md`, `30-strony-statyczne.md`, `40-ustawienia.md`
- Modify: `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md` (DoD sek. 2.2)
- Modify: `README.md` (wskaźnik)

---

## Task 1: Mechanizm — app `apps/guide` + widok + hook + 1 rozdział + testy

**Files:**
- Modify: `pyproject.toml`, `klastergoz/settings/base.py`
- Create: `apps/guide/__init__.py`, `apps/guide/apps.py`, `apps/guide/views.py`, `apps/guide/wagtail_hooks.py`, `apps/guide/templates/guide/handbook.html`
- Create: `docs/przewodnik-moderatora/10-strona-glowna.md`
- Create: `apps/guide/tests/__init__.py`, `apps/guide/tests/test_handbook.py`

- [ ] **Step 1: Dodaj zależność `markdown`**

In `pyproject.toml`, add `"markdown>=3.7"` to the `[project] dependencies` list (after `whitenoise`). Then run `& C:\Users\tmrow\.local\bin\uv.exe sync` to install it.

- [ ] **Step 2: Scaffold app**

Create `apps/guide/__init__.py` (empty).

Create `apps/guide/apps.py`:
```python
from django.apps import AppConfig


class GuideConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.guide"
    verbose_name = "Przewodnik moderatora"
```

Add `"apps.guide"` to `INSTALLED_APPS` in `klastergoz/settings/base.py` — in the local apps block (after `"apps.pages"`).

- [ ] **Step 3: Widok `apps/guide/views.py`**

```python
"""Widok Przewodnika moderatora — renderuje pliki Markdown z docs/przewodnik-moderatora/."""
from pathlib import Path

import markdown as md
from django.conf import settings
from django.shortcuts import render
from wagtail.admin.auth import require_admin_access

GUIDE_DIR = Path(settings.BASE_DIR) / "docs" / "przewodnik-moderatora"
MD_EXTENSIONS = ["toc", "tables", "fenced_code", "sane_lists"]


def _load_markdown() -> str:
    """Skleja wszystkie rozdziały (sort po nazwie pliku) w jeden tekst Markdown."""
    if not GUIDE_DIR.exists():
        return "# Przewodnik moderatora\n\nBrak treści (katalog docs/przewodnik-moderatora/ nie istnieje)."
    chapters = []
    for path in sorted(GUIDE_DIR.glob("*.md")):
        chapters.append(path.read_text(encoding="utf-8"))
    if not chapters:
        return "# Przewodnik moderatora\n\nBrak rozdziałów."
    # [TOC] na górze → rozszerzenie 'toc' wstawi klikalny spis treści z kotwicami.
    return "[TOC]\n\n" + "\n\n---\n\n".join(chapters)


@require_admin_access
def handbook(request):
    html = md.markdown(_load_markdown(), extensions=MD_EXTENSIONS)
    return render(request, "guide/handbook.html", {"content_html": html})
```

- [ ] **Step 4: Hooki `apps/guide/wagtail_hooks.py`**

```python
"""Rejestracja Przewodnika moderatora w panelu Wagtail: URL + pozycja w menu głównym."""
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from apps.guide import views


@hooks.register("register_admin_urls")
def register_guide_url():
    return [path("przewodnik/", views.handbook, name="guide_handbook")]


@hooks.register("register_admin_menu_item")
def register_guide_menu_item():
    return MenuItem(
        "Przewodnik moderatora",
        reverse("guide_handbook"),
        icon_name="help",
        order=10000,  # na dole menu
    )
```

- [ ] **Step 5: Szablon `apps/guide/templates/guide/handbook.html`**

```django
{% extends "wagtailadmin/base.html" %}
{% block titletag %}Przewodnik moderatora{% endblock %}
{% block content %}
  {% include "wagtailadmin/shared/headers/slim_header.html" with title="Przewodnik moderatora" icon="help" %}
  <div class="nice-padding" style="max-width: 900px;">
    <div class="guide-content">{{ content_html|safe }}</div>
  </div>
{% endblock %}
```
> Treść Markdown pochodzi wyłącznie z repo (zaufane źródło), więc `|safe` jest tu akceptowalne.

- [ ] **Step 6: Pierwszy rozdział `docs/przewodnik-moderatora/10-strona-glowna.md`**

```markdown
# Strona główna

Strona główna (`/`) to strona typu **HomePage** — edytujesz ją w **Pages → Klaster GOZ**. Składa się z sekcji; każda jest niezależna i ukrywa się, gdy nie ma treści.

## Strona główna → Slajdy hero
**Co steruje:** duży slider na samej górze (slajdy: nadtytuł, nagłówek, lead, przyciski, tło).
**Gdzie edytujesz:** Pages → Klaster GOZ → „Slajdy hero" (wybierasz snippety **Slajd hero**; same slajdy tworzysz w Snippets → Slajdy hero).
**Wskazówki:** 1–3 slajdy działają najlepiej; pierwszy ładuje się najszybciej. Kursywę w nagłówku robisz przez pogrubienie/kursywę edytora.

## Strona główna → Pasek statystyk (pod hero)
**Co steruje:** poziomy pasek liczb tuż pod sliderem (np. „150+ firm").
**Gdzie edytujesz:** Snippets → Statystyki, grupa **„Home — pasek pod hero"**.
**Wskazówki:** kolejność ustawiasz polem „Kolejność"; zalecane 3–4 pozycje.

## Strona główna → Sekcja „Filary"
**Co steruje:** trzy kafelki filarów (Klaster / Edukacja / Doradztwo) + nagłówek sekcji.
**Gdzie edytujesz:** nagłówek w Pages → Klaster GOZ → „Sekcja: Filary"; kafelki w „Filary (kafelki)" (snippety **Filar** z Snippets → Filary, każdy linkuje do strony filaru).
**Wskazówki:** środkowy kafelek ma wariant ciemny (pole „Wariant ciemny" w snippecie Filar).

## Strona główna → Sekcja „Konsultacja"
**Co steruje:** blok z zachętą do bezpłatnej konsultacji + lista kroków.
**Gdzie edytujesz:** Pages → Klaster GOZ → „Sekcja: Konsultacja" (nagłówek, lead, przycisk) i „Kroki konsultacji".
**Wskazówki:** pełny formularz konsultacji pojawi się w kolejnej fazie; teraz przycisk prowadzi do strony Kontakt.

## Strona główna → Druga sekcja statystyk
**Co steruje:** szerszy blok statystyk w środku strony.
**Gdzie edytujesz:** Snippets → Statystyki, grupa **„Home — sekcja statystyk"**.

## Strona główna → Usługi
**Co steruje:** kafelki usług klastra + nagłówek i przycisk „Cała oferta".
**Gdzie edytujesz:** Pages → Klaster GOZ → „Sekcja: Usługi" i „Kafelki usług".
**Wskazówki:** w przyszłej fazie kafelki mogą zostać zastąpione automatyczną listą stron usług.

## Strona główna → Członkowie (logosy)
**Co steruje:** pas logotypów „Zaufali nam".
**Gdzie edytujesz:** Pages → Klaster GOZ → „Sekcja: Członkowie" i „Logosy członków".

## Strona główna → O klastrze
**Co steruje:** blok tekstowy o klastrze z punktami i obrazem.
**Gdzie edytujesz:** Pages → Klaster GOZ → „Sekcja: O klastrze" (nagłówek, lead, punkty — jeden na linię, przycisk, obraz).

## Strona główna → Aktualności
**Co steruje:** trzy kafelki aktualności + nagłówek i przycisk.
**Gdzie edytujesz:** Pages → Klaster GOZ → „Sekcja: Aktualności" i „Teasery aktualności".
**Wskazówki:** w kolejnej fazie zostaną zastąpione automatyczną listą prawdziwych artykułów.

## Strona główna → CTA strip (pasek na dole)
**Co steruje:** kolorowy pasek wezwania do działania na dole strony.
**Gdzie edytujesz:** Pages → Klaster GOZ → „Sekcja: CTA strip".
```

- [ ] **Step 7: Testy `apps/guide/tests/test_handbook.py`**

Create `apps/guide/tests/__init__.py` (empty) and:
```python
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_handbook_requires_login():
    resp = Client().get(reverse("guide_handbook"))
    assert resp.status_code in (302, 403)
    if resp.status_code == 302:
        assert "/admin/login" in resp.url


@pytest.mark.django_db
def test_handbook_renders_for_admin():
    User = get_user_model()
    User.objects.create_superuser("mod", "mod@example.com", "pass12345")
    c = Client()
    c.force_login(User.objects.get(username="mod"))
    resp = c.get(reverse("guide_handbook"))
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Strona główna" in html          # nagłówek z rozdziału
    assert 'class="toc"' in html            # wygenerowany spis treści (rozszerzenie toc)


@pytest.mark.django_db
def test_menu_item_registered():
    from wagtail import hooks
    items = []
    for fn in hooks.get_hooks("register_admin_menu_item"):
        items.append(fn())
    labels = [getattr(i, "label", "") for i in items]
    assert "Przewodnik moderatora" in labels
```

- [ ] **Step 8: Weryfikacja**

Run:
```
& C:\Users\tmrow\.local\bin\uv.exe run python manage.py check
& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/guide/tests/test_handbook.py -v
```
Expected: check clean; 3 PASSED. If `test_handbook_requires_login` returns 403 instead of 302 (depending on Wagtail's `require_admin_access` behavior for anonymous), the `in (302, 403)` assert still passes — that's intended tolerance.

- [ ] **Step 9: Commit**
```
git add pyproject.toml uv.lock klastergoz/settings/base.py apps/guide/ docs/przewodnik-moderatora/10-strona-glowna.md
git commit -m "feat(guide): Przewodnik moderatora w panelu Wagtail (widok + hook + 1 rozdzial)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Pozostałe rozdziały przewodnika (Faza 0 + 1)

**Files:**
- Create: `docs/przewodnik-moderatora/00-wprowadzenie.md`, `20-filary.md`, `30-strony-statyczne.md`, `40-ustawienia.md`
- Test: rozszerzenie `apps/guide/tests/test_handbook.py`

- [ ] **Step 1: `docs/przewodnik-moderatora/00-wprowadzenie.md`**
```markdown
# Wprowadzenie

Ten przewodnik wyjaśnia, **która sekcja panelu odpowiada za co** na stronie i jak edytować treść. Rośnie wraz z portalem — każda nowa funkcja dokłada tu rozdział.

## Gdzie czego szukać
**Co steruje:** orientacja w panelu.
**Gdzie edytujesz:**
- **Pages** — strony i ich sekcje (strona główna, filary, strony prawne, kontakt).
- **Snippets** — elementy używane wielokrotnie (Slajdy hero, Filary, Statystyki).
- **Settings** — ustawienia całego serwisu (kontakt, menu, stopka, analytics, portale).

## Jak publikować zmiany
**Co steruje:** widoczność zmian na żywej stronie.
**Gdzie edytujesz:** w każdej stronie przyciskiem zapisu.
**Wskazówki:** zmiany zapisujesz jako wersję roboczą („Save draft") albo publikujesz („Publish"). Przed publikacją użyj **podglądu** („Preview"). Każda strona ma **historię wersji** — możesz cofnąć się do wcześniejszej.
```

- [ ] **Step 2: `docs/przewodnik-moderatora/20-filary.md`**
```markdown
# Filary (Klaster / Edukacja / Doradztwo)

Trzy strony-filary to typ **PillarPage** — landingi działów. Edytujesz je w **Pages**, pod stroną główną (Klaster / Edukacja / Doradztwo). Wszystkie mają tę samą budowę.

## Filar → Hero
**Co steruje:** nagłówek strony filaru: nadtytuł (np. „Filar 01 · Klaster"), tytuł, lead, dwa przyciski.
**Gdzie edytujesz:** Pages → wybrany filar → sekcja „Hero".

## Filar → Korzyści
**Co steruje:** siatkę kafelków „co zyskujesz".
**Gdzie edytujesz:** Pages → filar → „Korzyści" (każda: tag, tytuł, opis).

## Filar → Blok „jak działamy"
**Co steruje:** blok tekstowy z nagłówkiem, leadem i punktami.
**Gdzie edytujesz:** Pages → filar → „Blok 'jak działamy'" (punkty: jeden na linię).

## Filar → Kroki procesu
**Co steruje:** numerowane kroki (np. jak dołączyć).
**Gdzie edytujesz:** Pages → filar → „Kroki procesu" (numer, tytuł, opis).

## Filar → CTA strip
**Co steruje:** pasek wezwania do działania na dole.
**Gdzie edytujesz:** Pages → filar → „CTA strip".

## Filar → Podstrony
**Co steruje:** automatyczną listę podstron filaru (np. usługi, szkolenia).
**Gdzie edytujesz:** dodajesz podstrony pod filarem w drzewie Pages — pojawią się automatycznie. Na razie puste; podstrony dochodzą w kolejnych fazach.
```

- [ ] **Step 3: `docs/przewodnik-moderatora/30-strony-statyczne.md`**
```markdown
# Strony prawne i Kontakt

## Strony prawne (RODO / Regulamin / Cookies)
**Co steruje:** treść dokumentów prawnych — typ **LegalPage**.
**Gdzie edytujesz:** Pages → RODO / Regulamin / Cookies → pole „Treść" (bloki: nagłówek, akapit, obraz).
**Wskazówki:** używaj bloku „Nagłówek sekcji" do tytułów i „Tekst" do akapitów; kolejność bloków przeciągasz.

## Kontakt → Formularz
**Co steruje:** pola formularza kontaktowego i powiadomienie e-mail o zgłoszeniu.
**Gdzie edytujesz:** Pages → Kontakt → „Pola formularza" (dodajesz/usuwasz pola) oraz sekcja „Powiadomienie e-mail" (adres odbiorcy).
**Wskazówki:** zgłoszenia trafiają do **Forms** w panelu; jest też ukryte pole-pułapka na spam (nie ruszaj go).

## Kontakt → Karty kontaktowe i mapa
**Co steruje:** kafelki z danymi (biuro, sekretariat…) i osadzona mapa.
**Gdzie edytujesz:** Pages → Kontakt → „Karty kontaktowe" oraz pole „Mapa (embed)".
```

- [ ] **Step 4: `docs/przewodnik-moderatora/40-ustawienia.md`**
```markdown
# Ustawienia serwisu (Settings)

Ustawienia dotyczą **całego portalu** (nie pojedynczej strony). Znajdziesz je w panelu w **Settings**.

## Settings → Dane ogólne
**Co steruje:** nazwę organizacji, telefon, e-mail, adres, logo, opis w stopce.
**Gdzie edytujesz:** Settings → Dane ogólne.
**Wskazówki:** te dane pojawiają się w nagłówku (pasek kontaktu) i stopce na każdej stronie.

## Settings → Social media
**Co steruje:** linki do LinkedIn / Facebook / YouTube w stopce.
**Gdzie edytujesz:** Settings → Social media.

## Settings → Analytics i cookies
**Co steruje:** Google Analytics (GA4) i treść banera cookies.
**Gdzie edytujesz:** Settings → Analytics i cookies.
**Wskazówki:** baner cookies pojawia się dopiero po wpisaniu „GA4 Measurement ID".

## Settings → Nawigacja
**Co steruje:** menu główne w nagłówku.
**Gdzie edytujesz:** Settings → Nawigacja (pozycje menu; każda może linkować do strony lub adresu, mieć rozwijane kolumny).

## Settings → Stopka
**Co steruje:** kolumny linków w stopce, linki prawne (dolny pasek), nagłówki kolumn, teksty newslettera.
**Gdzie edytujesz:** Settings → Stopka.

## Settings → Portale logowania
**Co steruje:** dropdown „Strefa logowania" w nagłówku i listę portali w stopce.
**Gdzie edytujesz:** Settings → Portale logowania (nazwa, opis, adres każdego portalu).
```

- [ ] **Step 5: Rozszerz test renderu** — w `apps/guide/tests/test_handbook.py` dodaj test, że wszystkie obszary się renderują:
```python
@pytest.mark.django_db
def test_handbook_includes_all_chapters():
    User = get_user_model()
    User.objects.create_superuser("mod2", "mod2@example.com", "pass12345")
    c = Client()
    c.force_login(User.objects.get(username="mod2"))
    html = c.get(reverse("guide_handbook")).content.decode()
    for heading in ["Wprowadzenie", "Strona główna", "Filary", "Strony prawne i Kontakt", "Ustawienia serwisu"]:
        assert heading in html, f"brak rozdziału: {heading}"
```

- [ ] **Step 6: Weryfikacja**

Run: `& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db apps/guide/tests/test_handbook.py -v` → 4 PASSED.

- [ ] **Step 7: Commit**
```
git add docs/przewodnik-moderatora/ apps/guide/tests/test_handbook.py
git commit -m "docs(guide): rozdzialy przewodnika dla Fazy 0 i 1 (home/filary/strony/ustawienia)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: DoD w master specu + README + DoD lint/testy

**Files:**
- Modify: `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md` (sek. 2.2)
- Create: `apps/guide/README.md`
- Modify: `README.md`

- [ ] **Step 1: Dopisz punkt do DoD (master spec, sekcja 2.2)**

W `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md`, w sekcji „2.2 Definition of Done per faza", po punkcie 4 (Dokumentacja) dodaj punkt 5:
```markdown
5. **Przewodnik moderatora zaktualizowany** — dla każdego nowego typu strony / sekcji / ustawienia dodano lub rozszerzono odpowiedni rozdział w `docs/przewodnik-moderatora/` (renderowany w panelu Wagtail, menu „Przewodnik moderatora").
```

- [ ] **Step 2: `apps/guide/README.md`**
```markdown
# apps.guide

Przewodnik moderatora w panelu Wagtail.

## Co robi
- Pozycja „Przewodnik moderatora" w menu głównym panelu (hook `register_admin_menu_item`, ikona `help`).
- Widok `views.handbook` (chroniony `require_admin_access`) czyta `docs/przewodnik-moderatora/*.md` (sort po nazwie), skleja, konwertuje biblioteką `markdown` (rozszerzenia: toc, tables, fenced_code, sane_lists) z auto-spisem treści i renderuje w szablonie panelu.
- Treść (źródło prawdy) żyje w `docs/przewodnik-moderatora/`, NIE w kodzie.

## Jak dodać/rozszerzyć rozdział
Edytuj/utwórz plik `.md` w `docs/przewodnik-moderatora/` (prefiks numeryczny = kolejność). Mikro-struktura wpisu: **Co steruje / Gdzie edytujesz / Wskazówki**. Zmiana jest widoczna od razu (czytane na żywo).

## Zależności
`markdown`, Wagtail admin (hooks, auth).
```

- [ ] **Step 3: Zaktualizuj główny `README.md`** — w sekcji „Dokumentacja projektu" dodaj:
```markdown
  - Przewodnik moderatora (panel Wagtail): `docs/przewodnik-moderatora/` — spec `docs/superpowers/specs/2026-06-11-przewodnik-moderatora-design.md`
```

- [ ] **Step 4: Lint + pełne testy (DoD)**
```
& C:\Users\tmrow\.local\bin\uv.exe run ruff check .
& C:\Users\tmrow\.local\bin\uv.exe run black --check .
& C:\Users\tmrow\.local\bin\uv.exe run python manage.py check
& C:\Users\tmrow\.local\bin\uv.exe run pytest --create-db -q
```
Expected: ruff „All checks passed!" (jeśli isort w nowych plikach → `ruff check --fix .`); black clean (jeśli nie → `black .` i dodaj do commita); check clean; wszystkie testy PASSED (poprzednie 36 + 4 nowe = ~40).

- [ ] **Step 5: Commit**
```
git add docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md apps/guide/README.md README.md
git add -A
git commit -m "docs(guide): DoD o przewodnik + README apps/guide + lint" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (autor planu)

**1. Pokrycie specu:**
- Mechanizm (app/hook/widok/szablon/zależność/menu) → Task 1 ✅
- Renderowanie Markdown z `docs/` + auto-TOC → Task 1 (widok) ✅
- Rozdziały Faza 0+1 (wprowadzenie/home/filary/strony/ustawienia) → Task 1 (home) + Task 2 (reszta) ✅
- Granularność per sekcja (Co steruje/Gdzie edytujesz/Wskazówki) → treść rozdziałów ✅
- Pozycja menu głównego, ikona help → Task 1 hook ✅
- DoD „rośnie per faza" → Task 3 (sek. 2.2) ✅
- Testy (login redirect / render dla admina + TOC / menu zarejestrowane / wszystkie rozdziały) → Task 1 + Task 2 ✅

**2. Skan placeholderów:** brak TBD/TODO; cały kod i cała treść Markdown podane wprost.

**3. Spójność nazw:** `guide_handbook` (URL name) używany w hooku, widoku menu i testach; `views.handbook` spójne; `content_html` przekazywane z widoku i użyte w szablonie; katalog `docs/przewodnik-moderatora/` spójny w widoku, treści i README; nagłówki rozdziałów w testach (`Wprowadzenie`, `Strona główna`, `Filary`, `Strony prawne i Kontakt`, `Ustawienia serwisu`) zgodne z H1 plików `.md`.

**Punkt uwagi przy wykonaniu:** ikona `help` — jeśli nie istnieje w zestawie ikon tej wersji Wagtaila, użyj `doc-full` lub `info-circle` (sprawdź `/admin/styleguide/`). Test menu nie zależy od ikony.
