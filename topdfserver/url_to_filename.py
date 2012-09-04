import os
from urlparse import urlsplit

from .slugify import slugify


def url_to_filename(url, default_filename):
    splited_url = urlsplit(url)
    basename = os.path.basename(splited_url.path)
    if basename:
        path = os.path.dirname(splited_url.path)
        filename, ext = os.path.splitext(basename)
    else:
        path = splited_url.path
        filename = default_filename

    slugified_hostname = slugify(splited_url.hostname)
    slugified_path = slugify(path)

    return '-'.join([slugified_hostname, slugified_path, filename])
