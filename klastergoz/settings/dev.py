"""Development settings — local Docker Compose stack."""

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
INSTALLED_APPS += ["wagtail.contrib.styleguide"]  # admin design system tool

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Wagtail rzecze: w dev wyłączamy cache strony, żeby zmiany w admin'ie były widoczne natychmiast.
CACHES["default"]["BACKEND"] = "django.core.cache.backends.dummy.DummyCache"

# Manifest static storage (prod) wymaga collectstatic; w dev używamy prostego
# backendu, żeby runserver serwował {% static %} bez budowania manifestu.
STORAGES = {
    **STORAGES,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

SEO_ALLOW_INDEXING = True
