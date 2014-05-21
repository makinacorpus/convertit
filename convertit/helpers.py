import os
import urllib2
from urlparse import urlsplit
from uuid import uuid4
from datetime import datetime


def download_file(url, target_dir, headers=None):
    _, ext = os.path.splitext(url)

    if headers:
        selection = ['accept-language', 'user-agent']
        selected = dict((k.title(), v) for k, v in headers.items()
                        if k.lower() in selection)
        if selected:
            url = urllib2.Request(url, headers=selected)

    data = urllib2.urlopen(url).read()
    filename = "%s%s" % (uuid4(), ext)
    target_file = os.path.join(target_dir, filename)
    with open(target_file, 'w') as f:
        f.write(data)
    return target_file


def remove_files_older_than(limit, path):
    for basename in os.listdir(path):
        target = os.path.join(path, basename)
        target_mtime = os.path.getmtime(target)
        target_datetime = datetime.fromtimestamp(target_mtime)
        now_datetime = datetime.now()
        time_delta = now_datetime - target_datetime
        if time_delta.seconds > limit:
            os.remove(target)


def render_converted_name(template, url, extension):
    parsed_url = urlsplit(url)
    url_dirname = os.path.dirname(parsed_url.path)[1:].replace('/', '_')
    url_basename = os.path.basename(parsed_url.path)
    url_filename, url_extension = os.path.splitext(url_basename)

    data = {
        'url_hostname': parsed_url.hostname,
        'url_port': parsed_url.port,
        'url_dirname': url_dirname,
        'url_filename': url_filename,
        'url_extension': url_extension or '',
        'extension': extension,
    }

    return template.format(**data)
