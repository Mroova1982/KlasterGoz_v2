import pytest
from django.test import Client
from wagtail.models import Site

from apps.home.models import PillarPage, PillarBenefit


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.mark.django_db
def test_pillar_page_renders(root_page):
    page = PillarPage(
        title="Klaster ogólnokrajowy",
        slug="klaster",
        eyebrow="Filar 01 · Klaster",
        hero_lead="150+ firm i instytucji.",
        benefits_heading="Konkretne korzyści członkostwa.",
        feature_bullets="Przedsiębiorstwa\nUczelnie\nSamorząd",
    )
    root_page.add_child(instance=page)
    page.benefits.add(PillarBenefit(tag="Networking", title="150+ partnerów", description="..."))
    page.save_revision().publish()

    resp = Client().get("/klaster/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Klaster ogólnokrajowy" in html
    assert "Filar 01 · Klaster" in html
    assert "150+ partnerów" in html
    assert "site-header" in html


@pytest.mark.django_db
def test_feature_bullet_list(root_page):
    page = PillarPage(title="X", slug="x", feature_bullets="A\n\nB")
    root_page.add_child(instance=page)
    assert page.feature_bullet_list() == ["A", "B"]
