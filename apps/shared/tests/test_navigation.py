import pytest

from apps.shared.blocks import LinkBlock, MenuItemBlock


def test_linkblock_url_fallback_hash():
    block = LinkBlock()
    value = block.to_python({"label": "X", "page": None, "url": "", "description": ""})
    assert block.get_url(value) == "#"


def test_linkblock_uses_external_url_when_no_page():
    block = LinkBlock()
    value = block.to_python(
        {"label": "RODO", "page": None, "url": "https://example.org/rodo", "description": ""}
    )
    assert block.get_url(value) == "https://example.org/rodo"


def test_menuitemblock_url_fallback_hash():
    block = MenuItemBlock()
    value = block.to_python({"label": "Klaster", "page": None, "url": "", "nav_key": "", "columns": []})
    assert block.get_url(value) == "#"
