"""Local development settings."""
from .base import *  # noqa: F403

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in {"1", "true", "yes"}
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# A clean checkout can run locally without a MySQL server. Setting DB_NAME in
# .env opts into the MySQL configuration from base.py; production always uses MySQL.
if not os.environ.get("DB_NAME"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / ".local.sqlite3",
    }
