"""Usługi klastra: ServicesIndexPage (katalog) + ServicePage (5 usług)."""

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable

from apps.shared.models import BasePage


class ServicesIndexPage(BasePage):
    """Katalog usług pod /klaster/uslugi — auto-lista stron ServicePage."""

    eyebrow = models.CharField("Nadtytuł", max_length=80, blank=True, default="Usługi klastra")
    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [
        FieldPanel("eyebrow"),
        FieldPanel("intro"),
    ]
    promote_panels = BasePage.promote_panels
    template = "services/services_index_page.html"

    parent_page_types = ["home.PillarPage"]
    subpage_types = ["services.ServicePage"]
    max_count = 1

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["services"] = self.get_children().live().specific()
        return ctx

    class Meta:
        verbose_name = "Katalog usług"


class ServiceBenefit(Orderable):
    """Kafelek 'dla kogo / korzyść' na stronie usługi."""

    page = ParentalKey("ServicePage", on_delete=models.CASCADE, related_name="benefits")
    tag = models.CharField("Tag", max_length=40, blank=True)
    title = models.CharField("Tytuł", max_length=160)
    description = models.TextField("Opis", blank=True)
    panels = [FieldPanel("tag"), FieldPanel("title"), FieldPanel("description")]


class ServiceStep(Orderable):
    """Etap procesu usługi."""

    page = ParentalKey("ServicePage", on_delete=models.CASCADE, related_name="steps")
    number = models.CharField("Numer", max_length=4, help_text="np. '01'")
    title = models.CharField("Tytuł", max_length=120)
    description = models.TextField("Opis", blank=True)
    panels = [FieldPanel("number"), FieldPanel("title"), FieldPanel("description")]


class ServiceFAQ(Orderable):
    """Pytanie FAQ na stronie usługi."""

    page = ParentalKey("ServicePage", on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField("Pytanie", max_length=255)
    answer = RichTextField("Odpowiedź", features=["bold", "italic", "link"])
    panels = [FieldPanel("question"), FieldPanel("answer")]


class ServicePage(BasePage):
    """Pojedyncza usługa (KNR Green / PRO GOZ / PRO INNO / GO GREEN / PRO EKO)."""

    tag = models.CharField("Tag (chip w hero)", max_length=40, blank=True)
    hero_lead = models.TextField("Lead w hero", blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    primary_cta_label = models.CharField("CTA główne — tekst", max_length=60, blank=True)
    primary_cta_url = models.CharField("CTA główne — URL", max_length=255, blank=True)
    secondary_cta_label = models.CharField("CTA drugie — tekst", max_length=60, blank=True)
    secondary_cta_url = models.CharField("CTA drugie — URL", max_length=255, blank=True)

    hero_box_chip = models.CharField("Box hero — etykieta", max_length=40, blank=True)
    hero_box_heading = models.CharField("Box hero — nagłówek", max_length=120, blank=True)
    hero_box_items = models.TextField("Box hero — pozycje (jedna na linię)", blank=True)

    intro = RichTextField("Opis usługi", blank=True, features=["bold", "italic", "link"])

    benefits_heading = models.CharField("Nagłówek sekcji korzyści", max_length=160, blank=True)
    process_heading = models.CharField("Nagłówek sekcji procesu", max_length=160, blank=True)

    pricing = RichTextField("Cennik / widełki", blank=True, features=["bold", "italic", "link"])

    faq_heading = models.CharField(
        "Nagłówek sekcji FAQ", max_length=160, blank=True, default="Najczęściej zadawane pytania."
    )

    cta_heading = models.CharField("CTA strip — nagłówek", max_length=200, blank=True)
    cta_lead = models.TextField("CTA strip — lead", blank=True)
    cta_button_label = models.CharField("CTA strip — przycisk", max_length=60, blank=True)
    cta_button_url = models.CharField("CTA strip — URL", max_length=255, blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("tag"),
                FieldPanel("hero_lead"),
                FieldPanel("hero_image"),
                FieldPanel("primary_cta_label"),
                FieldPanel("primary_cta_url"),
                FieldPanel("secondary_cta_label"),
                FieldPanel("secondary_cta_url"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("hero_box_chip"),
                FieldPanel("hero_box_heading"),
                FieldPanel("hero_box_items"),
            ],
            heading="Hero — boczny box (opcjonalny)",
        ),
        FieldPanel("intro"),
        FieldPanel("benefits_heading"),
        InlinePanel("benefits", label="Korzyści / dla kogo"),
        FieldPanel("process_heading"),
        InlinePanel("steps", label="Etapy procesu"),
        FieldPanel("pricing"),
        FieldPanel("faq_heading"),
        InlinePanel("faqs", label="FAQ"),
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
    template = "services/service_page.html"

    parent_page_types = ["services.ServicesIndexPage"]
    subpage_types = []

    def hero_box_item_list(self) -> list[str]:
        return [i.strip() for i in self.hero_box_items.splitlines() if i.strip()]

    class Meta:
        verbose_name = "Usługa"
        verbose_name_plural = "Usługi"
