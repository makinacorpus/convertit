import importlib
import json
import logging
import os
import urllib
import urllib.error
import urllib.parse
import urllib.request
from functools import partial
from mimetypes import guess_extension
from uuid import uuid4

import magic
from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve as static_serve

from convertit import create_dir
from convertit.helpers import (
    download_file,
    remove_files_older_than,
    render_converted_name,
)

seconds_in_hour = 3600
log = logging.getLogger(__name__)

MIMETYPE_LABELS = {
    'application/vnd.oasis.opendocument.text': 'Document OpenDocument (.odt)',
    'application/vnd.oasis.opendocument.spreadsheet': (
        'Feuille de calcul OpenDocument (.ods)'
    ),
    'plain/text': 'Texte / CSV (.csv, .txt)',
    'image/svg+xml': 'Image vectorielle SVG (.svg)',
    'application/pdf': 'Document PDF (.pdf)',
    'application/msword': 'Document Word (.doc)',
    'application/vnd.ms-excel': 'Feuille de calcul Excel (.xls)',
    'image/png': 'Image PNG (.png)',
}

EXTENSION_TO_MIMETYPE = {
    '.odt': 'application/vnd.oasis.opendocument.text',
    '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
    '.csv': 'plain/text',
    '.txt': 'plain/text',
    '.svg': 'image/svg+xml',
}


class ConvertitHttpException(Exception):
    def __init__(self, body, status=400, content_type='text/plain'):
        super().__init__(body)
        self.body = body
        self.status = status
        self.content_type = content_type

    def to_response(self):
        return HttpResponse(
            self.body, status=self.status, content_type=self.content_type
        )


def remove_old_files(request=None):
    downloads_path = settings.CONVERTIT_DOWNLOADS_PATH
    converted_path = settings.CONVERTIT_CONVERTED_PATH

    downloads_max_age = getattr(
        settings, 'CONVERTIT_DOWNLOADS_MAX_AGE', seconds_in_hour
    )
    converted_max_age = getattr(
        settings, 'CONVERTIT_CONVERTED_MAX_AGE', seconds_in_hour
    )

    if os.path.exists(downloads_path):
        remove_files_older_than(int(downloads_max_age), downloads_path)
    if os.path.exists(converted_path):
        remove_files_older_than(int(converted_max_age), converted_path)


def save(request, uploaded_file):
    downloads_path = settings.CONVERTIT_DOWNLOADS_PATH
    create_dir(downloads_path)
    filename = getattr(uploaded_file, 'name', None) or getattr(
        uploaded_file, 'filename', None
    )
    target_name = os.path.basename(filename) if filename else str(uuid4())
    target_file = os.path.join(downloads_path, target_name)
    with open(target_file, 'wb') as f:
        f.write(uploaded_file.read())
    return target_file


def download(request, url):
    downloads_path = settings.CONVERTIT_DOWNLOADS_PATH

    message_template = (
        "Sorry, there was an error fetching the document '{url}'. Reason: {e}"
    )
    try:
        downloaded_filepath = download_file(
            url, downloads_path, headers=request.headers
        )
        return downloaded_filepath
    except ValueError as e:
        message = message_template.format(url=url, e=str(e))
        log.error(message)
        raise ConvertitHttpException(
            body=message, status=400, content_type='text/plain'
        )
    except urllib.error.HTTPError as e:
        message = message_template.format(url=url, e=str(e))
        log.error(message)
        raise ConvertitHttpException(
            body=message, status=e.getcode(), content_type='text/plain'
        )
    except urllib.error.URLError as e:
        message = message_template.format(url=url, e=str(e))
        log.error(message)
        raise ConvertitHttpException(
            body=message, status=400, content_type='text/plain'
        )


def get_input_mimetype(request, input_filepath):
    guessed_mimetype = magic.from_file(input_filepath, mime=True)
    input_mimetype = (
        request.GET.get('from')
        or request.POST.get('from')
        or guessed_mimetype
    )

    if not input_mimetype:
        log.error('Can not guess mimetype')
        raise ConvertitHttpException(
            body='Can not guess mimetype', status=400, content_type='text/plain'
        )

    return input_mimetype


def get_converters():
    converters = {}
    converter_settings = settings.CONVERTIT_CONVERTERS
    if isinstance(converter_settings, str):
        namespaces = converter_settings.split()
    else:
        namespaces = converter_settings
    for namespace in namespaces:
        package = importlib.import_module(namespace)
        converters.update(package.converters())
    return converters


def get_converter(request, input_mimetype, output_mimetype):
    converters = get_converters()

    if (input_mimetype, output_mimetype) not in converters:
        message = 'Unsupported transform: from %s to %s'
        log.error(message % (input_mimetype, output_mimetype))
        raise ConvertitHttpException(
            body=message % (input_mimetype, output_mimetype),
            status=400,
            content_type='text/plain',
        )

    return converters[(input_mimetype, output_mimetype)]


def output_basename_from_url(request, mimetype, url):
    name_template = settings.CONVERTIT_CONVERTED_NAME
    extension = guess_extension(mimetype)
    try:
        # if url has a correct filename, se it
        parse = urllib.parse.urlparse(url)
        basename = os.path.basename(parse.path)
        if '.' in basename:
            return os.path.splitext(basename)[0] + extension

    except Exception:
        pass

    return render_converted_name(name_template, url, extension)


def get_client_addr(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR') or request.headers.get(
        'x-forwarded-for'
    )
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def build_converted_url(request, output_basename):
    converted_url = settings.CONVERTIT_CONVERTED_URL
    if converted_url.startswith(('http://', 'https://')):
        return f"{converted_url.rstrip('/')}/{output_basename}"
    url_prefix = converted_url.strip('/')
    path = (
        f"/{url_prefix}/{output_basename}"
        if url_prefix
        else f"/{output_basename}"
    )
    return request.build_absolute_uri(path)


@csrf_exempt
def home(request):
    create_dir(settings.CONVERTIT_CONVERTED_PATH)
    create_dir(settings.CONVERTIT_DOWNLOADS_PATH)
    try:
        if request.method == 'GET':
            return home_get_view(request)
        elif request.method == 'POST':
            return home_post_view(request)
        return HttpResponseNotAllowed(['GET', 'POST'])
    except ConvertitHttpException as e:
        return e.to_response()


def home_get_view(request):
    url = request.GET.get('url')
    if url is None:
        log.error('Missing parameter: url')
        return HttpResponseBadRequest(
            'Missing parameter: url', content_type='text/plain'
        )

    if '{X_FORWARDED_FOR}' in url:
        url = url.replace('{X_FORWARDED_FOR}', get_client_addr(request))

    input_filepath = download(request, url)
    output_basename_generator = partial(output_basename_from_url, url=url)

    return home_view(request, input_filepath, output_basename_generator)


def home_post_view(request):
    uploaded = request.FILES.get('file')
    if uploaded is None:
        log.error('Missing parameter: file')
        return HttpResponseBadRequest(
            'Missing parameter: file', content_type='text/plain'
        )
    input_filepath = save(request, uploaded)

    filename = os.path.splitext(uploaded.name)[0]

    def output_basename_generator(request, mimetype):
        extension = guess_extension(mimetype)
        return '%s%s' % (filename, extension)

    return home_view(request, input_filepath, output_basename_generator)


def home_view(request, input_filepath, output_basename_generator):
    converted_path = settings.CONVERTIT_CONVERTED_PATH

    input_mimetype = get_input_mimetype(request, input_filepath)

    output_mimetype = (
        request.GET.get('to')
        or request.POST.get('to')
        or 'application/pdf'
    )
    output_basename = output_basename_generator(request, output_mimetype)
    output_filepath = os.path.join(converted_path, output_basename)

    remove_old_files(request)
    log.error(
        f"from: {input_mimetype} to {output_mimetype}, file: {output_filepath}"
    )
    convert = get_converter(request, input_mimetype, output_mimetype)

    try:
        convert(input_filepath, converted_path)
        log.error(f"converted: {input_filepath} to {converted_path}")
    except Exception as e:
        msg = "Sorry, there was an error converting the document. Reason: %s"
        log.error(msg % str(e))
        return HttpResponseServerError(msg % str(e), content_type='text/plain')

    response = HttpResponseRedirect(
        build_converted_url(request, output_basename)
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % output_basename
    return response


def get_available_conversions():
    conversions = []
    for input_mime, output_mime in get_converters().keys():
        conversions.append(
            {
                'from': input_mime,
                'from_label': MIMETYPE_LABELS.get(input_mime, input_mime),
                'to': output_mime,
                'to_label': MIMETYPE_LABELS.get(output_mime, output_mime),
            }
        )
    return conversions


def ui_view(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    conversions = get_available_conversions()
    context = {
        'conversions': conversions,
        'conversions_json': json.dumps(conversions),
        'extension_map_json': json.dumps(EXTENSION_TO_MIMETYPE),
        'accepted_extensions': ','.join(EXTENSION_TO_MIMETYPE.keys()),
    }
    return render(request, 'ui.html', context)


def serve_converted(request, path):
    response = static_serve(
        request, path, document_root=settings.CONVERTIT_CONVERTED_PATH
    )
    response['Cache-Control'] = f'max-age={seconds_in_hour}'
    return response


def serve_static(request, path):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    response = static_serve(request, path, document_root=static_dir)
    response['Cache-Control'] = f'max-age={seconds_in_hour}'
    return response
