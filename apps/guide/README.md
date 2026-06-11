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
