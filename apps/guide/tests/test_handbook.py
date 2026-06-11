import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_handbook_requires_login():
    resp = Client().get(reverse("guide_handbook"))
    assert resp.status_code in (302, 403)
    if resp.status_code == 302:
        assert "/admin/login" in resp.url


@pytest.mark.django_db
def test_handbook_renders_for_admin():
    User = get_user_model()
    User.objects.create_superuser("mod", "mod@example.com", "pass12345")
    c = Client()
    c.force_login(User.objects.get(username="mod"))
    resp = c.get(reverse("guide_handbook"))
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Strona główna" in html
    assert 'class="toc"' in html


@pytest.mark.django_db
def test_menu_item_registered():
    from wagtail import hooks

    items = [fn() for fn in hooks.get_hooks("register_admin_menu_item")]
    labels = [getattr(i, "label", "") for i in items]
    assert "Przewodnik moderatora" in labels


@pytest.mark.django_db
def test_handbook_includes_all_chapters():
    User = get_user_model()
    User.objects.create_superuser("mod2", "mod2@example.com", "pass12345")
    c = Client()
    c.force_login(User.objects.get(username="mod2"))
    html = c.get(reverse("guide_handbook")).content.decode()
    for heading in [
        "Wprowadzenie",
        "Strona główna",
        "Filary",
        "Strony prawne i Kontakt",
        "Ustawienia serwisu",
    ]:
        assert heading in html, f"brak rozdziału: {heading}"
