from django.conf import settings
from django.urls import path, re_path

from convertit import views

urlpatterns = [
    path("", views.home, name="home"),
    path("ui/", views.ui_view, name="ui"),
    re_path(r"^static/(?P<path>.*)$", views.serve_static, name="static"),
    re_path(r"^converted/(?P<path>.*)$", views.serve_converted, name="converted"),
]

converted_url = getattr(settings, "CONVERTIT_CONVERTED_URL", "converted")
if not converted_url.startswith(("http://", "https://")):
    prefix = converted_url.strip("/")
    if prefix and prefix != "converted":
        urlpatterns.append(
            re_path(
                rf"^{prefix}/(?P<path>.*)$",
                views.serve_converted,
                name="converted_custom",
            )
        )
