# apps.home

Strona główna portalu i landingi filarów.

## Co robi
- Snippety: `HeroSlide` (slajdy hero), `Pillar` (kafelki filarów z linkiem do strony), `Statistic` (statystyki; grupy home_strip / home_section / about_klastra).
- `HomePage` — root portalu. 10 sekcji z `mockup/index.html` jako pola + Orderable children (hero_slides, home_pillars, consult_steps, offerings, member_logos, news_teasers). Statystyki pobierane z `Statistic` po grupie w `get_context`. `max_count=1`, `parent_page_types=["wagtailcore.Page"]`.
- `PillarPage` — wspólny landing filaru (Klaster/Edukacja/Doradztwo): hero, korzyści, blok „jak działamy", kroki procesu, CTA, auto-listing żywych dzieci (puste do Faz 2–4).
- `static/js/hero-slider.js` — slider hero (vanilla, aktywny tylko gdy `#heroSlider` istnieje).

## Tymczasowe (do zastąpienia w późniejszych fazach)
- Kafelki usług (`offerings`) → auto-lista ServicePage w Fazie 2.
- Logosy członków (`member_logos`) → Member snippets w Fazie 2.
- Teasery aktualności (`news_teasers`) → ArticlePage w Fazie 4.
- Sekcja konsultacji renderuje CTA do /kontakt/; pełny formularz konsultacji = Faza 2.

## Re-rooting
`manage.py seed_initial_content` ustawia HomePage jako `Site.root_page`, przenosi pod nią strony prawne/kontakt z Fazy 0, tworzy 3 PillarPage i ustawia menu główne (filary + Kontakt). Idempotentne.

## Zależności
`apps.shared` (BasePage/SeoMixin), Wagtail snippets/images.
