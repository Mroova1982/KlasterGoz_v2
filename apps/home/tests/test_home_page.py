import pytest
from django.test import Client
from wagtail.models import Site

from apps.home.models import HomePage, HeroSlide, HomeHeroSlide, Statistic, HomePillar, Pillar


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


@pytest.mark.django_db
def test_homepage_renders_at_root(root_page):
    hp = HomePage(title="Klaster GOZ", slug="home-root", pillars_heading="Trzy filary")
    root_page.add_child(instance=hp)
    slide = HeroSlide.objects.create(eyebrow="KLASTERBOX", headline="<p>Najnowsza <em>platforma</em></p>", lead="Lead hero")
    hp.hero_slides.add(HomeHeroSlide(slide=slide))
    pillar = Pillar.objects.create(number="01 / FILAR", title="Klaster ogólnokrajowy", lead="...")
    hp.home_pillars.add(HomePillar(pillar=pillar))
    hp.save_revision().publish()
    Statistic.objects.create(value="150+", label="firm", group="home_strip", sort_order=0)

    site = Site.objects.get(is_default_site=True)
    site.root_page = hp
    site.save()

    resp = Client().get("/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "heroSlider" in html
    assert "KLASTERBOX" in html
    assert "Klaster ogólnokrajowy" in html
    assert "150+" in html
    assert "hero-slider.js" in html
    assert "site-header" in html
