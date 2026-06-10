"""Bloki StreamField dla nawigacji, stopki i portali (Site Settings)."""

from wagtail import blocks


class LinkBlock(blocks.StructBlock):
    """Pojedynczy link: tekst + cel (strona Wagtaila ALBO zewnętrzny URL).

    Jeśli ustawione oba — wygrywa `page`. `get_url` zwraca finalny adres.
    """

    label = blocks.CharBlock(label="Tekst linku", max_length=80)
    page = blocks.PageChooserBlock(label="Strona (wewnętrzna)", required=False)
    url = blocks.URLBlock(label="Adres URL (zewnętrzny)", required=False)
    description = blocks.CharBlock(
        label="Opis (mały tekst pod linkiem)", required=False, max_length=120
    )

    class Meta:
        icon = "link"
        label = "Link"

    def get_url(self, value) -> str:
        page = value.get("page")
        if page:
            return page.url
        return value.get("url") or "#"


class MenuColumnBlock(blocks.StructBlock):
    """Kolumna w dropdownie/mega-menu: opcjonalny nagłówek + lista linków."""

    heading = blocks.CharBlock(label="Nagłówek kolumny", required=False, max_length=80)
    links = blocks.ListBlock(LinkBlock(), label="Linki")

    class Meta:
        icon = "list-ul"
        label = "Kolumna menu"


class MenuItemBlock(blocks.StructBlock):
    """Pozycja menu głównego. Bez kolumn = zwykły link.

    Z kolumnami = dropdown (1 kolumna) lub mega-menu (≥2 kolumny).
    """

    label = blocks.CharBlock(label="Tekst pozycji", max_length=60)
    page = blocks.PageChooserBlock(label="Strona docelowa", required=False)
    url = blocks.URLBlock(label="URL docelowy (jeśli brak strony)", required=False)
    nav_key = blocks.CharBlock(
        label="Klucz aktywności",
        required=False,
        max_length=40,
        help_text="np. 'klaster' — podświetla pozycję na stronach tego działu.",
    )
    columns = blocks.ListBlock(MenuColumnBlock(), label="Kolumny dropdownu", required=False)

    class Meta:
        icon = "bars"
        label = "Pozycja menu"

    def get_url(self, value) -> str:
        page = value.get("page")
        if page:
            return page.url
        return value.get("url") or "#"


class FooterColumnBlock(blocks.StructBlock):
    """Kolumna stopki: nagłówek + lista linków."""

    heading = blocks.CharBlock(label="Nagłówek kolumny", max_length=80)
    links = blocks.ListBlock(LinkBlock(), label="Linki")

    class Meta:
        icon = "list-ul"
        label = "Kolumna stopki"


class PortalLinkBlock(blocks.StructBlock):
    """Zewnętrzny portal w dropdownie 'Strefa logowania'."""

    label = blocks.CharBlock(label="Nazwa portalu", max_length=80)
    description = blocks.CharBlock(label="Opis", required=False, max_length=120)
    url = blocks.URLBlock(label="Adres portalu")

    class Meta:
        icon = "user"
        label = "Portal logowania"
