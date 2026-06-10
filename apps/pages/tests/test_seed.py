import pytest
from django.core.management import call_command
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
    assert nav.primary_menu[0].value["page"].url == "/kontakt/"
    legal = FooterSettings.for_site(site).legal_links
    assert legal[0].value["page"].url == "/rodo/"


@pytest.mark.django_db
def test_seed_is_idempotent():
    call_command("seed_initial_content")
    call_command("seed_initial_content")
    assert Page.objects.filter(slug="rodo").count() == 1
    assert Page.objects.filter(slug="kontakt").count() == 1
