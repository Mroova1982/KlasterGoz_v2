# apps.shared

Współdzielone fundamenty portalu.

## Co robi
- `SeoMixin` / `BasePage` — wspólny mixin i bazowa strona dające każdej stronie kontekst SEO (meta title/description z fallbackiem, Open Graph, canonical) na bazie wbudowanych pól Wagtaila (`seo_title`, `search_description`) + `og_image`. Wszystkie typy stron dziedziczą z `BasePage`.
- Site Settings (per-site, edytowalne w `/admin/settings/`):
  - `GeneralSettings` — dane kontaktowe, logo, opis stopki.
  - `SocialMediaSettings` — linki social (LinkedIn/Facebook/YouTube).
  - `AnalyticsSettings` — GA4 measurement ID + treść bannera cookies (RODO).
  - `NavigationSettings` — menu główne (StreamField pozycji z opcjonalnymi kolumnami dropdownu).
  - `FooterSettings` — kolumny linków, linki prawne (dolny pasek), nagłówki kolumn, pola newslettera.
  - `PortalsSettings` — zewnętrzne portale logowania.
- `blocks.py` — bloki StreamField nawigacji/stopki/portali (LinkBlock, MenuColumnBlock, MenuItemBlock, FooterColumnBlock, PortalLinkBlock). Linki wewnętrzne przez chooser strony, zewnętrzne przez URL.
- `views.py` — `robots.txt` zależny od `SEO_ALLOW_INDEXING` (prod indeksuje, staging/dev blokuje).

## Jak używać
- Nowe typy stron: `from apps.shared.models import BasePage` i dziedzicz.
- W szablonach Settings dostępne przez `{{ settings.shared.<Nazwa>.<pole> }}` (context processor `wagtail.contrib.settings`).

## SEO
Podstawy SEO realizowane bez pakietu `wagtail-seo`: własny `SeoMixin` (meta/OG/canonical) + `wagtail.contrib.sitemaps` (sitemap.xml) + widok robots. Rozbudowany panel SEO (SERP preview, walidacja długości) zaplanowany na Fazę 5.

## Zależności
Wagtail (`contrib.settings`, `contrib.sitemaps`, `images`), Django `contrib.sitemaps`.
