"""Modele strony głównej i filarów: snippety (HeroSlide, Pillar, Statistic), HomePage, PillarPage."""

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet

from apps.shared.models import BasePage


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
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
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

    class Meta:
        verbose_name = "Slajd hero"
        verbose_name_plural = "Slajdy hero"

    def __str__(self):
        return self.eyebrow or (self.lead[:40] if self.lead else "Slajd hero")


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
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
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

    class Meta:
        verbose_name = "Filar"
        verbose_name_plural = "Filary"

    def __str__(self):
        return self.title

    def bullet_list(self) -> list[str]:
        return [b.strip() for b in self.bullets.splitlines() if b.strip()]


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

    panels = [
        FieldPanel("value"),
        FieldPanel("label"),
        FieldPanel("group"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Statystyka"
        verbose_name_plural = "Statystyki"

    def __str__(self):
        return f"{self.value} — {self.label}"


class PillarBenefit(Orderable):
    """Kafelek korzyści na stronie-filarze."""

    page = ParentalKey("PillarPage", on_delete=models.CASCADE, related_name="benefits")
    tag = models.CharField("Tag", max_length=40, blank=True)
    title = models.CharField("Tytuł", max_length=120)
    description = models.TextField("Opis", blank=True)

    panels = [FieldPanel("tag"), FieldPanel("title"), FieldPanel("description")]


class PillarStep(Orderable):
    """Krok procesu (np. jak dołączyć)."""

    page = ParentalKey("PillarPage", on_delete=models.CASCADE, related_name="steps")
    number = models.CharField("Numer", max_length=4, help_text="np. '01'")
    title = models.CharField("Tytuł", max_length=80)
    description = models.TextField("Opis", blank=True)

    panels = [FieldPanel("number"), FieldPanel("title"), FieldPanel("description")]


class PillarPage(BasePage):
    """Landing filaru (Klaster / Edukacja / Doradztwo). Jeden typ, 3 instancje."""

    eyebrow = models.CharField("Nadtytuł (np. 'Filar 01 · Klaster')", max_length=120, blank=True)
    hero_lead = models.TextField("Lead w hero", blank=True)
    primary_cta_label = models.CharField("CTA główne — tekst", max_length=60, blank=True)
    primary_cta_url = models.CharField("CTA główne — URL", max_length=255, blank=True)
    secondary_cta_label = models.CharField("CTA drugie — tekst", max_length=60, blank=True)
    secondary_cta_url = models.CharField("CTA drugie — URL", max_length=255, blank=True)

    benefits_heading = models.CharField("Nagłówek sekcji korzyści", max_length=160, blank=True)

    feature_heading = models.CharField("Blok 'jak działamy' — nagłówek", max_length=160, blank=True)
    feature_lead = models.TextField("Blok 'jak działamy' — lead", blank=True)
    feature_bullets = models.TextField("Blok 'jak działamy' — punkty (jeden na linię)", blank=True)

    steps_heading = models.CharField("Nagłówek sekcji procesu", max_length=160, blank=True)

    cta_heading = models.CharField("CTA strip — nagłówek", max_length=200, blank=True)
    cta_lead = models.TextField("CTA strip — lead", blank=True)
    cta_button_label = models.CharField("CTA strip — przycisk", max_length=60, blank=True)
    cta_button_url = models.CharField("CTA strip — URL", max_length=255, blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("eyebrow"),
                FieldPanel("hero_lead"),
                FieldPanel("primary_cta_label"),
                FieldPanel("primary_cta_url"),
                FieldPanel("secondary_cta_label"),
                FieldPanel("secondary_cta_url"),
            ],
            heading="Hero",
        ),
        FieldPanel("benefits_heading"),
        InlinePanel("benefits", label="Korzyści"),
        MultiFieldPanel(
            [
                FieldPanel("feature_heading"),
                FieldPanel("feature_lead"),
                FieldPanel("feature_bullets"),
            ],
            heading="Blok 'jak działamy'",
        ),
        FieldPanel("steps_heading"),
        InlinePanel("steps", label="Kroki procesu"),
        MultiFieldPanel(
            [
                FieldPanel("cta_heading"),
                FieldPanel("cta_lead"),
                FieldPanel("cta_button_label"),
                FieldPanel("cta_button_url"),
            ],
            heading="CTA strip",
        ),
    ]
    promote_panels = BasePage.promote_panels
    template = "home/pillar_page.html"

    def feature_bullet_list(self) -> list[str]:
        return [b.strip() for b in self.feature_bullets.splitlines() if b.strip()]

    def get_context(self, request):
        ctx = super().get_context(request)
        # Żywe dzieci strony-filaru (puste w Fazie 1 — podstrony dochodzą w Fazach 2–4).
        ctx["children"] = self.get_children().live().specific()
        return ctx

    class Meta:
        verbose_name = "Strona filaru"
        verbose_name_plural = "Strony filarów"


class HomeHeroSlide(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="hero_slides")
    slide = models.ForeignKey("home.HeroSlide", on_delete=models.CASCADE, related_name="+")
    panels = [FieldPanel("slide")]


class HomePillar(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="home_pillars")
    pillar = models.ForeignKey("home.Pillar", on_delete=models.CASCADE, related_name="+")
    panels = [FieldPanel("pillar")]


class HomeConsultStep(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="consult_steps")
    text = models.CharField("Krok", max_length=200)
    panels = [FieldPanel("text")]


class HomeOffering(Orderable):
    """Kafelek usługi (sekcja 'Usługi klastra'). W Fazie 2 może zostać zastąpiony auto-listą ServicePage."""

    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="offerings")
    tag = models.CharField("Tag", max_length=40, blank=True)
    title = models.CharField("Tytuł", max_length=120)
    description = models.TextField("Opis", blank=True)
    link_label = models.CharField(
        "Tekst linku", max_length=60, blank=True, default="Dowiedz się więcej →"
    )
    url = models.CharField("URL", max_length=255, blank=True)
    panels = [
        FieldPanel("tag"),
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("link_label"),
        FieldPanel("url"),
    ]


class HomeMemberLogo(Orderable):
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="member_logos")
    name = models.CharField("Nazwa", max_length=80)
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    panels = [FieldPanel("name"), FieldPanel("logo")]


class HomeNewsTeaser(Orderable):
    """Teaser aktualności. W Fazie 4 może zostać zastąpiony auto-listą ArticlePage."""

    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="news_teasers")
    category = models.CharField("Kategoria", max_length=40, blank=True)
    reading_time = models.CharField("Czas czytania", max_length=20, blank=True)
    date = models.CharField("Data", max_length=20, blank=True)
    title = models.CharField("Tytuł", max_length=200)
    excerpt = models.TextField("Zajawka", blank=True)
    url = models.CharField("URL", max_length=255, blank=True)
    panels = [
        FieldPanel("category"),
        FieldPanel("reading_time"),
        FieldPanel("date"),
        FieldPanel("title"),
        FieldPanel("excerpt"),
        FieldPanel("url"),
    ]


class HomePage(BasePage):
    """Strona główna portalu (root Site)."""

    pillars_eyebrow = models.CharField(max_length=80, blank=True, default="Co robimy")
    pillars_heading = models.CharField(max_length=200, blank=True)
    pillars_lead = models.TextField(blank=True)

    consult_eyebrow = models.CharField(max_length=80, blank=True, default="Bezpłatna konsultacja")
    consult_heading = models.CharField(max_length=200, blank=True)
    consult_lead = models.TextField(blank=True)
    consult_cta_label = models.CharField(max_length=60, blank=True, default="Wyślij zgłoszenie")
    consult_cta_url = models.CharField(max_length=255, blank=True)

    services_eyebrow = models.CharField(max_length=80, blank=True, default="Usługi klastra")
    services_heading = models.CharField(max_length=200, blank=True)
    services_cta_label = models.CharField(max_length=60, blank=True, default="Cała oferta")
    services_cta_url = models.CharField(max_length=255, blank=True)

    members_eyebrow = models.CharField(max_length=80, blank=True, default="Zaufali nam")
    members_heading = models.CharField(max_length=200, blank=True)

    about_eyebrow = models.CharField(max_length=80, blank=True, default="O klastrze")
    about_heading = models.CharField(max_length=200, blank=True)
    about_lead = models.TextField(blank=True)
    about_bullets = models.TextField("Punkty (jeden na linię)", blank=True)
    about_cta_label = models.CharField(max_length=60, blank=True)
    about_cta_url = models.CharField(max_length=255, blank=True)
    about_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    news_eyebrow = models.CharField(max_length=80, blank=True, default="Aktualności")
    news_heading = models.CharField(max_length=200, blank=True)
    news_cta_label = models.CharField(max_length=60, blank=True, default="Wszystkie wpisy")
    news_cta_url = models.CharField(max_length=255, blank=True)

    cta_chip = models.CharField(max_length=60, blank=True, default="Krajowy Klaster Kluczowy")
    cta_heading = models.CharField(max_length=200, blank=True)
    cta_lead = models.TextField(blank=True)
    cta_primary_label = models.CharField(max_length=60, blank=True)
    cta_primary_url = models.CharField(max_length=255, blank=True)
    cta_secondary_label = models.CharField(max_length=60, blank=True)
    cta_secondary_url = models.CharField(max_length=255, blank=True)

    content_panels = BasePage.content_panels + [
        InlinePanel("hero_slides", label="Slajdy hero"),
        MultiFieldPanel(
            [
                FieldPanel("pillars_eyebrow"),
                FieldPanel("pillars_heading"),
                FieldPanel("pillars_lead"),
            ],
            heading="Sekcja: Filary — nagłówek",
        ),
        InlinePanel("home_pillars", label="Filary (kafelki)"),
        MultiFieldPanel(
            [
                FieldPanel("consult_eyebrow"),
                FieldPanel("consult_heading"),
                FieldPanel("consult_lead"),
                FieldPanel("consult_cta_label"),
                FieldPanel("consult_cta_url"),
            ],
            heading="Sekcja: Konsultacja",
        ),
        InlinePanel("consult_steps", label="Kroki konsultacji"),
        MultiFieldPanel(
            [
                FieldPanel("services_eyebrow"),
                FieldPanel("services_heading"),
                FieldPanel("services_cta_label"),
                FieldPanel("services_cta_url"),
            ],
            heading="Sekcja: Usługi — nagłówek",
        ),
        InlinePanel("offerings", label="Kafelki usług"),
        MultiFieldPanel(
            [FieldPanel("members_eyebrow"), FieldPanel("members_heading")],
            heading="Sekcja: Członkowie — nagłówek",
        ),
        InlinePanel("member_logos", label="Logosy członków"),
        MultiFieldPanel(
            [
                FieldPanel("about_eyebrow"),
                FieldPanel("about_heading"),
                FieldPanel("about_lead"),
                FieldPanel("about_bullets"),
                FieldPanel("about_cta_label"),
                FieldPanel("about_cta_url"),
                FieldPanel("about_image"),
            ],
            heading="Sekcja: O klastrze",
        ),
        MultiFieldPanel(
            [
                FieldPanel("news_eyebrow"),
                FieldPanel("news_heading"),
                FieldPanel("news_cta_label"),
                FieldPanel("news_cta_url"),
            ],
            heading="Sekcja: Aktualności — nagłówek",
        ),
        InlinePanel("news_teasers", label="Teasery aktualności"),
        MultiFieldPanel(
            [
                FieldPanel("cta_chip"),
                FieldPanel("cta_heading"),
                FieldPanel("cta_lead"),
                FieldPanel("cta_primary_label"),
                FieldPanel("cta_primary_url"),
                FieldPanel("cta_secondary_label"),
                FieldPanel("cta_secondary_url"),
            ],
            heading="Sekcja: CTA strip",
        ),
    ]
    promote_panels = BasePage.promote_panels
    template = "home/home_page.html"

    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    def about_bullet_list(self) -> list[str]:
        return [b.strip() for b in self.about_bullets.splitlines() if b.strip()]

    def get_context(self, request):
        from apps.home.models import Statistic

        ctx = super().get_context(request)
        ctx["stats_strip"] = Statistic.objects.filter(group="home_strip")
        ctx["stats_section"] = Statistic.objects.filter(group="home_section")
        return ctx

    class Meta:
        verbose_name = "Strona główna"
