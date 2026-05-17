"""Test settings — SQLite in-memory dla szybkich testów."""
from .base import *

DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
CACHES["default"]["BACKEND"] = "django.core.cache.backends.dummy.DummyCache"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]   # fast hashing for tests
