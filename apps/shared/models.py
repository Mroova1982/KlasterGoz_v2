"""Współdzielone modele: mixin SEO, bazowa strona, ustawienia globalne."""
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page


class SeoMixin(models.Model):
    """Wspólne pola i kontekst SEO. Komponowalny z Page i AbstractEmailForm.

    Korzysta z wbudowanych pól Wagtaila (`seo_title`, `search_description`)
    i dokłada obraz Open Graph oraz metody budujące kontekst dla szablonu meta.
    """

    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Obraz social (Open Graph)",
        help_text="Obraz pokazywany przy udostępnianiu na FB/LinkedIn. Zalecane 1200×630 px.",
    )

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("slug"),
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel("og_image"),
            ],
            heading="SEO i social",
        ),
    ]

    class Meta:
        abstract = True

    def get_meta_title(self) -> str:
        """Tytuł do <title> i og:title — seo_title z fallbackiem do title."""
        return self.seo_title or self.title

    def get_meta_description(self) -> str:
        return self.search_description or ""

    def get_meta_image(self):
        """Obraz OG strony albo None (szablon spada wtedy do domyślnego)."""
        return self.og_image


class BasePage(SeoMixin, Page):
    """Bazowa strona portalu — wszystkie typy dziedziczą stąd dla spójnego SEO."""

    class Meta:
        abstract = True
