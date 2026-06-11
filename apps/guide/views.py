"""Widok Przewodnika moderatora — renderuje pliki Markdown z docs/przewodnik-moderatora/."""
from pathlib import Path

import markdown as md
from django.conf import settings
from django.shortcuts import render
from wagtail.admin.auth import require_admin_access

GUIDE_DIR = Path(settings.BASE_DIR) / "docs" / "przewodnik-moderatora"
MD_EXTENSIONS = ["toc", "tables", "fenced_code", "sane_lists"]


def _load_markdown() -> str:
    """Skleja wszystkie rozdziały (sort po nazwie pliku) w jeden tekst Markdown."""
    if not GUIDE_DIR.exists():
        return "# Przewodnik moderatora\n\nBrak treści (katalog docs/przewodnik-moderatora/ nie istnieje)."
    chapters = []
    for path in sorted(GUIDE_DIR.glob("*.md")):
        chapters.append(path.read_text(encoding="utf-8"))
    if not chapters:
        return "# Przewodnik moderatora\n\nBrak rozdziałów."
    return "[TOC]\n\n" + "\n\n---\n\n".join(chapters)


@require_admin_access
def handbook(request):
    html = md.markdown(_load_markdown(), extensions=MD_EXTENSIONS)
    return render(request, "guide/handbook.html", {"content_html": html})
