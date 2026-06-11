import pytest

from apps.home.models import HeroSlide, Pillar, Statistic


@pytest.mark.django_db
def test_heroslide_str_uses_eyebrow():
    s = HeroSlide.objects.create(eyebrow="Platforma KLASTERBOX", headline="<p>X</p>")
    assert str(s) == "Platforma KLASTERBOX"


@pytest.mark.django_db
def test_pillar_bullet_list_splits_lines():
    p = Pillar.objects.create(number="01 / FILAR", title="Klaster", lead="...", bullets="A\nB\n\nC")
    assert p.bullet_list() == ["A", "B", "C"]


@pytest.mark.django_db
def test_statistic_str_and_ordering():
    Statistic.objects.create(value="12", label="lat", group="home_strip", sort_order=1)
    Statistic.objects.create(value="150+", label="firm", group="home_strip", sort_order=0)
    first = Statistic.objects.filter(group="home_strip").first()
    assert first.value == "150+"
    assert str(first) == "150+ — firm"
