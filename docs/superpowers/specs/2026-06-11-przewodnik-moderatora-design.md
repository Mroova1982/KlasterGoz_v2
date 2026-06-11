# Przewodnik moderatora — design / spec

**Data:** 2026-06-11
**Autor:** Tomasz (z udziałem Claude)
**Status:** zaakceptowany po brainstormingu — podstawa do planu implementacji
**Powiązane:** master spec `2026-05-15-klastergoz-portal-design.md` (sekcja 2.2 — Definition of Done)

---

## 1. Cel i kontekst

Portal jest zarządzany przez **moderatora/redaktora nietechnicznego**. Panel Wagtail rośnie z każdą fazą (Faza 0: Settings + strony prawne + kontakt; Faza 1: HomePage z 10 sekcjami + 3 PillarPage + snippety; kolejne fazy 2–6). Moderator musi wiedzieć **która sekcja / panel / ustawienie za co odpowiada** i jak edytować treść. Potrzebujemy dokumentacji, która:

- jest **przyjazna nietechnicznemu moderatorowi**,
- **rośnie wraz z funkcjami** (faza po fazie),
- jest **wersjonowana z kodem** (źródło prawdy w repo),
- jest **dostępna w narzędziu**, którego moderator używa (panel Wagtail) — bez wychodzenia na GitHub.

Developerska dokumentacja (README per app) zostaje bez zmian — to jej uzupełnienie dla użytkownika końcowego.

## 2. Decyzje (z brainstormingu)

| Decyzja | Wybór |
|---|---|
| Forma główna | Osobny „Przewodnik moderatora" (czytany obok panelu) |
| Źródło prawdy | Markdown w `docs/przewodnik-moderatora/` (wersjonowany, rośnie per faza) |
| Dostęp | Renderowany w panelu Wagtail (opcja A: własny widok admina) |
| Granularność | Per sekcja / panel (mapuje 1:1 na `MultiFieldPanel`) |
| Umiejscowienie w menu | **Menu główne** (top-level), pozycja „Przewodnik moderatora" z ikoną pomocy |
| Mikro-struktura wpisu | **Co steruje / Gdzie edytujesz / Wskazówki** |
| Dodatki user-friendly | Klikalny spis treści (kotwice) na górze, prosty język |

## 3. Architektura / komponenty

Nowy app **`apps/guide`** (czysta granica — funkcja „przewodnik moderatora"):

- `apps/guide/wagtail_hooks.py`
  - `register_admin_urls` → ścieżka `guide/` → widok,
  - `register_admin_menu_item` → pozycja „Przewodnik moderatora" w menu głównym (ikona `help`).
- `apps/guide/views.py` — `handbook(request)`:
  - czyta wszystkie `docs/przewodnik-moderatora/*.md` (sort po nazwie pliku),
  - konwertuje przez bibliotekę `markdown` z rozszerzeniami `toc`, `tables`, `fenced_code`, `sane_lists`,
  - skleja w jeden dokument, generuje spis treści (rozszerzenie `toc`) z kotwicami,
  - renderuje w szablonie panelu.
- `apps/guide/templates/guide/handbook.html` — `{% extends "wagtailadmin/base.html" %}`, wstawia wyrenderowany HTML (`|safe`) + spis treści.
- `apps/guide/apps.py` — `GuideConfig`.

Treść (Markdown) żyje w `docs/`, NIE w kodzie — kod tylko ją renderuje.

**Zależność:** dodać `markdown` (mała, pure-python) do `pyproject.toml`.

**Bezpieczeństwo:** widok za standardową autoryzacją panelu (tylko zalogowani). Markdown pochodzi z repo (zaufane źródło), więc `|safe` na wyrenderowanym HTML jest akceptowalne.

## 4. Struktura treści (Markdown)

```
docs/przewodnik-moderatora/
  00-wprowadzenie.md       # po co przewodnik; podstawy publikacji (draft → publish, podgląd, historia wersji)
  10-strona-glowna.md      # HomePage — sekcje (Faza 1)
  20-filary.md             # PillarPage: Klaster / Edukacja / Doradztwo (Faza 1)
  30-strony-statyczne.md   # RODO / Regulamin / Cookies + Kontakt (Faza 0)
  40-ustawienia.md         # 6 grup Site Settings (Faza 0)
```

Prefiksy numeryczne → kolejność i miejsce na wstawki (kolejne fazy dokładają np. `50-aktualnosci.md`).

**Mikro-struktura każdego wpisu (per sekcja):**

```markdown
## Strona główna → sekcja „Hero"
**Co steruje:** slider na górze strony głównej (slajdy: nagłówek, lead, przyciski).
**Gdzie edytujesz:** Pages → Klaster GOZ → „Slajdy hero" (wybór snippetów Slajd hero).
**Wskazówki:** 1–3 slajdy; pierwszy ładuje się najszybciej.
```

Każdy plik zaczyna się nagłówkiem `# <Obszar>` (H1), sekcje to `##` (H2) — spis treści budowany z nagłówków.

## 5. Mechanizm „rośnie z funkcjami"

Do **Definition of Done każdej fazy** (master spec, sekcja 2.2) dochodzi punkt:

> **Przewodnik moderatora zaktualizowany** — dla każdego nowego typu strony / sekcji / ustawienia dodano lub rozszerzono odpowiedni rozdział w `docs/przewodnik-moderatora/`.

Dzięki temu dokumentacja nie zostaje w tyle — rośnie w tym samym cyklu, w którym powstają funkcje.

## 6. Zakres tej implementacji

**W zakresie (teraz):**
- Mechanizm: `apps/guide` (hook + widok + szablon), zależność `markdown`, pozycja w menu głównym.
- Rozdziały dla istniejących funkcji (Faza 0 + 1): wprowadzenie, strona główna, filary, strony statyczne, ustawienia.
- Aktualizacja DoD w master specu (sekcja 2.2) o punkt „Przewodnik moderatora".
- Testy: widok zwraca 200 dla zalogowanego użytkownika panelu i renderuje znany nagłówek; pozycja menu zarejestrowana; (przekierowanie do logowania dla niezalogowanego).

**Poza zakresem (YAGNI):**
- Kontekstowy `help_text` / `HelpPanel` przy polach (ewentualnie punktowo w przyszłości).
- Wielojęzyczność przewodnika, wyszukiwarka w przewodniku, edycja przewodnika z panelu.

## 7. Testowanie

- `test_handbook_requires_login` — niezalogowany → przekierowanie do logowania panelu.
- `test_handbook_renders_for_admin` — zalogowany admin → 200 + zawiera znany nagłówek z Markdownu (np. „Strona główna") i wygenerowany spis treści.
- `test_menu_item_registered` — hook rejestruje pozycję „Przewodnik moderatora".

## Powiązane dokumenty
- Master spec: `docs/superpowers/specs/2026-05-15-klastergoz-portal-design.md`
- Plan implementacji: *do utworzenia (writing-plans)*
