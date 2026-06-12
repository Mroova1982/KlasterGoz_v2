"""Filar Klaster: snippety (Member, TeamMember, Partner) + strony (dalej w kolejnych zadaniach)."""
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Member(models.Model):
    """Członek klastra (firma/instytucja)."""

    SECTOR_CHOICES = [
        ("recykling", "Recykling"),
        ("produkcja", "Produkcja"),
        ("technologie", "Technologie"),
        ("nauka", "Nauka"),
        ("doradztwo", "Doradztwo"),
        ("finanse", "Finanse"),
        ("administracja", "Administracja"),
    ]
    name = models.CharField("Nazwa", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True)
    sector = models.CharField("Sektor", max_length=20, choices=SECTOR_CHOICES, default="recykling")
    description = models.TextField("Opis", blank=True)
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    website = models.URLField("Strona WWW", blank=True)
    is_featured = models.BooleanField("Wyróżniony", default=False)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("sector"),
        FieldPanel("description"),
        FieldPanel("logo"),
        FieldPanel("website"),
        FieldPanel("is_featured"),
    ]

    def initials(self) -> str:
        parts = [w for w in self.name.replace("|", " ").split() if w]
        return "".join(w[0] for w in parts[:2]).upper()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Członek"
        verbose_name_plural = "Członkowie"


@register_snippet
class TeamMember(models.Model):
    """Osoba z zespołu klastra."""

    GROUP_CHOICES = [
        ("zarzad", "Zarząd i koordynator"),
        ("biuro", "Biuro klastra"),
        ("rada", "Rada klastra"),
    ]
    name = models.CharField("Imię i nazwisko", max_length=160)
    role = models.CharField("Rola", max_length=160, blank=True)
    group = models.CharField("Grupa", max_length=20, choices=GROUP_CHOICES, default="biuro")
    photo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    bio = models.TextField("Bio", blank=True)
    email = models.EmailField("E-mail", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    sort_order = models.IntegerField("Kolejność", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("group"),
        FieldPanel("photo"),
        FieldPanel("bio"),
        FieldPanel("email"),
        FieldPanel("linkedin"),
        FieldPanel("sort_order"),
    ]

    def initials(self) -> str:
        parts = [w for w in self.name.split() if w]
        return "".join(w[0] for w in parts[:2]).upper()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Osoba zespołu"
        verbose_name_plural = "Zespół"


@register_snippet
class Partner(models.Model):
    """Partner klastra (instytucja / uczelnia / klaster UE / branżowy)."""

    TYPE_CHOICES = [
        ("instytucja", "Instytucja publiczna"),
        ("uczelnia", "Uczelnia / jednostka naukowa"),
        ("klaster_ue", "Klaster partnerski w UE"),
        ("branzowy", "Partner branżowy"),
    ]
    name = models.CharField("Nazwa", max_length=200)
    type = models.CharField("Typ", max_length=20, choices=TYPE_CHOICES, default="instytucja")
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    link = models.URLField("Link", blank=True)
    sort_order = models.IntegerField("Kolejność", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("type"),
        FieldPanel("logo"),
        FieldPanel("link"),
        FieldPanel("sort_order"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Partner"
        verbose_name_plural = "Partnerzy"
