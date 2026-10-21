import configparser
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_ini_settings():
    ini_file = os.environ.get("CONVERTIT_INI") or os.environ.get("INIPASTE")
    if not ini_file:
        for candidate in (
            "/opt/convertit/convertit.ini",
            str(BASE_DIR / "production.ini"),
            str(BASE_DIR / "development.ini"),
        ):
            if os.path.exists(candidate):
                ini_file = candidate
                break

    app_settings = {}
    server_settings = {}
    if ini_file and os.path.exists(ini_file):
        here_dir = os.path.dirname(os.path.abspath(ini_file))
        parser = configparser.RawConfigParser()
        parser.read(ini_file)
        if parser.has_section("app:main"):
            for key, value in parser.items("app:main"):
                app_settings[key] = value.replace("%(here)s", here_dir)
        if parser.has_section("server:main"):
            for key, value in parser.items("server:main"):
                server_settings[key] = value.replace("%(here)s", here_dir)

    return app_settings, server_settings


INI_APP_SETTINGS, INI_SERVER_SETTINGS = load_ini_settings()

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-convertit-default-secret-key"
)

DEBUG = os.environ.get(
    "DEBUG",
    INI_APP_SETTINGS.get(
        "debug", INI_APP_SETTINGS.get("pyramid.reload_templates", "false")
    ),
).lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "convertit.apps.ConvertitConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "convertit.urls"

WSGI_APPLICATION = "convertit.wsgi.application"
ASGI_APPLICATION = "convertit.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

LANGUAGE_CODE = INI_APP_SETTINGS.get(
    "default_locale_name",
    INI_APP_SETTINGS.get("pyramid.default_locale_name", "en-us"),
)
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "convertit" / "static",
]

CONVERTIT_DOWNLOADS_PATH = os.environ.get(
    "CONVERTIT_DOWNLOADS_PATH",
    INI_APP_SETTINGS.get(
        "convertit.downloads_path", "/var/cache/convertit/downloads"
    ),
)
CONVERTIT_DOWNLOADS_MAX_AGE = int(
    os.environ.get(
        "CONVERTIT_DOWNLOADS_MAX_AGE",
        INI_APP_SETTINGS.get("convertit.downloads_max_age", 3600),
    )
)
CONVERTIT_CONVERTED_PATH = os.environ.get(
    "CONVERTIT_CONVERTED_PATH",
    INI_APP_SETTINGS.get(
        "convertit.converted_path", "/var/cache/convertit/converted"
    ),
)
CONVERTIT_CONVERTED_MAX_AGE = int(
    os.environ.get(
        "CONVERTIT_CONVERTED_MAX_AGE",
        INI_APP_SETTINGS.get("convertit.converted_max_age", 3600),
    )
)
CONVERTIT_CONVERTED_URL = os.environ.get(
    "CONVERTIT_CONVERTED_URL",
    INI_APP_SETTINGS.get("convertit.converted_url", "converted"),
)
CONVERTIT_CONVERTED_NAME = os.environ.get(
    "CONVERTIT_CONVERTED_NAME",
    INI_APP_SETTINGS.get(
        "convertit.converted_name",
        "{url_hostname}_{url_port}_{url_dirname}_{url_filename}{extension}",
    ),
)
CONVERTIT_CONVERTERS = os.environ.get(
    "CONVERTIT_CONVERTERS",
    INI_APP_SETTINGS.get(
        "convertit.converters",
        "convertit.converters.unoconv\nconvertit.converters.cairosvg",
    ),
).split()

CONVERTIT_HOST = os.environ.get(
    "CONVERTIT_HOST", INI_SERVER_SETTINGS.get("host", "0.0.0.0")
)
CONVERTIT_PORT = int(
    os.environ.get("CONVERTIT_PORT", INI_SERVER_SETTINGS.get("port", 6543))
)
