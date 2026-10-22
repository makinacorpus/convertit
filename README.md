<img src="convertit/static/img/convertit_logo_light.png" alt="Convertit" style="max-width: 200px; height: auto;">

**Convertit** is a format conversion webservice.

Retrieve your document in an other format ! The input file is converted and served back !
Using a dead simple `GET` request, documents are pulled. Using `POST` request, it takes the attachment.

[![CI](https://github.com/makinacorpus/convertit/actions/workflows/ci.yml/badge.svg)](https://github.com/makinacorpus/convertit/actions/workflows/ci.yml)

Supported conversions:

- odt -> pdf
- odt -> doc
- ods -> xls
- csv -> ods
- csv -> xls
- svg -> pdf
- svg -> png

Previously converted documents are cleaned along the way (on each request).

## USAGE

### Using GET request

Example, convert from *odt* to *pdf* :

```bash
curl http://convertit/?url=http://server/document.odt&to=application/pdf
HTTP/1.1 302 Found
Content-Disposition: attachment; filename=document.pdf
...
```

GET parameters:

**url**: absolute url of the document to be converted.

"url" also supports a "{X_FORWARDED_FOR}" placeholder for requests not knowing
their own host. "{X_FORWARDED_FOR}" will be replaced with the corresponding
"X_FORWARDED_FOR" header if available. Be warned that "X_FORWARDED_FOR" is not
a safe value since it can be modified by user agents or given false value by
forward proxies. Use only if really needed. Exemple:

```bash
curl "http://convertit/?url=http://{X_FORWARDED_FOR}/document.odt&to=application/pdf"
```

### Using POST request

Upload data in POST parameter named `file`:

```bash
curl -F "file=@tiger.svg" http://convertit/?to=image/png
HTTP/1.1 302 Found
Content-Disposition: attachment; filename=tiger.png
```

### Query parameters

- **to**: output mimetype (optionnal, default to `application/pdf` if not provided);
- **from**: input mimetype (optionnal, guessed from input url or file if not provided).

## INSTALL

### System dependencies

- for *OpenDocument* support: `libreoffice-writer-nogui`, `libreoffice-calc-nogui`
- for *SVG* support: `libcairo2` (used by `CairoSVG`)

Conversion binaries should be in system `PATH` (`which` is used internally.)

### Download

- Download and extract a released tarball from [pypi](http://pypi.python.org/pypi/convertit)
- The bleeding edge version is hosted on [github](https://github.com/makinacorpus/convertit):

```bash
git clone https://github.com/makinacorpus/convertit.git
cd convertit
```

### Development

```bash
make serve
```

Once the application is running, you may visit http://localhost:6543/ in your browser.

Run tests:

```bash
make tests
```

### Production

Using *gunicorn* for example :

```bash
gunicorn --workers=1 -c python:convertit.gunicorn_conf convertit.wsgi:application
```

Using Docker :

```bash
sudo docker build -t="convertit" .
sudo docker run -p :6543 convertit
```

### Feedback

Open [an issue](https://github.com/makinacorpus/convertit/issues) to report a
bug or request a new feature.

## CREDITS

### Companies

[![makinacom](https://github.com/makinacorpus.png)](https://www.makina-corpus.com)

* [Planet Makina Corpus](https://www.makina-corpus.com)
* [Contact us](mailto:python@makina-corpus.com)

### Authors

- Antoine Cezar
- Alex Marandon

### Contributors

- kiorky <kiorky@cryptelium.net>
- Mathieu Leplatre <mathieu.leplatre@makina-corpus.com>
- Gaël Utard <gael.utard@makina-corpus.com>
- Jean-Etienne Castagnede <j.e.castagnede@gmail.com>
