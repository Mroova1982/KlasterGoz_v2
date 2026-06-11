import pytest
from django.test import Client
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.services.models import (
    ServiceBenefit,
    ServiceFAQ,
    ServicePage,
    ServicesIndexPage,
    ServiceStep,
)


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    pillar = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=pillar)
    pillar.save_revision().publish()
    return pillar


@pytest.mark.django_db
def test_service_page_renders(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    svc = ServicePage(
        title="KNR Green",
        slug="knr-green",
        tag="Certyfikacja",
        hero_lead="Standard certyfikacji recyklingu.",
        hero_box_heading="7 branż",
        hero_box_items="Tekstylna\nMetalurgiczna",
        benefits_heading="Dla kogo",
        process_heading="Proces",
        cta_heading="Gotowy?",
    )
    idx.add_child(instance=svc)
    svc.benefits.add(ServiceBenefit(tag="B2B", title="Duzi klienci wymagają recyklatu"))
    svc.steps.add(ServiceStep(number="01", title="Zgłoszenie"))
    svc.faqs.add(ServiceFAQ(question="Ile trwa proces?", answer="<p>8–12 tygodni.</p>"))
    svc.save_revision().publish()

    resp = Client().get("/klaster/uslugi/knr-green/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "KNR Green" in html
    assert "Certyfikacja" in html
    assert "7 branż" in html
    assert "Duzi klienci wymagają recyklatu" in html
    assert "Zgłoszenie" in html
    assert "Ile trwa proces?" in html
    assert "site-header" in html


@pytest.mark.django_db
def test_services_index_lists_services(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi", intro="<p>Katalog.</p>")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    for slug, title in [("knr-green", "KNR Green"), ("pro-goz", "PRO GOZ")]:
        s = ServicePage(title=title, slug=slug, tag="X", hero_lead="...")
        idx.add_child(instance=s)
        s.save_revision().publish()

    resp = Client().get("/klaster/uslugi/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "KNR Green" in html
    assert "PRO GOZ" in html
    assert "/klaster/uslugi/knr-green/" in html
