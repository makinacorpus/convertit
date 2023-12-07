import os
import urllib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def download_file(url, target_dir, headers=None):
    url_parsed = urlparse(url)
    file_path = Path(url_parsed.path)

    if headers:
        selection = ['accept-language', 'user-agent']
        selected = dict((k.title(), v) for k, v in headers.items()
                        if k.lower() in selection)
        if selected:
            url = urllib.request.Request(url, headers=selected)

    data = urllib.request.urlopen(url).read()
    target_file = os.path.join(target_dir, file_path.name)
    with open(target_file, 'wb') as f:
        f.write(data)
    return target_file


def remove_files_older_than(limit, path):
    for basename in os.listdir(path):
        target = os.path.join(path, basename)
        target_mtime = os.path.getmtime(target)
        target_datetime = datetime.utcfromtimestamp(target_mtime)
        now_datetime = datetime.utcnow()
        time_delta = now_datetime - target_datetime
        if time_delta.seconds > limit:
            os.remove(target)


def render_converted_name(template, url, extension):
    parsed_url = urllib.parse.urlsplit(url)
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
