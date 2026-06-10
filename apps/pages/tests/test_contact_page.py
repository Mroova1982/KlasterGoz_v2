import pytest
from django.test import Client
from wagtail.contrib.forms.models import FormSubmission
from wagtail.models import Site

from apps.pages.models import ContactFormField, ContactPage


@pytest.fixture
def root_page(db):
    return Site.objects.get(is_default_site=True).root_page


@pytest.fixture
def contact_page(root_page):
    page = ContactPage(
        title="Kontakt",
        slug="kontakt",
        to_address="biuro@klastergoz.pl",
        from_address="noreply@klastergoz.pl",
        subject="Nowe zgłoszenie kontaktowe",
        intro="<p>Napisz do nas.</p>",
    )
    root_page.add_child(instance=page)
    page.save_revision().publish()
    # Save each field individually so AbstractFormField.save() populates clean_name
    # (committing children via the parental cluster bypasses that override).
    ContactFormField.objects.create(
        page=page, label="Imię i nazwisko", field_type="singleline", required=True, sort_order=0
    )
    ContactFormField.objects.create(
        page=page, label="E-mail", field_type="email", required=True, sort_order=1
    )
    ContactFormField.objects.create(
        page=page, label="Wiadomość", field_type="multiline", required=True, sort_order=2
    )
    return page


@pytest.mark.django_db
def test_contact_page_renders_form_and_cards(contact_page):
    resp = Client().get("/kontakt/")
    assert resp.status_code == 200
    html = resp.content.decode()
    assert "Formularz kontaktowy" in html
    assert "Imię i nazwisko" in html


@pytest.mark.django_db
def test_contact_form_submission_creates_record(contact_page):
    resp = Client().post(
        "/kontakt/",
        {
            "imie_i_nazwisko": "Anna Kowalska",
            "e_mail": "anna@firma.pl",
            "wiadomosc": "Dzień dobry, mam pytanie.",
        },
    )
    assert resp.status_code == 200
    assert FormSubmission.objects.filter(page=contact_page).count() == 1
    assert "Dziękujemy" in resp.content.decode()


@pytest.mark.django_db
def test_honeypot_blocks_spam(contact_page):
    Client().post(
        "/kontakt/",
        {
            "imie_i_nazwisko": "Bot",
            "e_mail": "bot@spam.ru",
            "wiadomosc": "spam",
            "hp_website": "http://spam.example",
        },
    )
    assert FormSubmission.objects.filter(page=contact_page).count() == 0
