from mimetypes import guess_type
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound


def odt_to_pdf(filepath):
    pass


converters = {
    'application/vnd.oasis.opendocument.text': odt_to_pdf
}


@view_config(route_name='home')
def home_view(request):
    url = request.GET.get('url')

    if url is None:
        return HTTPBadRequest('Missing parameter: url')

    mimetype = guess_type(url)[0]

    if mimetype not in converters:
        return HTTPBadRequest('Unsupported mimetype %s' % mimetype)

    filepath = download_file(url)
    converted_filepath = converters[mimetype](filepath)
    converted_file_url = path_to_url(converted_filepath)

    return HTTPFound(converted_file_url)


def download_file(url):
    pass


def path_to_url(filepath):
    pass
