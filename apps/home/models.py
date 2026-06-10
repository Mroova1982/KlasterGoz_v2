"""Modele strony głównej i filarów: snippety (HeroSlide, Pillar, Statistic), HomePage, PillarPage."""
from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField


@register_snippet
class HeroSlide(models.Model):
    """Slajd hero na stronie głównej (3 sztuki wg mockupu)."""

    eyebrow = models.CharField("Nadtytuł (eyebrow)", max_length=120, blank=True)
    headline = RichTextField(
        "Nagłówek",
        features=["italic"],
        help_text="Użyj kursywy (em) dla akcentu, jak w mockupie.",
    )
    lead = models.TextField("Lead", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Tło slajdu.",
    )
    primary_cta_label = models.CharField("CTA główne — tekst", max_length=60, blank=True)
    primary_cta_url = models.CharField("CTA główne — URL", max_length=255, blank=True)
    secondary_cta_label = models.CharField("CTA drugie — tekst", max_length=60, blank=True)
    secondary_cta_url = models.CharField("CTA drugie — URL", max_length=255, blank=True)

    panels = [
        FieldPanel("eyebrow"),
        FieldPanel("headline"),
        FieldPanel("lead"),
        FieldPanel("image"),
        FieldPanel("primary_cta_label"),
        FieldPanel("primary_cta_url"),
        FieldPanel("secondary_cta_label"),
        FieldPanel("secondary_cta_url"),
    ]

    def __str__(self):
        return self.eyebrow or (self.lead[:40] if self.lead else "Slajd hero")

    class Meta:
        verbose_name = "Slajd hero"
        verbose_name_plural = "Slajdy hero"


@register_snippet
class Pillar(models.Model):
    """Filar (3 sztuki) — kafelek na home, linkuje do strony-filaru."""

    number = models.CharField("Numer", max_length=12, help_text="np. '01 / FILAR'")
    title = models.CharField("Tytuł", max_length=120)
    lead = models.TextField("Opis")
    bullets = models.TextField("Punkty (jeden na linię)", blank=True)
    icon_svg = models.TextField(
        "Ikona (inline SVG)", blank=True, help_text="Wklej kod <svg>…</svg>."
    )
    link = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Strona-filar docelowa.",
    )
    cta_label = models.CharField("Tekst linku", max_length=60, blank=True)
    is_dark = models.BooleanField("Wariant ciemny", default=False)

    panels = [
        FieldPanel("number"),
        FieldPanel("title"),
        FieldPanel("lead"),
        FieldPanel("bullets"),
        FieldPanel("icon_svg"),
        FieldPanel("link"),
        FieldPanel("cta_label"),
        FieldPanel("is_dark"),
    ]

    def bullet_list(self) -> list[str]:
        return [b.strip() for b in self.bullets.splitlines() if b.strip()]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Filar"
        verbose_name_plural = "Filary"


@register_snippet
class Statistic(models.Model):
    """Statystyka liczbowa (paski na home)."""

    GROUP_CHOICES = [
        ("home_strip", "Home — pasek pod hero"),
        ("home_section", "Home — sekcja statystyk"),
        ("about_klastra", "O klastrze"),
    ]
    value = models.CharField("Wartość", max_length=40, help_text="np. '150+' lub '240 mln zł'")
    label = models.CharField("Opis", max_length=160)
    group = models.CharField("Grupa", max_length=20, choices=GROUP_CHOICES, default="home_strip")
    sort_order = models.IntegerField("Kolejność", default=0)

    panels = [FieldPanel("value"), FieldPanel("label"), FieldPanel("group"), FieldPanel("sort_order")]

    def __str__(self):
        return f"{self.value} — {self.label}"

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Statystyka"
        verbose_name_plural = "Statystyki"
