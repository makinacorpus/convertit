import os
import urllib2
import logging
from functools import partial
from mimetypes import guess_extension
from uuid import uuid4

import magic
from pyramid.httpexceptions import (
    HTTPError,
    HTTPBadRequest,
    HTTPFound,
    HTTPInternalServerError,
)
from pyramid.url import static_url
from pyramid.view import view_config

from convertit.helpers import (
    download_file,
    remove_files_older_than,
    render_converted_name,
)


seconds_in_hour = 3600
log = logging.getLogger(__name__)


def remove_old_files(request):
    settings = request.registry.settings

    downloads_path = settings['convertit.downloads_path']
    converted_path = settings['convertit.converted_path']

    downloads_max_age = settings.get('convertit.downloads_max_age',
                                     seconds_in_hour)
    converted_max_age = settings.get('convertit.converted_max_age',
                                     seconds_in_hour)

    remove_files_older_than(int(downloads_max_age), downloads_path)
    remove_files_older_than(int(converted_max_age), converted_path)


def save(request, uploaded_file):
    downloads_path = request.registry.settings['convertit.downloads_path']
    target_file = os.path.join(downloads_path, str(uuid4()))
    with open(target_file, 'w') as f:
        f.write(uploaded_file.read())
    return target_file


def download(request, url):
    downloads_path = request.registry.settings['convertit.downloads_path']

    message = "Sorry, there was an error fetching the document. Reason: %s"
    try:
        downloaded_filepath = download_file(url,
                                            downloads_path,
                                            headers=request.headers)
        return downloaded_filepath
    except ValueError as e:
        log.error(message % str(e))
        raise HTTPBadRequest(body=message % str(e), content_type='text/plain')
    except urllib2.HTTPError as e:
        log.error(message % str(e))
        raise HTTPError(body=message % str(e), status_int=e.getcode(),
                        content_type='text/plain')
    except urllib2.URLError as e:
        log.error(message % str(e))
        raise HTTPBadRequest(body=message % str(e), content_type='text/plain')


def get_input_mimetype(request, input_filepath):
    guessed_mimetype = magic.from_file(input_filepath, mime=True)
    input_mimetype = request.GET.get('from', guessed_mimetype)

    if not input_mimetype:
        log.error('Can not guess mimetype')
        raise HTTPBadRequest(body='Can not guess mimetype',
                             content_type='text/plain')

    return input_mimetype


def get_converter(request, input_mimetype, output_mimetype):
    converters = request.registry.convertit

    if (input_mimetype, output_mimetype) not in converters:
        message = 'Unsupported transform: from %s to %s'
        log.error(message % (input_mimetype, output_mimetype))
        raise HTTPBadRequest(body=message % (input_mimetype, output_mimetype),
                             content_type='text/plain')

    return converters[(input_mimetype, output_mimetype)]


def output_basename_from_url(request, mimetype, url):
    settings = request.registry.settings
    name_template = settings['convertit.converted_name']
    extension = guess_extension(mimetype)
    return render_converted_name(name_template, url, extension)


@view_config(route_name='home', request_method='GET')
def home_get_view(request):
    url = request.GET.get('url')
    if url is None:
        log.error('Missing parameter: url')
        return HTTPBadRequest(body='Missing parameter: url',
                              content_type='text/plain')

    if '{X_FORWARDED_FOR}' in url:
        url = url.replace('{X_FORWARDED_FOR}', request.client_addr)

    input_filepath = download(request, url)
    output_basename_generator = partial(output_basename_from_url, url=url)

    return home_view(request, input_filepath, output_basename_generator)


@view_config(route_name='home', request_method='POST')
def home_post_view(request):
    uploaded = request.POST.get('file')
    input_filepath = save(request, uploaded.file)

    filename = os.path.splitext(uploaded.filename)[0]

    def output_basename_generator(request, mimetype):
        extension = guess_extension(mimetype)
        return '%s%s' % (filename, extension)

    return home_view(request, input_filepath, output_basename_generator)


def home_view(request, input_filepath, output_basename_generator):
    settings = request.registry.settings
    converted_path = settings['convertit.converted_path']

    input_mimetype = get_input_mimetype(request, input_filepath)

    output_mimetype = request.GET.get('to', 'application/pdf')
    output_basename = output_basename_generator(request, output_mimetype)
    output_filepath = os.path.join(converted_path, output_basename)

    remove_old_files(request)

    convert = get_converter(request, input_mimetype, output_mimetype)

    try:
        convert(input_filepath, output_filepath)
    except Exception as e:
        message = "Sorry, there was an error converting the document. Reason: %s"
        log.error(message %  str(e))
        return HTTPInternalServerError(body=message % str(e),
                                       content_type='text/plain')

    return HTTPFound(static_url(output_filepath, request),
                     content_disposition='attachement; filename=%s' %
                     output_basename)
