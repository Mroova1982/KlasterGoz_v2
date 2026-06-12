import pytest
from django.test import Client
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.cluster.models import (
    MembersIndexPage, TeamPage, PartnersPage, AboutClusterPage,
    Member, TeamMember, Partner,
)


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    p = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=p)
    p.save_revision().publish()
    return p


@pytest.mark.django_db
def test_members_page_renders_and_filters(klaster):
    idx = MembersIndexPage(title="Członkowie", slug="czlonkowie")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    Member.objects.create(name="RecFirma", slug="rec", sector="recykling")
    Member.objects.create(name="ProdFirma", slug="prod", sector="produkcja")
    html = Client().get("/klaster/czlonkowie/").content.decode()
    assert "RecFirma" in html and "ProdFirma" in html and "site-header" in html
    filtered = Client().get("/klaster/czlonkowie/?sektor=recykling").content.decode()
    assert "RecFirma" in filtered and "ProdFirma" not in filtered


@pytest.mark.django_db
def test_team_page_renders_groups(klaster):
    page = TeamPage(title="Zespół", slug="zespol")
    klaster.add_child(instance=page)
    page.save_revision().publish()
    TeamMember.objects.create(name="Jan Kowalski", role="Prezes", group="zarzad")
    html = Client().get("/klaster/zespol/").content.decode()
    assert "Jan Kowalski" in html and "Zarząd i koordynator" in html


@pytest.mark.django_db
def test_partners_page_renders_groups(klaster):
    page = PartnersPage(title="Partnerzy", slug="partnerzy")
    klaster.add_child(instance=page)
    page.save_revision().publish()
    Partner.objects.create(name="PARP", type="instytucja")
    html = Client().get("/klaster/partnerzy/").content.decode()
    assert "PARP" in html and "Instytucja publiczna" in html


@pytest.mark.django_db
def test_about_page_renders_blocks(klaster):
    page = AboutClusterPage(title="O klastrze", slug="o-klastrze", hero_lead="Lead")
    page.body = [{"type": "text_section", "value": {"heading": "Misja klastra", "body": "<p>Tekst.</p>", "background": "green", "eyebrow": ""}}]
    klaster.add_child(instance=page)
    page.save_revision().publish()
    html = Client().get("/klaster/o-klastrze/").content.decode()
    assert "Misja klastra" in html and "bg-green" in html and "site-header" in html
