"""Idempotentny seed startowej zawartości portalu (strony prawne, kontakt, Settings).

Uruchamiany ręcznie po wdrożeniu świeżej bazy: `./manage.py seed_initial_content`.
NIE jest migracją danych — celowo, żeby nie zaśmiecać bazy testowej.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page, Site

from apps.pages.models import (
    ContactFormField,
    ContactPage,
    ContactPageContactCard,
    LegalPage,
)
from apps.shared.models import (
    FooterSettings,
    GeneralSettings,
    NavigationSettings,
    PortalsSettings,
)


class Command(BaseCommand):
    help = "Tworzy startowe strony (RODO/Regulamin/Cookies/Kontakt) i podstawowe Settings. Idempotentne."

    def handle(self, *args, **options):
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stderr.write("Brak domyślnego Site — pomijam seed.")
            return

        with transaction.atomic():
            root = site.root_page

            # --- Strony prawne ---
            legal = {
                "rodo": "Polityka prywatności i RODO",
                "regulamin": "Regulamin",
                "cookies": "Polityka cookies",
            }
            for slug, title in legal.items():
                if not Page.objects.filter(slug=slug).exists():
                    page = LegalPage(
                        title=title,
                        slug=slug,
                        body=[
                            {"type": "paragraph", "value": "<p>Treść do uzupełnienia w panelu administracyjnym.</p>"}
                        ],
                    )
                    root.add_child(instance=page)
                    page.save_revision().publish()
                    self.stdout.write(f"Utworzono /{slug}/")

            # --- Strona kontaktu ---
            if not Page.objects.filter(slug="kontakt").exists():
                contact = ContactPage(
                    title="Kontakt",
                    slug="kontakt",
                    to_address="biuro@klastergoz.pl",
                    from_address="noreply@klastergoz.pl",
                    subject="Nowe zgłoszenie kontaktowe",
                    intro="<p>Pytania ogólne, członkostwo, doradztwo, szkolenia — wybierz kanał.</p>",
                )
                root.add_child(instance=contact)
                contact.save_revision().publish()
                for i, (label, ftype) in enumerate(
                    [("Imię i nazwisko", "singleline"), ("E-mail", "email"), ("Wiadomość", "multiline")]
                ):
                    ContactFormField.objects.create(
                        page=contact, label=label, field_type=ftype, required=True, sort_order=i
                    )
                ContactPageContactCard.objects.create(
                    page=contact,
                    heading="Biuro klastra",
                    body="<p>ul. Przykładowa 12<br>00-001 Warszawa</p>",
                    sort_order=0,
                )
                self.stdout.write("Utworzono /kontakt/")

            # --- Settings ---
            gs = GeneralSettings.for_site(site)
            if not gs.email:
                gs.organization_name = "Klaster Gospodarki Cyrkularnej i Recyklingu"
                gs.phone = "+48 22 123 45 67"
                gs.email = "biuro@klastergoz.pl"
                gs.address = "ul. Przykładowa 12\n00-001 Warszawa"
                gs.footer_description = (
                    "Klaster Gospodarki Cyrkularnej i Recyklingu — od 2012 roku łączymy firmy, "
                    "naukę i instytucje wokół transformacji cyrkularnej polskiego przemysłu."
                )
                gs.save()

            kontakt = Page.objects.filter(slug="kontakt").first()
            nav = NavigationSettings.for_site(site)
            if not nav.primary_menu:
                nav.primary_menu = [
                    {"type": "item", "value": {
                        "label": "Kontakt",
                        "page": kontakt.id if kontakt else None,
                        "url": "",
                        "nav_key": "kontakt",
                        "columns": [],
                    }}
                ]
                nav.save()

            footer = FooterSettings.for_site(site)
            if not footer.legal_links:
                links = []
                for slug, label in [("rodo", "RODO"), ("regulamin", "Regulamin"), ("cookies", "Cookies")]:
                    pg = Page.objects.filter(slug=slug).first()
                    links.append({"type": "link", "value": {
                        "label": label,
                        "page": pg.id if pg else None,
                        "url": "",
                        "description": "",
                    }})
                footer.legal_links = links
                footer.save()

            PortalsSettings.for_site(site)  # zapewnij istnienie rekordu

        self.stdout.write(self.style.SUCCESS("Seed zakończony."))
