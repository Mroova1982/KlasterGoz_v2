import pytest
from wagtail.models import Site

from apps.home.models import HomePage, HeroSlide, HomeHeroSlide, Statistic


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.mark.django_db
def test_homepage_about_bullets(root_page):
    hp = HomePage(title="Klaster GOZ", slug="home-test", about_bullets="A\nB\nC")
    root_page.add_child(instance=hp)
    assert hp.about_bullet_list() == ["A", "B", "C"]


@pytest.mark.django_db
def test_homepage_hero_slides_relation(root_page):
    hp = HomePage(title="Klaster GOZ", slug="home-test2")
    root_page.add_child(instance=hp)
    slide = HeroSlide.objects.create(eyebrow="X", headline="<p>H</p>")
    hp.hero_slides.add(HomeHeroSlide(slide=slide))
    hp.save_revision().publish()
    assert hp.hero_slides.count() == 1
    assert hp.hero_slides.first().slide.eyebrow == "X"


@pytest.mark.django_db
def test_homepage_max_count_one():
    assert HomePage.max_count == 1
