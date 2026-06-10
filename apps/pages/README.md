# apps.pages

Statyczne typy stron portalu.

## Co robi
- `LegalPage` — dokument prawny (RODO / Regulamin / Cookies). Jeden typ, wiele instancji. Body = StreamField (nagłówek / akapit / obraz).
- `ContactPage` — strona kontaktu na Wagtail Form Builder:
  - edytowalne pola formularza (`form_fields`), zgłoszenia zapisywane w DB + e-mail do biura,
  - honeypot anti-spam (`HoneypotFormBuilder` w `forms.py`; ukryte pole `hp_website` — wypełnione = zgłoszenie cicho odrzucone),
  - karty kontaktowe (`contact_cards`, Orderable), wstęp, tekst podziękowania, embed mapy.

## Seed startowy
`./manage.py seed_initial_content` — idempotentnie tworzy strony /rodo, /regulamin, /cookies, /kontakt (z polami i kartą kontaktową) oraz wypełnia podstawowe Settings (dane kontaktowe, menu, linki prawne w stopce). Uruchom raz po wdrożeniu świeżej bazy. To management command, nie migracja danych — nie zaśmieca bazy testowej.

## Jak używać
Strony tworzy/edytuje redaktor w `/admin/`. Treść w pełni edytowalna (zero hardkodu w szablonach).

## Zależności
`apps.shared` (BasePage/SeoMixin), `wagtail.contrib.forms`.

## Uwaga (sekwencja faz)
W Fazie 0 strony są dziećmi root page domyślnego Site. Faza 1 wprowadzi `HomePage` jako root i przeniesie te strony pod nią (URL-e najwyższego poziomu pozostają: /rodo/, /kontakt/).
