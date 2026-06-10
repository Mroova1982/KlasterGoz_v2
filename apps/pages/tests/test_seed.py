import pytest
from django.core.management import call_command
from django.test import Client
from wagtail.models import Page, Site

from apps.shared.models import FooterSettings, GeneralSettings


@pytest.mark.django_db
def test_seed_creates_pages_and_settings():
    call_command("seed_initial_content")
    for slug in ["rodo", "regulamin", "cookies", "kontakt"]:
        assert Page.objects.filter(slug=slug).exists(), f"brak strony {slug}"
    site = Site.objects.get(is_default_site=True)
    assert GeneralSettings.for_site(site).email == "biuro@klastergoz.pl"
    assert list(FooterSettings.for_site(site).legal_links)  # populated

    from apps.shared.models import NavigationSettings

    nav = NavigationSettings.for_site(site)
    menu_urls = [block.value["page"].url for block in nav.primary_menu]
    assert menu_urls == ["/klaster/", "/edukacja/", "/doradztwo/", "/kontakt/"]
    legal = FooterSettings.for_site(site).legal_links
    assert legal[0].value["page"].url == "/rodo/"


@pytest.mark.django_db
def test_seed_is_idempotent():
    call_command("seed_initial_content")
    call_command("seed_initial_content")
    assert Page.objects.filter(slug="rodo").count() == 1
    assert Page.objects.filter(slug="kontakt").count() == 1


@pytest.mark.django_db
def test_seed_sets_homepage_as_root():
    from apps.home.models import HomePage

    call_command("seed_initial_content")
    site = Site.objects.get(is_default_site=True)
    assert isinstance(site.root_page.specific, HomePage)
    home = site.root_page
    child_slugs = set(home.get_children().values_list("slug", flat=True))
    for slug in ["rodo", "regulamin", "cookies", "kontakt", "klaster", "edukacja", "doradztwo"]:
        assert slug in child_slugs, f"brak {slug} pod HomePage"


@pytest.mark.django_db
def test_seed_homepage_has_content_and_renders():
    call_command("seed_initial_content")
    resp = Client().get("/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "heroSlider" in html
    assert "Klaster ogólnokrajowy" in html
