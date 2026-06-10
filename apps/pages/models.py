"""Statyczne typy stron: LegalPage (dokumenty prawne) i ContactPage (formularz)."""

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable

from apps.pages.forms import HoneypotFormBuilder
from apps.shared.models import BasePage, SeoMixin


class LegalPage(BasePage):
    """Dokument prawny (RODO / Regulamin / Cookies). Jeden typ, wiele instancji."""

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title", label="Nagłówek sekcji")),
            ("paragraph", blocks.RichTextBlock(label="Tekst")),
            ("image", ImageChooserBlock(label="Obraz")),
        ],
        blank=True,
        help_text="Treść dokumentu — nagłówki, akapity, obrazy.",
    )

    content_panels = BasePage.content_panels + [FieldPanel("body")]
    promote_panels = BasePage.promote_panels
    template = "pages/legal_page.html"

    class Meta:
        verbose_name = "Strona prawna"
        verbose_name_plural = "Strony prawne"


class ContactFormField(AbstractFormField):
    """Pole formularza kontaktowego (konfigurowalne przez redaktora)."""

    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactPageContactCard(Orderable):
    """Karta z danymi kontaktowymi (biuro, sekretariat, koordynator...)."""

    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="contact_cards")
    heading = models.CharField("Nagłówek", max_length=120)
    body = RichTextField("Treść", features=["bold", "link"])

    panels = [FieldPanel("heading"), FieldPanel("body")]


class ContactPage(SeoMixin, AbstractEmailForm):
    """Strona kontaktu: Form Builder + karty kontaktowe + mapa. Jedna instancja."""

    form_builder = HoneypotFormBuilder

    intro = RichTextField("Wstęp nad formularzem", blank=True, features=["bold", "italic", "link"])
    thank_you_text = RichTextField("Tekst podziękowania", blank=True, features=["bold", "link"])
    map_embed = models.TextField(
        "Mapa (embed HTML / iframe)",
        blank=True,
        help_text="Wklej kod iframe z Google Maps. Puste = brak mapy.",
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("contact_cards", label="Karty kontaktowe"),
        InlinePanel("form_fields", label="Pola formularza"),
        FieldPanel("thank_you_text"),
        FieldPanel("map_embed"),
        MultiFieldPanel(
            [
                FieldPanel("to_address"),
                FieldPanel("from_address"),
                FieldPanel("subject"),
            ],
            heading="Powiadomienie e-mail o zgłoszeniu",
        ),
    ]
    promote_panels = SeoMixin.promote_panels

    template = "pages/contact_page.html"
    landing_page_template = "pages/contact_page_landing.html"

    def process_form_submission(self, form):
        """Odrzuca zgłoszenia z wypełnionym honeypotem (cicho — bot nie wie)."""
        if form.cleaned_data.get("hp_website"):
            return None
        return super().process_form_submission(form)

    class Meta:
        verbose_name = "Strona kontaktu"
        verbose_name_plural = "Strony kontaktu"
