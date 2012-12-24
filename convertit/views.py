import os
import urllib2
from mimetypes import guess_type

from pyramid.view import view_config
from pyramid.url import static_url
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound,
)
from pyramid.response import Response
from convertit.helpers import (
    download_file,
    url_to_filename,
    remove_files_older_than
)

from convertit import CONVERTERS as converters


seconds_in_hour = 3600


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


@view_config(route_name='home')
def home_view(request):
    converted_path = request.registry.settings['convertit.converted_path']
    downloads_path = request.registry.settings['convertit.downloads_path']

    remove_old_files(request)

    url = request.GET.get('url')
    output_mt = request.GET.get('to', 'application/pdf')

    if url is None:
        return HTTPBadRequest('Missing parameter: url')

    guessed_mimetype, _ = guess_type(url)
    mimetype = request.GET.get('from', guessed_mimetype)
    if not mimetype:
        return HTTPBadRequest('Can not guess mimetype')

    try:
        transform = converters.get_transform(mimetype, output_mt)
    except Exception as e:
        return HTTPBadRequest(
            'Unsupported transform: %s for mimetype %s (url: %s)' % (
                output_mt,
                mimetype,
                url,
            )
        )

    base_error_msg = "Sorry, there was an error fetching the document."
    try:
        downloaded_filepath = download_file(url, downloads_path)
    except ValueError as e:
        return HTTPBadRequest(base_error_msg + " Reason: %s" % e.message)
    except urllib2.HTTPError as e:
        return Response(base_error_msg + " Reason: %s" % e.reason,
                        status_int=e.getcode())
    except urllib2.URLError as e:
        return HTTPBadRequest(base_error_msg + " Reason: %s" % e.reason)

    downloaded_basename = os.path.basename(downloaded_filepath)
    downloaded_filename, _ = os.path.splitext(downloaded_basename)

    converted_filename = url_to_filename(url)
    converted_basename = converted_filename + '.%s' % transform['extension']
    converted_filepath = os.path.join(converted_path, converted_basename)

    try:
        transform['method'](downloaded_filepath, converted_filepath)
    except Exception as e:
        return HTTPBadRequest(base_error_msg + " Reason: %s" % e.message)

    return HTTPFound(static_url(converted_filepath, request),
                     content_disposition='attachement; filename=%s' %
                     converted_basename)
