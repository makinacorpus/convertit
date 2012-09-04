import os
import urllib2
from uuid import uuid4


def download_file(url, target_dir):
    _, ext = os.path.splitext(url)
    data = urllib2.urlopen(url).read()
    filename = "%s%s" % (uuid4(), ext)
    target_file = os.path.join(target_dir, filename)
    with open(target_file, 'w') as f:
        f.write(data)
    return target_file
