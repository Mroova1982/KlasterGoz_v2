from apps.shared.models import SeoMixin


class _Dummy(SeoMixin):
    """Lekki obiekt do testu metod (bez zapisu do bazy)."""

    class Meta:
        app_label = "shared"
        abstract = True

    def __init__(self, title="", seo_title="", search_description=""):
        self.title = title
        self.seo_title = seo_title
        self.search_description = search_description
        # Store og_image directly in __dict__ to bypass the FK descriptor
        # (the descriptor requires a concrete model; _Dummy is abstract-only).
        self.__dict__["og_image"] = None


def test_meta_title_falls_back_to_title():
    d = _Dummy(title="Kontakt", seo_title="")
    assert d.get_meta_title() == "Kontakt"


def test_meta_title_uses_seo_title_when_set():
    d = _Dummy(title="Kontakt", seo_title="Kontakt — Klaster GOZ")
    assert d.get_meta_title() == "Kontakt — Klaster GOZ"


def test_meta_description_empty_by_default():
    d = _Dummy(title="X")
    assert d.get_meta_description() == ""
