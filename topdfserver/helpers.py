import os
import re
import urllib2
from unicodedata import normalize
from urlparse import urlsplit
from uuid import uuid4


def download_file(url, target_dir):
    _, ext = os.path.splitext(url)
    data = urllib2.urlopen(url).read()
    filename = "%s%s" % (uuid4(), ext)
    target_file = os.path.join(target_dir, filename)
    with open(target_file, 'w') as f:
        f.write(data)
    return target_file


# Credit: http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def url_to_filename(url):
    splited_url = urlsplit(url)

    parts = [slugify(splited_url.hostname)]

    if splited_url.path[-1] == '/':
        path = splited_url.path[:-1]
    else:
        path, ext = os.path.splitext(splited_url.path)

    parts.append(slugify(path))

    return '-'.join(parts)
