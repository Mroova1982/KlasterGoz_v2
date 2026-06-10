import pytest
from django.test import Client
from wagtail.models import Site

from apps.pages.models import LegalPage


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.mark.django_db
def test_legal_page_renders_title_and_body(root_page):
    page = LegalPage(
        title="Polityka prywatności i RODO",
        slug="rodo",
        body=[
            {"type": "heading", "value": "1. Administrator danych"},
            {"type": "paragraph", "value": "<p>Administratorem jest Klaster GOZ.</p>"},
        ],
    )
    root_page.add_child(instance=page)
    page.save_revision().publish()

    resp = Client().get("/rodo/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Polityka prywatności i RODO" in html
    assert "1. Administrator danych" in html
    assert "Administratorem jest Klaster GOZ." in html


@pytest.mark.django_db
def test_legal_page_in_sitemap(root_page):
    page = LegalPage(title="Regulamin", slug="regulamin", body=[])
    root_page.add_child(instance=page)
    page.save_revision().publish()

    resp = Client().get("/sitemap.xml")
    assert resp.status_code == 200
    assert "/regulamin/" in resp.content.decode()
