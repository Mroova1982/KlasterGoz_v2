# Projekt portalu klastergoz.pl — design / spec

**Data utworzenia:** 2026-05-15
**Ostatnia aktualizacja:** 2026-06-10 (review sekcja po sekcji — podział na fazy, OVH, GA4, płaskie role, migracja z bazy)
**Autor:** Tomasz (z udziałem Claude)
**Status:** zaakceptowany po review — podstawa do planów implementacji per faza
**Mockup:** `C:\Programer\Projekty\KlasterGoz_v2\mockup\`
**Brief designerski:** `~/Downloads/klastergoz-brief-designerski.md`

---

## Spis treści

1. [Cele i ograniczenia](#1-cele-i-ograniczenia)
2. [Zakres projektu](#2-zakres-projektu)
   - [2.1 Podział na fazy](#21-podzia%C5%82-na-fazy)
   - [2.2 Definition of Done per faza](#22-definition-of-done-per-faza)
3. [Stack technologiczny](#3-stack-technologiczny)
4. [Architektura informacji i drzewo stron](#4-architektura-informacji-i-drzewo-stron)
5. [Modele treści (page types, snippety, bloki, settings)](#5-modele-tre%C5%9Bci)
6. [Integracje (formularze, newsletter, search, multilingual, email)](#6-integracje)
7. [SEO](#7-seo)
8. [Migracja danych i 301 redirects](#8-migracja-danych-i-301-redirects)
9. [Deployment, hosting, monitoring](#9-deployment-hosting-monitoring)
10. [Role edytorów i workflow](#10-role-edytor%C3%B3w-i-workflow)
11. [Koszty operacyjne (TCO)](#11-koszty-operacyjne-tco)
12. [Otwarte pytania](#12-otwarte-pytania)

---

## 1. Cele i ograniczenia

### Cele biznesowe (z briefu)

- Pełna oferta klastra w jednym miejscu — koniec rozproszenia między portalem a subdomenami.
- Pozyskiwanie nowych członków klastra.
- Pozyskiwanie klientów na usługi doradcze i szkoleniowe.
- Budowa autorytetu eksperckiego w obszarze GOZ.
- Wsparcie SEO dla zapytań: "audyt GOZ", "dofinansowanie GOZ", "szkolenia GOZ", "klaster gospodarki obiegu zamkniętego" + powiązane.

### Twarde ograniczenia projektowe

- **Edytor nietechniczny** — biuro klastra ma w pełni zarządzać treścią bez programisty.
- **Premium look** zgodny z briefem (kierunek "circular industrial premium") — bez "framework feel".
- **Server-side rendering** z klasycznym przeładowaniem strony (bez SPA).
- **Maksymalnie szablonowane strony** — strukturalne pola page-types, StreamField tylko gdzie konieczne (artykuły, case studies).
- **Stack Python** — preferowany Wagtail.
- **Pełna migracja** ze starych źródeł (klastergoz.pl + akademia.klastergoz.pl).
- **PL primary, EN per-page opcjonalnie** (nie 1:1, EN okrojone).
- **SEO krytyczne** — migracja nie może zniszczyć obecnych pozycji.
- **Łatwość zarządzania kodem + dobra dokumentacja** (wymaganie niefunkcjonalne, obowiązuje we wszystkich fazach) — kod modularny (małe, jednocelowe aplikacje i pliki, zgodnie z podziałem `apps/*`), docstringi na modelach / blokach / management commands, README per aplikacja opisujące „co robi / jak używać / od czego zależy", komentarze tam gdzie logika nieoczywista. Każda faza zostawia dokumentację na tyle, że kolejny dev wchodzi bez archeologii.

### Co NIE jest w zakresie

- 4 portale loginowe widoczne w mockupie (strefa członka, LMS Akademii, Giełda B2B, platforma badań) — to istniejące/zewnętrzne aplikacje, na portalu są tylko **linki** w dropdownie "Strefa logowania".
- Aplikacja CRM / sprzedażowa — wyłącznie ewentualne wpięcie webhooków ze zgłoszeń.
- Aplikacja mailingowa / marketing automation — używamy zewnętrznego (Brevo).

---

## 2. Zakres projektu

Portal marketingowy `klastergoz.pl` — content-driven witryna z pełnym CMS-em (Wagtail), zarządzana przez biuro klastra bez udziału dewelopera po wdrożeniu. Obejmuje:

- ~30 podstron z mockupu (home + 3 filary + ich podstrony + listy + szczegółowe)
- 5 podstron usług klastra pod `/klaster/uslugi/*`
- 3 podstrony doradztwa pod `/doradztwo/*`
- Akademia GOZ — strony informacyjne (programy ATB / ATB-VIP / ATT, trenerzy, harmonogram, 9 kategorii szkoleń, single szkolenia)
- Aktualności (artykuły) + Wydarzenia + Projekty (case studies)
- Strony statyczne (RODO, regulamin, cookies, kontakt, forum)
- Formularze konwertujące (konsultacja, członkostwo, kontakt, newsletter)
- Multilingual PL/EN
- Pełen panel administracyjny z workflow publikacji
- Pełna migracja treści z istniejących źródeł
- 301 redirects + sitemap + structured data + SEO infra

### 2.1 Podział na fazy

Projekt **nie jest budowany naraz**. Dzielimy go na 7 samodzielnie wdrażalnych faz. Każda faza dostaje własny cykl **spec → plan → implementacja**, kończy się działającym, wdrażalnym przyrostem i może trafić na produkcję. Fundament idzie pierwszy, bo wszystko od niego zależy; potem wygląd (home + filary); potem trzy filary z treścią po kolei; na końcu twardy SEO i wersja EN. Import treści idzie **per filar w jego fazie**, a nie hurtem na końcu.

| Faza | Zakres | Efekt (wdrażalny przyrost) |
|---|---|---|
| **0 — Fundament** | Design system z mockupu (base.html, header/footer, `styles.css`), renditions obrazów, Site Settings (General / Navigation / Footer / Portals / Social), nawigacja (dropdowny + footer 5 kolumn), podstawy SEO (wagtail-seo, sitemap, robots, meta), strony statyczne (LegalPage ×3, ContactPage z formularzem kontaktowym), cookie banner (GA4) | Wdrażalny szkielet z działającą nawigacją i kontaktem |
| **1 — Home + filary** | HomePage 1:1 z mockupu + 3 PillarPage (Klaster / Edukacja / Doradztwo) jako landingi z auto-listingiem podstron. Snippety: HeroSlide, Pillar, Statistic | Pełna strona główna i wejścia w trzy filary |
| **2 — Filar Klaster** | ServicesIndex + 5 ServicePage, AboutCluster, Członkowie (+Member), Zespół (+TeamMember), Partnerzy (+Partner), Showroom (+ShowroomItem), Giełda B2B (+B2BService). Formularze: konsultacja + członkostwo. **Import treści klastra z bazy** | Filar 01 sprzedaje usługi i pozyskuje członków |
| **3 — Filar Edukacja / Akademia** | AkademiaPillar, ATB / ATB-VIP / ATT, kategorie szkoleń (+TrainingCategory), TrainingPage, Trenerzy (+Trainer), Harmonogram, formularz „zapytaj o ofertę". **Migracja mieszana z Google Sites** (scrape szkieletu + ręczny cleanup) | Cała Akademia na portalu |
| **4 — Doradztwo + treści dynamiczne** | DoradztwoPillar + 3 ConsultingAreaPage, Aktualności (ArticlePage + StreamField), Wydarzenia, Projekty (case studies), Forum, Newsletter (Brevo). **Import artykułów / wydarzeń / projektów z bazy** | Content marketing + lead-gen na pełnych obrotach |
| **5 — Twardy SEO** | 301 redirects (priorytet wg rankingu z GSC), pełne structured data, search (PostgreSQL `tsvector` PL), monitoring GSC przez 4 tygodnie po launchu | Stare treści i pozycje SEO przeniesione bez strat |
| **6 — Multilingual EN + finishing** | wagtail-localize, EN per-page (ręcznie), opcjonalnie DeepL, performance / Core Web Vitals finishing | Wersja EN i ostatnie szlify |

Kolejność filarów: **Klaster → Edukacja → Doradztwo**. Produkcyjne wdrożenie możliwe już po Fazie 1; każda kolejna faza dokłada wartość.

### 2.2 Definition of Done per faza

Fazę uznajemy za zamkniętą dopiero, gdy spełnia **wszystkie** poniższe kryteria:

1. **Pełne zarządzanie treścią w panelu Wagtail** — redaktor nietechniczny może z poziomu `/admin` edytować *całą* treść stron należących do fazy: żadnego tekstu / obrazu / CTA / listy zahardkodowanego w szablonach. Każdy element to pole modelu, snippet albo Setting. Weryfikacja: da się to przeklikać w adminie i zobaczyć efekt na froncie.
2. **Przechodzące testy** — `pytest` zielony (modele, renderowanie kluczowych stron, formularze / importery danej fazy).
3. **Commit do Git** — czysty, opisowy commit zamykający fazę (przy większych fazach również commity pośrednie per logiczny krok).
4. **Dokumentacja** — zgodnie z wymaganiem niefunkcjonalnym z sekcji 1 (docstringi, README aplikacji, komentarze przy nieoczywistej logice).

---

## 3. Stack technologiczny

### Wybór i uzasadnienie

**Wagtail 6.x na Django 5.x, Python 3.12+**

Dlaczego Wagtail dla tego briefu:
- Page tree model = naturalne mapowanie IA z mockupu na URL-e.
- StreamField + StructValue + structured page types = "jak najwięcej szablonowanych stron" (cel projektowy).
- Dojrzały admin UI w PL, edytor nietechniczny pracuje na formularzach.
- Server-side rendering = klasyczne przeładowanie strony + idealne SEO + pełna kontrola nad HTML/CSS (premium look zgodny z mockupem).
- wagtail-localize obsługuje wymóg PL + EN per-page.
- Built-in search, sitemap, redirects, workflow, scheduled publish, image renditions.

Odrzucone alternatywy:
- **WordPress** — ryzyko "framework feel" z briefu, słabsza kontrola nad premium look, pluginy zawodne.
- **Headless (Sanity/Strapi + Astro/Next)** — wymaga dwóch serwisów do utrzymania, nadmiarowe dla content-only site bez SPA.
- **No-code (Webflow/Framer)** — vendor lock-in, rosnące koszty miesięczne, ograniczenia dla list z filtrowaniem.

### Składniki techniczne

| Warstwa | Wybór |
|---|---|
| Backend / CMS | Wagtail 6.x / Django 5.x / Python 3.12+ |
| Database | PostgreSQL 16 |
| Cache + queue broker | Redis 7 |
| Worker (async tasks) | Django-Q2 (lub Celery jeśli wolumen zarezerwowany) |
| Frontend rendering | Django templates (server-side) |
| CSS | `assets/styles.css` z mockupu jako baza, vanilla (bez Tailwind) |
| JavaScript | Vanilla, minimalny (hero slider, akordeon, burger, search submit) |
| Search backend | `wagtail.search.backends.database` (PostgreSQL `tsvector` + `pl_PL` config) |
| Forms | mix: Wagtail Form Builder + custom modele dla CTA |
| Newsletter | Brevo API (transactional + marketing) |
| Email backend | django-anymail → Brevo |
| Anti-spam | honeypot + reCAPTCHA v3 |
| Multilingual | wagtail-localize |
| SEO meta | wagtail-seo |
| Media storage | lokalny wolumen (start), OVH Object Storage (S3-compat) gdy wolumen wzrośnie |
| Reverse proxy | Caddy 2 (auto-HTTPS Let's Encrypt) |
| App server | Gunicorn (3 workers) |
| Containerization | Docker + Docker Compose |
| Hosting | **OVH VPS** (prod; staging jako kontener na tym samym VPS) |
| CI/CD | GitHub Actions |
| Monitoring (errors) | Sentry (free tier) |
| Monitoring (uptime) | Uptime-Kuma (self-hosted) |
| Analytics | **Google Analytics (GA4)** — wymaga obowiązkowego cookie consent banner (RODO) |
| Backup | **mechanizm OVH** (automated backup / snapshot); rekomendowany dodatkowo okresowy `pg_dump` (logiczny, granularny) |

---

## 4. Architektura informacji i drzewo stron

```
/                                    HomePage
├── /klaster                         KlasterPillarPage          (filar 01)
│   ├── /klaster/o-klastrze          AboutClusterPage
│   ├── /klaster/czlonkowie          MembersIndexPage
│   ├── /klaster/zespol              TeamPage
│   ├── /klaster/showroom            ShowroomPage  +  ShowroomItemPage
│   ├── /klaster/gielda-uslug        B2BExchangePage  +  B2BServicePage
│   ├── /klaster/partnerzy           PartnersPage
│   └── /klaster/uslugi              ServicesIndexPage
│       ├── /klaster/uslugi/knr-green   ServicePage  (Certyfikacja)
│       ├── /klaster/uslugi/pro-goz     ServicePage  (Model GOZ)
│       ├── /klaster/uslugi/pro-inno    ServicePage  (Innowacje)
│       ├── /klaster/uslugi/go-green    ServicePage  (ESG · CSRD)
│       └── /klaster/uslugi/pro-eko     ServicePage  (Ekoprojektowanie)
│
├── /edukacja                        AkademiaPillarPage         (filar 02)
│   ├── /edukacja/atb                ATBProgramPage
│   ├── /edukacja/atb-vip            ATBVipPage
│   ├── /edukacja/att                ATTPage
│   ├── /edukacja/trenerzy           TrainersIndexPage
│   ├── /edukacja/harmonogram        TrainingScheduleIndexPage
│   ├── /edukacja/kategoria/<slug>   TrainingCategoryPage       (9 kategorii)
│   └── /edukacja/szkolenie/<slug>   TrainingPage               (single)
│
├── /doradztwo                       DoradztwoPillarPage        (filar 03)
│   ├── /doradztwo/dofinansowania    ConsultingAreaPage
│   ├── /doradztwo/consulting        ConsultingAreaPage
│   └── /doradztwo/strategiczne      ConsultingAreaPage
│
├── /aktualnosci                     NewsIndexPage  +  ArticlePage
├── /wydarzenia                      EventsIndexPage  +  EventPage
├── /projekty                        ProjectsIndexPage  +  ProjectPage
├── /forum                           ForumPage                  (info o Polish Circular Forum)
├── /kontakt                         ContactPage
└── /rodo  /regulamin  /cookies      LegalPage                  (jeden typ, 3 instancje)
```

### Mapowanie URL z mockupu → nowe URL-e (301)

| Mockup | Docelowe URL |
|---|---|
| `index.html` | `/` |
| `klaster.html` | `/klaster` |
| `o-klastrze.html` | `/klaster/o-klastrze` |
| `czlonkowie.html` | `/klaster/czlonkowie` |
| `zespol.html` | `/klaster/zespol` |
| `showroom.html` | `/klaster/showroom` |
| `gielda-uslug.html` | `/klaster/gielda-uslug` |
| `partnerzy.html` | `/klaster/partnerzy` |
| `oferta.html` | `/klaster/uslugi` |
| `oferta/knr-green.html` | `/klaster/uslugi/knr-green` |
| `oferta/pro-goz.html` | `/klaster/uslugi/pro-goz` |
| `oferta/proinno.html` | `/klaster/uslugi/pro-inno` |
| `oferta/gogreen.html` | `/klaster/uslugi/go-green` |
| `oferta/proeko.html` | `/klaster/uslugi/pro-eko` |
| `edukacja.html` | `/edukacja` |
| `akademia/atb.html` | `/edukacja/atb` |
| `akademia/atb-vip.html` | `/edukacja/atb-vip` |
| `akademia/att.html` | `/edukacja/att` |
| `akademia/trenerzy.html` | `/edukacja/trenerzy` |
| `akademia/harmonogram.html` | `/edukacja/harmonogram` |
| `akademia/kategoria.html?k=<x>` | `/edukacja/kategoria/<x>` |
| `akademia/szkolenie.html` | `/edukacja/szkolenie/<slug>` |
| `doradztwo.html` | `/doradztwo` |
| `aktualnosci.html` | `/aktualnosci` |
| `artykul.html` | `/aktualnosci/<slug>` |
| `wydarzenia.html` | `/wydarzenia` |
| `projekty.html` | `/projekty` |
| `forum.html` | `/forum` |
| `kontakt.html` | `/kontakt` |
| `login.html?p=*` | linki zewnętrzne (4 portale) — pola w `PortalsSettings` |
| `rodo.html` / `regulamin.html` / `cookies.html` | `/rodo` / `/regulamin` / `/cookies` |

### Nawigacja (Header / Footer)

- **Header (main nav)**: Wydarzenia · Klaster · Edukacja · Doradztwo · Projekty · Kontakt — 6 pozycji
- **Klaster dropdown**: O klastrze · Członkowie · Zespół · Showroom · Giełda usług · Partnerzy · **Usługi** (link do `/klaster/uslugi` + opcjonalnie 5 sub-linków do pojedynczych usług)
- **Edukacja mega-dropdown**: kolumna "Akademia GOZ" (ATB-VIP, ATT, Trenerzy, Harmonogram) + kolumna "ATB" (9 kategorii) — jak w mockupie
- **Doradztwo dropdown** (przebudowane): Dofinansowania · Consulting · Strategiczne — 3 pozycje (zamiast 5 z mockupu)
- **Strefa logowania dropdown** (4 portale): Strefa członka · Akademia LMS · Giełda B2B · Platforma badań — wszystkie linki do zewnętrznych URL-i z `PortalsSettings`
- **Footer**: 5 kolumn (Filar 01 / Filar 02 / Filar 03 / O klastrze / Portale + Kontakt) — wszystkie z `FooterSettings`

---

## 5. Modele treści

Filozofia: **structured fields first, StreamField second**. StreamField użyty tylko tam, gdzie redaktor naprawdę potrzebuje wolności kompozycji (artykuły, case studies, długie opisy programów). Reszta = sztywne pola dopasowane 1:1 do sekcji w mockupie.

### 5.1 Page types — strukturalne pola

| Page type | Najważniejsze pola |
|---|---|
| **HomePage** | hero_slides (M2M → HeroSlide) · stats_strip · pillars (M2M → Pillar) · consult_intro · consult_steps[] · stats_secondary · services_intro · members_intro · about_intro / about_bullets · news_intro · cta_strip_heading + lead + buttons |
| **KlasterPillarPage** | hero · intro · korzysci[] (ikona + tytuł + opis) · stats · cta · auto-listing sub-pages |
| **ServicesIndexPage** | hero · intro · auto-listing 5 ServicePage |
| **ServicePage** (5×) | tag · hero (heading + lead + image) · description (short RichText) · proces_etapy[] (numer + tytuł + opis) · korzysci[] · cennik_widelki (RichText opc.) · faq[] · related_projects (M2M → ProjectPage) · cta |
| **DoradztwoPillarPage** | hero · intro · auto-listing 3 ConsultingAreaPage · cta |
| **ConsultingAreaPage** (3×) | dziedziczy z `AbstractServiceLikePage` (DRY z ServicePage) |
| **AkademiaPillarPage** | hero · intro · programy (M2M → program pages) · trenerzy_teaser · harmonogram_teaser · cta |
| **ATBProgramPage / ATBVipPage / ATTPage** | hero · program_modules[] · trenerzy · target · cennik · enrollment_url |
| **TrainingPage** | category (FK → TrainingCategory) · trainer (FK → Trainer) · duration · format (open/closed/online) · program[] · price · enrollment_url · upcoming_dates[] |
| **TrainingCategoryPage** | category info + auto-listing TrainingPages w kategorii |
| **TrainersIndexPage** | hero · grid wszystkich Trainer snippets |
| **TrainingScheduleIndexPage** | filtrowalna tabela najbliższych terminów (z TrainingPage.upcoming_dates) |
| **ArticlePage** | category (FK) · published_at · reading_time · cover · lead · body (StreamField) · related_articles · tags |
| **EventPage** | type (FK) · start_at · end_at · location · format (online/onsite/hybrid) · cover · lead · agenda (StreamField) · register_url |
| **ProjectPage** | sector_tag · client (FK → Member opc.) · period · cover · lead · challenge · solution · results · body (StreamField) · gallery |
| **NewsIndexPage / EventsIndexPage / ProjectsIndexPage** | filtrowanie + paginacja + intro |
| **MembersIndexPage** | hero · intro · filtrowalna lista Member snippets (sektor, alfabetycznie) |
| **TeamPage** | hero · sekcje (zarząd / biuro / rada / koordynator) z TeamMember snippets |
| **PartnersPage** | hero · grid Partner snippets pogrupowanych (uczelnie / instytucje / klastry UE / źródła finansowania) |
| **ShowroomPage** | hero · intro · grid ShowroomItem snippets |
| **B2BExchangePage** | hero · intro · grid B2BService snippets |
| **ForumPage** | hero · intro · historia · agenda · register_url · galeria |
| **ContactPage** | hero · dane kontaktowe (z GeneralSettings) · mapa · formularz (Form Builder) |
| **LegalPage** | tytuł · body (StreamField) — jeden typ dla RODO / Regulamin / Cookies |

### 5.2 Snippety (reużywalne, edytowane raz, używane wszędzie)

- **HeroSlide** — image · eyebrow · headline (z `<em>` markup) · lead · primary_cta_label/url · secondary_cta_label/url · is_active · sort_order
- **Pillar** — number · title · lead · bullets[] · cta_label · link (FK → Page) · color · icon
- **Statistic** — value (string) · label · group (home_strip / home_section / about_klastra) · sort_order
- **Member** — name · logo · slug · sector · description · website · is_featured · joined_at
- **Trainer** — name · photo · bio · expertise_tags · linkedin · slug · is_featured
- **TeamMember** — name · photo · role · bio · email · linkedin · group (zarząd / biuro / rada / koordynator)
- **Partner** — name · logo · link · type (uczelnia / instytucja / klaster_ue / źródło_finansowania) · sort_order
- **TrainingCategory** — slug · name · description · color · icon · sort_order
- **ArticleCategory / EventType / ProjectCategory** — slug · name · color
- **Testimonial** — quote · author_name · author_role · author_company · photo
- **FAQItem** — question · answer (RichText) · category
- **PortalLink** — label · url · icon · description (dla dropdown'a "Strefa logowania")
- **ShowroomItem** — name · slug · member (FK → Member) · cover · description · category · gallery
- **B2BService** — title · slug · member (FK → Member) · category · description · contact

### 5.3 Bloki StreamField (skromna paleta)

Używane głównie w artykułach, case studies i długich opisach programów:

- `RichTextBlock`
- `ImageBlock` (image + caption + alt)
- `TwoColumnBlock` (text + image, możliwa zamiana stron)
- `QuoteBlock`
- `VideoEmbedBlock` (YouTube / Vimeo)
- `AccordionBlock` (FAQ)
- `StatsBlock` (2-4 statystyki inline)
- `CTABlock`
- `DownloadBlock` (PDF link z metadata)
- `TableBlock` (Wagtail built-in)
- `GalleryBlock`

Świadomie BRAK bloków typu "HeroBlock" / "PillarsBlock" — te są sztywno na strukturalnych polach Page'a dla spójności renderowania.

### 5.4 Site Settings (globalne, edytowalne)

- **GeneralSettings** — telefon · email · adres · NIP · krótki opis klastra (footer)
- **NavigationSettings** — pozycje menu głównego + dropdowny
- **FooterSettings** — kolumny linków
- **PortalsSettings** — 4 portale logowania (M2M → PortalLink)
- **SocialMediaSettings** — LinkedIn / FB / YT URL-e
- **FundingPartnersSettings** — logosy źródeł finansowania (UE / NCBR / ministerstwa)
- **FormsSettings** — odbiorca notyfikacji · auto-reply template · reCAPTCHA keys
- **NewsletterSettings** — Brevo API key (encrypted) · list_id · double_opt_in_template
- **AnalyticsSettings** — GA4 measurement ID · cookie_banner_text · toggle zgody
- **HomeHighlightsSettings** — które aktualności / wydarzenia / projekty featurować na home (override domyślnego "3 najnowsze")
- **SEOSettings** — default OG image · organization JSON-LD fields · GSC verification meta

### 5.5 Co to daje redaktorowi

Edytor wchodzi w `/admin/pages/home/edit/` i widzi:
- listę slajdów hero (drag & drop reorder)
- listę statystyk w pasku (drag & drop reorder)
- 3 filary (FK chooser do snippetów)
- pola tekstowe dla każdego nagłówka sekcji
- chooser do logosów członków
- które aktualności wyróżnić

Żaden HTML, żadne CSS-y, żadne kombinowanie z kolejnością bloków na home — wszystko trzymane przez schemę.

---

## 6. Integracje

### 6.1 Formularze

**Tryb A — Wagtail Form Builder** dla `/kontakt` (klasyczny formularz z polami konfigurowanymi przez redaktora).

**Tryb B — dedykowane modele** dla high-conversion CTA (stabilna struktura wszędzie identyczna):
- `ConsultationRequest` — "Bezpłatna konsultacja"
- `MembershipRequest` — "Dołącz do klastra"
- `AcademyInquiry` — "Zapytaj o ofertę" (Akademia)

Wspólna mechanika dla obu trybów:
- Zapis w DB (audit, eksport CSV w admin'ie)
- Email notification do biura (z `FormsSettings.notification_recipients`)
- Auto-reply do klienta (template w `FormsSettings`)
- Webhook do CRM opcjonalnie (generic POST z JSON-em; włączane w settings)
- Anti-spam: honeypot (zawsze) + reCAPTCHA v3 (włączane w settings, threshold 0.5)
- RODO consent (`consent_text_snapshot` + `consent_timestamp` zapisywane w submission)
- Throttling: max 5 zgłoszeń/IP/godz (django-ratelimit)
- Status flow: `new → reviewed → contacted → closed` (admin może oznaczać)

### 6.2 Newsletter — Brevo

- Formularze w stopce (na każdej stronie) + opcjonalna dedykowana strona zapisu
- Integracja z Brevo API: po submit → POST do `/contacts` z `listIds: [main_list]`, double opt-in template
- **Lokalny backup model `NewsletterSignup`**: wszystkie próby zapisu lądują tu PIERWSZY, potem worker (Django-Q) wysyła do Brevo z exponential backoff (1m / 5m / 30m / 2h / 24h). Po 5 nieudanych próbach → Sentry alert.
- Unsubscribe link z Brevo (zarządza po stronie ich)
- Per-language listy (`list_id_en` gotowe w settings na przyszłość)
- RODO: snapshot consent text identyczny jak w innych formularzach

### 6.3 Email transactional — Brevo + django-anymail

| Typ emaila | Trigger |
|---|---|
| Form notification | nowe zgłoszenie konsultacji/członkostwa/kontaktu |
| Auto-reply | potwierdzenie odbioru zgłoszenia |
| Newsletter double opt-in | Brevo template |
| Moderation notification | strona oczekuje na zatwierdzenie (Wagtail built-in) |
| Password reset / admin invitation | Django built-in |
| Failure alerts | błąd workflow (np. scheduled publish padł) |

**Wybór: Brevo (ten sam co newsletter) + django-anymail abstrakcja.** Jeden provider, jedna konfiguracja, jeden klucz API. Skrzynka odbiorcza klienta zostaje na Gmail Workspace (klient _odbiera_ ręcznie) — aplikacyjne wysyłki idą przez Brevo (klient _nadaje_ programowo). Te dwa flow nie kolidują.

**DNS (deliverability)**:
- SPF: `v=spf1 include:spf.brevo.com -all`
- DKIM: klucz z Brevo
- DMARC: `v=DMARC1; p=quarantine; rua=mailto:dmarc@klastergoz.pl; pct=100`
- Domena nadawcza: `noreply@klastergoz.pl` (verify w Brevo), reply-to: `biuro@klastergoz.pl`

**Szablony emaili**:
- Django templates `templates/emails/<name>.{html,txt}` (HTML + plain-text fallback)
- Inline CSS via `premailer-py`
- Branding spójny ze stroną (header z logo, kolory marki, RODO footer)
- PL/EN per locale
- Pola edytowalne w `FormsSettings` (subject + body templates z placeholderami) — redaktor edytuje bez deweloperia

**Audit i niezawodność**:
- Model `EmailLog` — kto/komu/co/kiedy/status (`queued / sent / bounced / failed`) — wymagane dla GDPR i debug
- Brevo webhooks → endpoint `/webhooks/brevo/` aktualizuje `EmailLog.status` (delivered / bounce / spam-complaint / opened)
- Retry queue: exponential backoff (5m / 30m / 2h / 12h), po 4 próbach → Sentry alert
- Rate limit wysyłki: max 100/min (broker queue)

**Tryb dev / staging**:
- Dev: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
- Staging: real Brevo z whitelistą domen odbiorców (`ALLOWED_EMAIL_DOMAINS`)
- Opcjonalnie Mailpit (lokalny SMTP dev server) do testowania szablonów

### 6.4 Search

- **Wagtail search backend**: `wagtail.search.backends.database` na PostgreSQL z `pl_PL` text configuration (polski stemming)
- **Globalna belka szukania** w header (już jest w mockupie) → `/szukaj?q=...`
- **Indeksowane typy**: wszystkie Pages + Trainer + Member
- **Wyniki pogrupowane** wg typu treści (Aktualności / Szkolenia / Usługi / Doradztwo / Strony), 3 wyniki + "więcej w tej kategorii →"
- **Filtry**: typ treści · data range · język
- **Search promotions** (Wagtail built-in) — redaktor przypina strony do query
- **Analytics zapytań** — admin widzi top wyszukiwań
- **Brak hits → propozycje**: "Może chodziło Ci o..." + linki do top kategorii

### 6.5 Multilingual — wagtail-localize

- Lokale: `pl` (default, bez prefix), `en` (prefix `/en/`)
- URL: `/o-klastrze/` (PL), `/en/about-the-cluster/` (EN — slugi mogą się różnić)
- **Strategia tłumaczenia**: per-page decyzja redaktora. Niektóre strony (home, /klaster/o-klastrze, /doradztwo) — pełne EN. Reszta (artykuły, większość szkoleń) — tylko PL.
- **Switch w headerze** ma 3 stany:
  - Aktualna strona ma EN translation → klik → EN strona
  - Brak EN translation → klik → redirect do `/en/` home + toast info
  - Aktualnie EN, brak PL → analogicznie (rzadkie)
- **Workflow**: edytor pisze PL → "Translate to English" → wagtail-localize klonuje stronę jako EN draft → tłumacz uzupełnia → publikuje
- **Translation engine** (opcjonalnie): DeepL API jako pre-translation (płatne ~20 EUR/mc dla małego volume), redaktor potem cleanup
- **SEO**: poprawne `<link rel="alternate" hreflang="pl|en|x-default">` automatycznie

---

## 7. SEO

### 7.1 Technical SEO

| Element | Implementacja |
|---|---|
| Meta title + description | `wagtail-seo` per-page (`seo_title`, `meta_description`, `og_image`); fallback do `title` + intro |
| Open Graph + Twitter Cards | Auto-generowane z page fields, override-owalne |
| Canonical URL | Auto z drzewa Wagtail; per-page override |
| Sitemap.xml | `wagtail.contrib.sitemaps` z `lastmod`, `changefreq`, `priority` |
| robots.txt | Statyczny przez Caddy; staging ma `Disallow: /` |
| hreflang | Auto przez wagtail-localize dla PL/EN par |
| 301 redirects | `wagtail.contrib.redirects` (sekcja 8) |
| JSON-LD structured data | Per page type (patrz 7.2) |
| HTML `lang` attribute | Auto z Wagtail locale |

### 7.2 Schema.org structured data

| Page type | Schema |
|---|---|
| HomePage | `Organization` + `WebSite` (z `potentialAction` SearchAction) |
| AboutClusterPage | `Organization` rozszerzone + `BreadcrumbList` |
| ArticlePage | `NewsArticle` / `Article` (author, publisher, datePublished, image) |
| EventPage | `Event` (location, startDate, endDate, eventStatus, eventAttendanceMode) |
| ServicePage / ConsultingAreaPage | `Service` (provider, areaServed, serviceType) |
| TrainingPage | `Course` (provider, hasCourseInstance dla terminów) |
| Trainer (na TrainersIndexPage) | `Person` (jobTitle, worksFor, knowsAbout) |
| ProjectPage | `CreativeWork` (creator, funder) |
| FAQ blocks | `FAQPage` |
| Wszystkie strony | `BreadcrumbList` |

### 7.3 Performance (Core Web Vitals)

Cele dla każdej strony:
- LCP < 2.5s
- CLS < 0.1
- INP < 200ms
- TTFB < 600ms

Techniki:
- Server-side rendering (Django templates) = brak JS rendering blocking
- Wagtail Image renditions: auto-generowane (mobile / tablet / desktop) + WebP (JPEG fallback)
- `<picture>` z `srcset` + `loading="lazy"` poniżej fold'a
- **Hero slider — krytyczne**: pierwszy slajd `loading="eager" fetchpriority="high"`, reszta `lazy`. Wszystkie 3 slajdy renderowane w HTML (nie JS) — crawler widzi treść.
- Critical CSS inlined (header + hero), reszta `styles.css` async
- Font loading: `font-display: swap` + preconnect do fonts.googleapis.com (Sora)
- Page cache w Redis (5-15 min, invalidate przy publish)
- Wagtail cache fragments (sekcje "top 3 aktualności" cached 1h)
- Caddy gzip + brotli
- HTTP/2 + HTTP/3 (Caddy default)
- No render-blocking JS (vanilla, na końcu body)

### 7.4 SEO panel w admin'ie

Każda Page dostaje tab SEO z:
- **Live SERP preview** (`seo_title` + URL + `meta_description` jak w Google)
- **Walidacja w czasie pisania**:
  - `seo_title` > 60 znaków → warning
  - `meta_description` > 160 znaków → warning
  - pusta `meta_description` przy publish → warning
  - duplicate `seo_title` → warning
- **Auto-suggest**: jeśli puste, system proponuje `seo_title = title`, `meta_description = first 155 chars of intro`
- **Focus keyword** (opcjonalne, *post-MVP*) — sprawdza obecność w title/H1/URL/meta_description, score Yoast-like
- **Internal linking suggestion** (opcjonalne, *post-MVP*) — przy edycji ArticlePage propozycje powiązanych stron z tagów/kategorii

> **Zakres MVP panelu SEO:** SERP preview + walidacja długości + auto-suggest meta (tanie, duża wartość) wchodzą od razu. Focus-keyword-score i internal-linking-suggestions są świadomie odłożone na później — nie blokują żadnej fazy.

### 7.5 Targetowane keywordy → landing pages

| Keyword | Landing page |
|---|---|
| audyt GOZ | `/klaster/uslugi/pro-goz` |
| dofinansowanie GOZ | `/doradztwo/dofinansowania` |
| szkolenia GOZ | `/edukacja` + `/edukacja/atb` |
| klaster gospodarki obiegu zamkniętego | `/klaster/o-klastrze` + home |
| certyfikacja recyklingu | `/klaster/uslugi/knr-green` |
| ESG raportowanie / CSRD | `/klaster/uslugi/go-green` |
| ekoprojektowanie | `/klaster/uslugi/pro-eko` |

Każda landing dostaje świadomie skonstruowany `<h1>`, `seo_title`, `meta_description` z target keyword (naturalnie, bez stuffing).

### 7.6 Migracja a SEO (krytyczne)

- 301 redirects 1:1 dla URL-i z rankingiem (top pages by impressions z GSC) — sekcja 8
- Sitemap.xml zaktualizowany + submit do GSC w dniu launch'u
- Stara sitemap zostaje przez 2-3 mc (Caddy może serwować obie ścieżki)
- Monitoring (pierwsze 4 tygodnie po launch'u) — codzienna kontrola GSC Coverage + Search Performance
- Akademia subdomain merge: DNS dla `akademia.klastergoz.pl` zachowany, Caddy robi 301 na `klastergoz.pl/edukacja/...` per path
- Importery (sekcja 8) kopiują istniejące `<title>` i `<meta description>` ze starej strony

### 7.7 Monitoring

- Google Search Console — verified, sitemap submitted
- Bing Webmaster Tools — 5 min konfiguracji
- GA4 — śledzenie SEO traffic
- Sentry — alerty na 404 z high referrer
- Custom Wagtail report: top 10 stron bez `meta_description` / `seo_title`

---

## 8. Migracja danych i 301 redirects

### Źródła migracji (dwa, różne strategie)

- **Źródło 1 — `klastergoz.pl`: stary Wagtail / Django / PostgreSQL.** Mamy **backup bazy ORAZ kod źródłowy** starego portalu (definicje modeli + StreamField). To migracja Wagtail→Wagtail — czytamy strukturalnie ze starego schematu, nie scrapujemy HTML. Mapowanie stary→nowy page type jest jednoznaczne, bo widać definicje starych modeli. Zachowane metadane SEO (`<title>`, `meta_description`), daty publikacji, media.
- **Źródło 2 — Akademia (`akademia.klastergoz.pl`): Google Sites, brak bazy.** Nie ma eksportu DB. Strategia **mieszana**: importer pobiera i parsuje szkielet / listy z Google Site, a redaktor czyści i uzupełnia treść ręcznie w nowym adminie (modele szkoleń / trenerów są nowe i sztywne).

### Etap A — Discovery / inwentaryzacja (przed kodem importerów)

- Analiza schematu starej bazy + kodu modeli (Źródło 1) → mapa „stary page type / tabela → nowy model".
- Inwentaryzacja stron Akademii z Google Site (Źródło 2) → lista szkoleń / kategorii / trenerów do scrape + ręcznego uzupełnienia.
- Eksport top URL-i z **Google Search Console** (dostęp potwierdzony) → **priorytetyzacja 301** (URL-e z rankingiem dostają redirecty w pierwszej kolejności) + baseline do monitoringu pozycji po launchu.
- Wynik: spreadsheet „źródłowy URL → typ treści → docelowa strona/snippet → priorytet 301 → status".

> **Uwaga o kolejności:** importery treści uruchamiamy **per filar w jego fazie** (członkowie/partnerzy/zespół w Fazie 2, szkolenia/trenerzy w Fazie 3, artykuły/wydarzenia/projekty w Fazie 4), a nie hurtem. Faza 5 obejmuje już tylko twardą warstwę SEO (301, structured data, search, monitoring).
>
> **Zależność — media:** pliki graficzne / zdjęcia ze starych źródeł zostaną dostarczone przez właściciela projektu. `import_media` i finalna publikacja stron z obrazami są zablokowane do czasu ich dostarczenia. Nie blokuje to startu — treść tekstowa migruje wcześniej, media dokłada idempotentny re-run importera.

### Etap B — Importery (Django management commands)

Każdy importer: standalone command (`./manage.py import_<source>`), idempotentny (re-run nie duplikuje), z flagami `--dry-run` i `--limit=N`.

| Command | Źródło | Cel |
|---|---|---|
| `import_members` | lista firm z klastergoz.pl | Member snippets |
| `import_team` | zespół z klastergoz.pl | TeamMember snippets |
| `import_partners` | partnerzy + logosy | Partner snippets |
| `import_articles` | aktualności z klastergoz.pl | ArticlePage |
| `import_events` | wydarzenia | EventPage |
| `import_projects` | projekty | ProjectPage |
| `import_trainings` | szkolenia z Akademii (Google Sites — scrape + ręczny cleanup) | TrainingPage + TrainingCategory |
| `import_trainers` | trenerzy z Akademii (Google Sites — scrape + ręczny cleanup) | Trainer snippets |
| `import_media` | obrazki / PDF-y | Wagtail Image + Document |
| `import_redirects` | mapping old → new URLs | `wagtail.contrib.redirects` |

### Etap C — 301 redirects

- **`wagtail.contrib.redirects`** dla per-page mappings (zarządzane w admin'ie)
- **Caddy/Nginx config** dla wzorców masowych:
  - `klastergoz.pl/portal/*` → `klastergoz.pl/`
  - `akademia.klastergoz.pl/szkolenie/<slug>` → `klastergoz.pl/edukacja/szkolenie/<slug>`
- Test po deployu: zestaw URL-i probek z GSC → `curl -I` musi zwrócić 301 + poprawny Location

### Etap D — Manual cleanup (redaktor)

- Importowane strony lądują jako `draft`
- Redaktor przegląda, poprawia formatowanie (HTML → StreamField nie zawsze idealny)
- Publikuje partiami w controlled tempie (żeby śledzić wpływ na ruch)

---

## 9. Deployment, hosting, monitoring

### Środowiska

- **Production**: `klastergoz.pl` (OVH VPS)
- **Staging**: `staging.klastergoz.pl` — **kontener na tym samym VPS** co prod (osobny compose service + subdomena), bez osobnego serwera

### Stack na serwerze (Docker Compose)

```
caddy        → reverse proxy + auto-HTTPS (Let's Encrypt)
web          → Gunicorn + Wagtail/Django (3 workers)
worker       → Django-Q2 (newsletter retry, emaile, scheduled publish, search indexing)
db           → PostgreSQL 16
redis        → cache + Q broker
backup       → mechanizm OVH (automated backup / snapshot); dodatkowo zalecany cron pg_dump (logiczny) → OVH Object Storage
```

### CI/CD (GitHub Actions)

- `push` → `main` → lint (ruff, black) → testy (pytest) → build Docker image → push do GHCR → SSH deploy do staging
- `tag v*.*.*` → deploy do prod (manual approval w Actions)
- DB migrations w entrypoint hooku (`./manage.py migrate --noinput`)
- Collectstatic + Wagtail update_index w post-deploy hook

### Monitoring

- **Sentry** (free tier 5k events/mc) — błędy Django/JS
- **Uptime-Kuma** (self-hosted) — ping HTTP /healthz, alerty na Slack/email
- **Google Analytics (GA4)** — analytics (wymaga cookie consent banner)
- **Logi**: Docker logs + logrotate; opcjonalnie Loki+Grafana w przyszłości
- **Performance**: Caddy access logs → custom „Slow Pages" report (>1s TTFB)

---

## 10. Role edytorów i workflow

### Grupy uprawnień (model płaski)

Realnie treść publikuje 1-2 zaufane osoby, więc **bez workflow moderacji** — edytorzy publikują od razu.

- **Redaktor** — pełne uprawnienia do treści: edytuje **i publikuje od razu** (strony, snippety). Bez kroku „submit do review".
- **Administrator** — to co Redaktor + Settings, użytkownicy, redirects, zarządzanie redaktorami.

*(Rozdział redaktor/moderator oraz rola „Redaktor Akademii" ograniczona do `/edukacja/*` można dodać później jedną grupą uprawnień, gdyby zespół urósł — nie wymaga to zmian w modelach.)*

### Funkcje publikacji (Wagtail built-in)

Mimo płaskich ról zostawiamy siatkę bezpieczeństwa (to nie komplikuje codziennej pracy):

- **Revision history** per strona — cofnięcie do dowolnej poprzedniej wersji (ratunek po pomyłce)
- **Preview** przed publikacją
- **Scheduled publish** — `go_live_at` / `expire_at` na każdej Page (zaplanowanie publikacji na przyszłość)

### Logi audytowe

- Wagtail `PageLogEntry` rejestruje kto / co / kiedy edytował
- **Revision history** per page — możliwe cofnięcie do dowolnej poprzedniej wersji
- Eksport logów (CSV) dla audytu GDPR

---

## 11. Koszty operacyjne (TCO)

Zakładamy małe-średnie obciążenie (~10-50k unique visitors/mc). **Domena już należy do klastra, OVH jest już używane** — koszty infrastruktury w praktyce już poniesione / marginalne. Poniżej orientacyjne widełki (OVH ma kilka wariantów VPS — doprecyzowane przy deploymencie).

| Pozycja | EUR/rok (orient.) |
|---|---|
| OVH VPS (prod + staging jako kontener na tym samym) | ~70–110 |
| OVH backup (automated) | ~15–25 |
| OVH Object Storage (media overflow, gdy urośnie) | ~10–20 |
| Domena .pl | 0 (już Wasza) |
| Brevo Free (start, do 300 sub. newslettera) | 0 |
| Brevo Starter (gdy lista > 300 sub.) | ~300 |
| Sentry / GA4 / reCAPTCHA / Uptime-Kuma | 0 |
| DeepL API pre-translation (opcjonalnie, później) | ~240 |
| **Razem (start, minimalny)** | **~120–180** |
| **Razem (z paid Brevo)** | **~420–480** |
| **Razem (full z DeepL)** | **~660–720** |

Realny dodatkowy koszt operacyjny sprowadza się do ewentualnego paid Brevo (gdy lista newslettera > 300 subów) i opcjonalnego DeepL. Dla porównania: Webflow CMS Business plan = ~564 USD/rok tylko za hosting + CMS. Wagtail self-hosted = dramatycznie taniej, z większą kontrolą.

---

## 12. Otwarte pytania

Wszystkie pytania rozstrzygnięte w review 2026-06-10:

1. **CRM** — ✅ **ROZSTRZYGNIĘTE: NIE.** Biuro nie używa CRM. Zgłoszenia trafiają do bazy + mail do biura. Webhook pomijamy (architektura zostawia furtkę na później).
2. **Akademia LMS / Strefa członka** — ✅ **ROZSTRZYGNIĘTE: zewnętrzne linki.** LMS istnieje, mamy URL. Strefa członka to przekierowanie do platformy na innym silniku. Oba to wyłącznie linki w `PortalsSettings` — zero pracy poza URL-em.
3. **Showroom / Giełda usług B2B** — ✅ **ROZSTRZYGNIĘTE: proste listy CMS, integration-ready.** Na teraz ShowroomItem / B2BService edytowane przez redaktora, bez logowania członków. **Docelowo integracja ze starą platformą** (tą na innym silniku) — modele projektujemy z miejscem na to (np. pole źródła / `external_id`), ale samą integrację robimy **później**, poza zakresem obecnych faz.
4. **DeepL pre-translation** — ✅ **ROZSTRZYGNIĘTE: później.** EN tłumaczone ręcznie przez redaktora. DeepL można dopiąć w Fazie 6.
5. **Email transactional provider** — ✅ **ROZSTRZYGNIĘTE: Brevo** (sekcja 6.3), abstrakcja przez `django-anymail`.
6. **Dostęp do Google Search Console** — ✅ **ROZSTRZYGNIĘTE: jest.** Użyty do priorytetyzacji 301 (URL-e z rankingiem najpierw) i monitoringu pozycji przez 4 tygodnie po launchu. (Discovery i tak opiera się o starą bazę — sekcja 8.)
7. **Hosting** — ✅ **ROZSTRZYGNIĘTE: OVH VPS** (sekcje 3 i 9).
8. **Analytics** — ✅ **ROZSTRZYGNIĘTE: GA4** + obowiązkowy cookie consent banner (sekcje 3 i 9).

---

## Powiązane dokumenty

- Brief designerski: `~/Downloads/klastergoz-brief-designerski.md`
- Mockup HTML: `C:\Programer\Projekty\KlasterGoz_v2\mockup\`
- Plan implementacji Fazy 0 (Fundament): `docs/superpowers/plans/2026-06-10-faza-0-fundament.md` — **zrealizowany**
- Plan implementacji Fazy 1 (Home + filary): `docs/superpowers/plans/2026-06-10-faza-1-home-filary.md`
- Plany faz 2–6: *do utworzenia, każda faza osobnym cyklem spec → plan → implementacja*
