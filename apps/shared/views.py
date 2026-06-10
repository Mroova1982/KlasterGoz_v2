"""Widoki współdzielone — robots.txt."""
from django.conf import settings
from django.http import HttpResponse


def robots_txt(request) -> HttpResponse:
    """robots.txt zależne od środowiska.

    Prod (SEO_ALLOW_INDEXING=True): pełne indeksowanie + sitemap.
    Staging/dev domyślnie blokuje crawlerów (SEO_ALLOW_INDEXING=False).
    """
    if getattr(settings, "SEO_ALLOW_INDEXING", False):
        lines = [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /django-admin/",
            f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
        ]
    else:
        lines = ["User-agent: *", "Disallow: /"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
