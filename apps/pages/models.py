"""Statyczne typy stron: LegalPage (dokumenty prawne); ContactPage dodawany w Task 9."""
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

from apps.shared.models import BasePage


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
