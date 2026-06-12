import pytest
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.cluster.models import MembersIndexPage, TeamPage, PartnersPage, Member, TeamMember, Partner


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    p = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=p)
    p.save_revision().publish()
    return p


@pytest.mark.django_db
def test_members_index_filters_by_sector(klaster, rf):
    idx = MembersIndexPage(title="Członkowie", slug="czlonkowie")
    klaster.add_child(instance=idx)
    Member.objects.create(name="RecFirma", slug="rec", sector="recykling")
    Member.objects.create(name="ProdFirma", slug="prod", sector="produkcja")
    req = rf.get("/klaster/czlonkowie/?sektor=recykling")
    ctx = idx.get_context(req)
    names = [m.name for m in ctx["members"]]
    assert names == ["RecFirma"]
    assert ctx["active_sector"] == "recykling"


@pytest.mark.django_db
def test_team_groups(klaster, rf):
    page = TeamPage(title="Zespół", slug="zespol")
    klaster.add_child(instance=page)
    TeamMember.objects.create(name="Jan", group="zarzad")
    ctx = page.get_context(rf.get("/"))
    labels = [g["label"] for g in ctx["groups"]]
    assert "Zarząd i koordynator" in labels


@pytest.mark.django_db
def test_partners_groups(klaster, rf):
    page = PartnersPage(title="Partnerzy", slug="partnerzy")
    klaster.add_child(instance=page)
    Partner.objects.create(name="PARP", type="instytucja")
    ctx = page.get_context(rf.get("/"))
    labels = [g["label"] for g in ctx["groups"]]
    assert "Instytucja publiczna" in labels


@pytest.mark.django_db
def test_about_page_body_streamfield(klaster):
    from apps.cluster.models import AboutClusterPage
    page = AboutClusterPage(title="O klastrze", slug="o-klastrze", hero_lead="...")
    page.body = [
        {"type": "text_section", "value": {"eyebrow": "Misja", "heading": "Współpraca", "body": "<p>Tekst.</p>", "background": "none"}},
        {"type": "steps", "value": {"heading": "Droga", "steps": [{"number": "01", "title": "Deklaracja", "text": "..."}], "background": "dark"}},
    ]
    klaster.add_child(instance=page)
    page.save_revision().publish()
    reloaded = AboutClusterPage.objects.get(slug="o-klastrze")
    assert reloaded.body[0].block_type == "text_section"
    assert reloaded.body[1].value["steps"][0]["title"] == "Deklaracja"
