import pytest
from wagtail.models import Site

from apps.shared.blocks import LinkBlock, MenuItemBlock
from apps.shared.models import FooterSettings, NavigationSettings, PortalsSettings


def test_linkblock_url_fallback_hash():
    block = LinkBlock()
    value = block.to_python({"label": "X", "page": None, "url": "", "description": ""})
    assert block.get_url(value) == "#"


def test_linkblock_uses_external_url_when_no_page():
    block = LinkBlock()
    value = block.to_python(
        {"label": "RODO", "page": None, "url": "https://example.org/rodo", "description": ""}
    )
    assert block.get_url(value) == "https://example.org/rodo"


def test_menuitemblock_url_fallback_hash():
    block = MenuItemBlock()
    value = block.to_python({"label": "Klaster", "page": None, "url": "", "nav_key": "", "columns": []})
    assert block.get_url(value) == "#"


@pytest.mark.django_db
def test_navigation_accepts_menu_item():
    site = Site.objects.get(is_default_site=True)
    nav = NavigationSettings.for_site(site)
    nav.primary_menu = [
        {"type": "item", "value": {"label": "Kontakt", "page": None, "url": "/kontakt/", "nav_key": "kontakt", "columns": []}}
    ]
    nav.save()
    reloaded = NavigationSettings.for_site(site)
    assert reloaded.primary_menu[0].value["label"] == "Kontakt"


@pytest.mark.django_db
def test_portals_accepts_entry():
    site = Site.objects.get(is_default_site=True)
    p = PortalsSettings.for_site(site)
    p.portals = [
        {"type": "portal", "value": {"label": "Strefa członka", "description": "Portal", "url": "https://portal.example/"}}
    ]
    p.save()
    assert PortalsSettings.for_site(site).portals[0].value["url"] == "https://portal.example/"


@pytest.mark.django_db
def test_footer_defaults():
    site = Site.objects.get(is_default_site=True)
    f = FooterSettings.for_site(site)
    assert f.newsletter_heading == "Newsletter"
