"""Współdzielone modele: mixin SEO, bazowa strona, ustawienia globalne."""
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.shared import blocks


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


@register_setting
class GeneralSettings(BaseGenericSetting):
    """Dane kontaktowe i tożsamość klastra (header utility bar, stopka, ContactPage)."""

    organization_name = models.CharField(
        "Nazwa organizacji", max_length=200, default="Klaster GOZ"
    )
    phone = models.CharField("Telefon", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    address = models.TextField("Adres", blank=True, help_text="Może być wieloliniowy.")
    nip = models.CharField("NIP", max_length=20, blank=True)
    footer_description = models.TextField(
        "Opis w stopce", blank=True, max_length=400
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Logo w headerze. Puste = domyślne logo z design systemu.",
    )

    panels = [
        FieldPanel("organization_name"),
        FieldPanel("logo"),
        MultiFieldPanel(
            [FieldPanel("phone"), FieldPanel("email"), FieldPanel("address"), FieldPanel("nip")],
            heading="Kontakt",
        ),
        FieldPanel("footer_description"),
    ]

    class Meta:
        verbose_name = "Dane ogólne"


@register_setting
class SocialMediaSettings(BaseGenericSetting):
    """Linki do social media (stopka)."""

    linkedin = models.URLField("LinkedIn", blank=True)
    facebook = models.URLField("Facebook", blank=True)
    youtube = models.URLField("YouTube", blank=True)

    class Meta:
        verbose_name = "Social media"


@register_setting
class AnalyticsSettings(BaseGenericSetting):
    """Google Analytics 4 + treść bannera cookies (RODO)."""

    ga4_measurement_id = models.CharField(
        "GA4 Measurement ID",
        max_length=20,
        blank=True,
        help_text="np. G-XXXXXXXXXX. Puste = analytics wyłączone.",
    )
    cookie_banner_text = models.TextField(
        "Treść bannera cookies",
        blank=True,
        default=(
            "Używamy plików cookies do analizy ruchu (Google Analytics). "
            "Możesz zaakceptować lub odrzucić."
        ),
    )

    class Meta:
        verbose_name = "Analytics i cookies"
