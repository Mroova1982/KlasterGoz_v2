"""Idempotentny seed startowej zawartości portalu (strony prawne, kontakt, Settings).

Uruchamiany ręcznie po wdrożeniu świeżej bazy: `./manage.py seed_initial_content`.
NIE jest migracją danych — celowo, żeby nie zaśmiecać bazy testowej.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page, Site

from apps.home.models import (
    HeroSlide,
    HomeHeroSlide,
    HomePage,
    HomePillar,
    Pillar,
    PillarPage,
    Statistic,
)
from apps.pages.models import (
    ContactFormField,
    ContactPage,
    ContactPageContactCard,
    LegalPage,
)
from apps.services.models import ServicePage, ServicesIndexPage
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
            # --- HomePage jako root Site ---
            home = HomePage.objects.first()
            if home is None:
                tree_root = Page.get_first_root_node()  # niewidoczny korzeń drzewa (depth=1)
                old_root = site.root_page
                # zwolnij slug 'home' zajęty przez domyślną stronę powitalną Wagtaila
                if old_root.slug == "home":
                    old_root.slug = "old-welcome-page"
                    old_root.save()
                home = HomePage(
                    title="Klaster GOZ",
                    slug="home",
                    pillars_heading="Trzy filary cyrkularnej transformacji.",
                )
                tree_root.add_child(instance=home)
                home.save_revision().publish()
                old_root.refresh_from_db()
                if old_root.pk != home.pk:
                    # przenieś istniejące strony (prawne/kontakt z Fazy 0) pod HomePage
                    for child in list(old_root.get_children()):
                        child.move(home, pos="last-child")
                    site.root_page = home
                    site.save()
                    # usuń starą domyślną stronę powitalną Wagtaila
                    old_root.refresh_from_db()
                    if old_root.specific_class is not HomePage:
                        old_root.delete()
            # od tego miejsca `root` to HomePage (parent dla stron prawnych/kontaktu/filarów)
            root = HomePage.objects.first()
            home = root

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
                            {
                                "type": "paragraph",
                                "value": "<p>Treść do uzupełnienia w panelu administracyjnym.</p>",
                            }
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
                    [
                        ("Imię i nazwisko", "singleline"),
                        ("E-mail", "email"),
                        ("Wiadomość", "multiline"),
                    ]
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

            # --- Strony filarów ---
            pillars_data = [
                ("klaster", "Klaster ogólnokrajowy", "Filar 01 · Klaster ogólnokrajowy"),
                ("edukacja", "Edukacja — Akademia GOZ", "Filar 02 · Akademia GOZ"),
                ("doradztwo", "Doradztwo", "Filar 03 · Doradztwo"),
            ]
            for slug, title, eyebrow in pillars_data:
                if not Page.objects.filter(slug=slug).exists():
                    pp = PillarPage(
                        title=title,
                        slug=slug,
                        eyebrow=eyebrow,
                        hero_lead="Treść do uzupełnienia w panelu administracyjnym.",
                        cta_heading="Porozmawiajmy o Twojej transformacji.",
                        cta_button_label="Skontaktuj się",
                        cta_button_url="/kontakt/",
                    )
                    home.add_child(instance=pp)
                    pp.save_revision().publish()
                    self.stdout.write(f"Utworzono /{slug}/")

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
                self.stdout.write("Utworzono /klaster/uslugi/ + 5 ServicePage")

            # --- Treść HomePage (raz) ---
            if not home.hero_slides.exists():
                slide = HeroSlide.objects.create(
                    eyebrow="Krajowy Klaster Kluczowy",
                    headline="<p>Cyrkularna gospodarka — <em>nasza wspólna</em> przewaga.</p>",
                    lead="Łączymy firmy, naukę i instytucje wokół zamykania obiegów surowcowych.",
                    primary_cta_label="Poznaj klaster",
                    primary_cta_url="/klaster/",
                    secondary_cta_label="Bezpłatna konsultacja",
                    secondary_cta_url="/kontakt/",
                )
                home.hero_slides.add(HomeHeroSlide(slide=slide))
            if not home.home_pillars.exists():
                klaster = Page.objects.filter(slug="klaster").first()
                edukacja = Page.objects.filter(slug="edukacja").first()
                doradztwo = Page.objects.filter(slug="doradztwo").first()
                p1 = Pillar.objects.create(
                    number="01 / FILAR",
                    title="Klaster ogólnokrajowy",
                    lead="Platforma kooperacji 150+ firm.",
                    bullets="Członkostwo i networking\nWspólne projekty B+R\nReprezentacja branży",
                    link=klaster,
                    cta_label="Dołącz do klastra",
                )
                p2 = Pillar.objects.create(
                    number="02 / FILAR",
                    title="Edukacja — Akademia GOZ",
                    lead="Szkolenia i programy rozwojowe.",
                    bullets="ATB / ATB-VIP / ATT\nSzkolenia GOZ, ESG, AI\nHarmonogram otwarty",
                    link=edukacja,
                    cta_label="Zobacz harmonogram",
                    is_dark=True,
                )
                p3 = Pillar.objects.create(
                    number="03 / FILAR",
                    title="Doradztwo",
                    lead="Indywidualne wsparcie firm.",
                    bullets="PRO GOZ\nGO GREEN\nKNR Green",
                    link=doradztwo,
                    cta_label="Umów konsultację",
                )
                home.home_pillars.add(
                    HomePillar(pillar=p1), HomePillar(pillar=p2), HomePillar(pillar=p3)
                )
            home.save_revision().publish()
            if not Statistic.objects.filter(group="home_strip").exists():
                for i, (v, lbl) in enumerate(
                    [
                        ("150+", "firm i instytucji członkowskich"),
                        ("12", "lat działalności klastra"),
                        ("19", "krajowych klastrów kluczowych"),
                        ("240 mln zł", "pozyskanego finansowania"),
                    ]
                ):
                    Statistic.objects.create(value=v, label=lbl, group="home_strip", sort_order=i)

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

            nav = NavigationSettings.for_site(site)
            if not nav.primary_menu:
                klaster = Page.objects.filter(slug="klaster").first()
                edukacja = Page.objects.filter(slug="edukacja").first()
                doradztwo = Page.objects.filter(slug="doradztwo").first()
                kontakt = Page.objects.filter(slug="kontakt").first()

                def menu_item(label, pg, key):
                    return {
                        "type": "item",
                        "value": {
                            "label": label,
                            "page": pg.id if pg else None,
                            "url": "",
                            "nav_key": key,
                            "columns": [],
                        },
                    }

                nav.primary_menu = [
                    menu_item("Klaster", klaster, "klaster"),
                    menu_item("Edukacja", edukacja, "edukacja"),
                    menu_item("Doradztwo", doradztwo, "doradztwo"),
                    menu_item("Kontakt", kontakt, "kontakt"),
                ]
                nav.save()

            footer = FooterSettings.for_site(site)
            if not footer.legal_links:
                links = []
                for slug, label in [
                    ("rodo", "RODO"),
                    ("regulamin", "Regulamin"),
                    ("cookies", "Cookies"),
                ]:
                    pg = Page.objects.filter(slug=slug).first()
                    links.append(
                        {
                            "type": "link",
                            "value": {
                                "label": label,
                                "page": pg.id if pg else None,
                                "url": "",
                                "description": "",
                            },
                        }
                    )
                footer.legal_links = links
                footer.save()

            PortalsSettings.for_site(site)  # zapewnij istnienie rekordu

        self.stdout.write(self.style.SUCCESS("Seed zakończony."))
