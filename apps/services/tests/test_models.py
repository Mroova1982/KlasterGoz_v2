import pytest
from wagtail.models import Site

from apps.home.models import PillarPage
from apps.services.models import ServicesIndexPage, ServicePage, ServiceBenefit


@pytest.fixture
def klaster(db):
    root = Site.objects.get(is_default_site=True).root_page
    pillar = PillarPage(title="Klaster", slug="klaster")
    root.add_child(instance=pillar)
    pillar.save_revision().publish()
    return pillar


@pytest.mark.django_db
def test_index_lists_service_children(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    idx.save_revision().publish()
    svc = ServicePage(title="KNR Green", slug="knr-green", tag="Certyfikacja", hero_lead="...")
    idx.add_child(instance=svc)
    svc.save_revision().publish()
    children = list(idx.get_children().live().specific())
    assert svc.pk in [c.pk for c in children]


@pytest.mark.django_db
def test_service_hero_box_item_list(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    svc = ServicePage(title="KNR Green", slug="knr-green", hero_box_items="Tekstylna\nMetalurgiczna\n\nPapiernicza")
    idx.add_child(instance=svc)
    assert svc.hero_box_item_list() == ["Tekstylna", "Metalurgiczna", "Papiernicza"]


@pytest.mark.django_db
def test_service_benefits_relation(klaster):
    idx = ServicesIndexPage(title="Usługi", slug="uslugi")
    klaster.add_child(instance=idx)
    svc = ServicePage(title="KNR Green", slug="knr-green")
    idx.add_child(instance=svc)
    svc.benefits.add(ServiceBenefit(tag="B2B", title="Duzi klienci", description="..."))
    svc.save_revision().publish()
    assert svc.benefits.count() == 1
