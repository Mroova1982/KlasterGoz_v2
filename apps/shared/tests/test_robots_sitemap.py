import pytest
from django.test import Client, override_settings


@pytest.mark.django_db
@override_settings(SEO_ALLOW_INDEXING=True)
def test_robots_allows_indexing_in_prod_mode():
    resp = Client().get("/robots.txt")
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "Disallow: /admin/" in body
    assert "Sitemap:" in body
    assert "Disallow: /\n" not in body


@pytest.mark.django_db
@override_settings(SEO_ALLOW_INDEXING=False)
def test_robots_blocks_all_when_indexing_off():
    resp = Client().get("/robots.txt")
    assert resp.status_code == 200
    assert "Disallow: /" in resp.content.decode()


@pytest.mark.django_db
def test_sitemap_returns_xml():
    resp = Client().get("/sitemap.xml")
    assert resp.status_code == 200
    assert "urlset" in resp.content.decode()
