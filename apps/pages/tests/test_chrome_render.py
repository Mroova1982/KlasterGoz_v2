import pytest
from django.test import Client
from wagtail.models import Site

from apps.pages.models import LegalPage
from apps.shared.models import AnalyticsSettings, GeneralSettings


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.mark.django_db
def test_chrome_renders_header_footer_with_settings(root_page):
    site = Site.objects.get(is_default_site=True)
    gs = GeneralSettings.for_site(site)
    gs.email = "biuro@klastergoz.pl"
    gs.save()

    page = LegalPage(title="RODO", slug="rodo", body=[])
    root_page.add_child(instance=page)
    page.save_revision().publish()

    resp = Client().get("/rodo/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "site-header" in html
    assert "site-footer" in html
    assert "biuro@klastergoz.pl" in html  # kontakt w stopce z GeneralSettings


@pytest.mark.django_db
def test_cookie_banner_conditional_on_ga_id(root_page):
    page = LegalPage(title="Cookies", slug="cookies", body=[])
    root_page.add_child(instance=page)
    page.save_revision().publish()

    # bez GA4 ID — brak bannera
    resp = Client().get("/cookies/")
    assert "cookieBanner" not in resp.content.decode()

    # z GA4 ID — banner obecny + ID widoczne
    site = Site.objects.get(is_default_site=True)
    a = AnalyticsSettings.for_site(site)
    a.ga4_measurement_id = "G-TEST12345"
    a.save()
    resp2 = Client().get("/cookies/")
    html = resp2.content.decode()
    assert "cookieBanner" in html
    assert "G-TEST12345" in html
