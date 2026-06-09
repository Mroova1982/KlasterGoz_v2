import pytest
from wagtail.models import Site

from apps.shared.models import AnalyticsSettings, GeneralSettings, SocialMediaSettings


@pytest.mark.django_db
def test_general_settings_defaults():
    site = Site.objects.get(is_default_site=True)
    gs = GeneralSettings.load(site)
    assert gs.organization_name == "Klaster GOZ"


@pytest.mark.django_db
def test_general_settings_editable():
    site = Site.objects.get(is_default_site=True)
    gs = GeneralSettings.load(site)
    gs.phone = "+48 22 123 45 67"
    gs.email = "biuro@klastergoz.pl"
    gs.save()
    reloaded = GeneralSettings.load(site)
    assert reloaded.phone == "+48 22 123 45 67"
    assert reloaded.email == "biuro@klastergoz.pl"


@pytest.mark.django_db
def test_analytics_default_cookie_text_present():
    site = Site.objects.get(is_default_site=True)
    a = AnalyticsSettings.load(site)
    assert "cookies" in a.cookie_banner_text.lower()


@pytest.mark.django_db
def test_social_settings_blank_by_default():
    site = Site.objects.get(is_default_site=True)
    s = SocialMediaSettings.load(site)
    assert s.linkedin == ""
