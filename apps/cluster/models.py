"""Filar Klaster: snippety (Member, TeamMember, Partner) + strony (dalej w kolejnych zadaniach)."""
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from apps.shared.models import BasePage


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


class MembersIndexPage(BasePage):
    """Lista członków pod /klaster/czlonkowie — filtrowalna po sektorze."""

    eyebrow = models.CharField(max_length=80, blank=True, default="Społeczność klastra")
    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [FieldPanel("eyebrow"), FieldPanel("intro")]
    promote_panels = BasePage.promote_panels
    template = "cluster/members_index_page.html"
    parent_page_types = ["home.PillarPage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request):
        from apps.cluster.models import Member
        ctx = super().get_context(request)
        active = request.GET.get("sektor", "")
        members = Member.objects.all()
        if active:
            members = members.filter(sector=active)
        ctx["members"] = members
        ctx["active_sector"] = active
        ctx["sectors"] = Member.SECTOR_CHOICES
        return ctx

    class Meta:
        verbose_name = "Lista członków"


class TeamPage(BasePage):
    """Zespół pod /klaster/zespol — osoby pogrupowane (zarząd / biuro / rada)."""

    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [FieldPanel("intro")]
    promote_panels = BasePage.promote_panels
    template = "cluster/team_page.html"
    parent_page_types = ["home.PillarPage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request):
        from apps.cluster.models import TeamMember
        ctx = super().get_context(request)
        groups = []
        for value, label in TeamMember.GROUP_CHOICES:
            people = TeamMember.objects.filter(group=value)
            if people:
                groups.append({"label": label, "people": people})
        ctx["groups"] = groups
        return ctx

    class Meta:
        verbose_name = "Zespół"


class PartnersPage(BasePage):
    """Partnerzy pod /klaster/partnerzy — pogrupowani po typie."""

    intro = RichTextField("Wstęp", blank=True, features=["bold", "italic", "link"])

    content_panels = BasePage.content_panels + [FieldPanel("intro")]
    promote_panels = BasePage.promote_panels
    template = "cluster/partners_page.html"
    parent_page_types = ["home.PillarPage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request):
        from apps.cluster.models import Partner
        ctx = super().get_context(request)
        groups = []
        for value, label in Partner.TYPE_CHOICES:
            items = Partner.objects.filter(type=value)
            if items:
                groups.append({"label": label, "items": items})
        ctx["groups"] = groups
        return ctx

    class Meta:
        verbose_name = "Partnerzy"
