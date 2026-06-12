"""Bloki StreamField dla AboutClusterPage (sekcje long-form 'O klastrze')."""
from wagtail import blocks

BACKGROUNDS = [("none", "Białe"), ("green", "Zielone"), ("dark", "Ciemne")]


class TextSectionBlock(blocks.StructBlock):
    """Sekcja tekstowa: nadtytuł + nagłówek + treść."""

    eyebrow = blocks.CharBlock(required=False, label="Nadtytuł")
    heading = blocks.CharBlock(required=False, label="Nagłówek")
    body = blocks.RichTextBlock(label="Treść", features=["bold", "italic", "link", "ul", "ol"])
    background = blocks.ChoiceBlock(choices=BACKGROUNDS, default="none", label="Tło")

    class Meta:
        icon = "doc-full"
        label = "Sekcja tekstowa"
        template = "cluster/blocks/text_section.html"


class CardBlock(blocks.StructBlock):
    number = blocks.CharBlock(required=False, label="Numer")
    title = blocks.CharBlock(label="Tytuł")
    text = blocks.TextBlock(required=False, label="Opis")


class CardsBlock(blocks.StructBlock):
    """Siatka kart (np. obszary działań / korzyści)."""

    eyebrow = blocks.CharBlock(required=False, label="Nadtytuł")
    heading = blocks.CharBlock(required=False, label="Nagłówek")
    cards = blocks.ListBlock(CardBlock(), label="Karty")
    background = blocks.ChoiceBlock(choices=BACKGROUNDS, default="none", label="Tło")

    class Meta:
        icon = "list-ul"
        label = "Siatka kart"
        template = "cluster/blocks/cards.html"


class StepsBlock(blocks.StructBlock):
    """Numerowane kroki (np. droga do klastra)."""

    eyebrow = blocks.CharBlock(required=False, label="Nadtytuł")
    heading = blocks.CharBlock(required=False, label="Nagłówek")
    steps = blocks.ListBlock(CardBlock(), label="Kroki")
    background = blocks.ChoiceBlock(choices=BACKGROUNDS, default="none", label="Tło")

    class Meta:
        icon = "list-ol"
        label = "Kroki"
        template = "cluster/blocks/steps.html"
