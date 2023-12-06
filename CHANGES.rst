=========
CHANGELOG
=========

2.2.6.dev0
------------------

- Add Ubuntu 22.04 official support with debian package
- Update Docker image to ubuntu 22.04 base
- Use directly libreoffice instead of deprecated unoconv
- Move CI to github-action


2.2.5 (2021-01-13)
------------------

- Fix build convertit


2.2.4 (2021-01-13)
------------------

- Fix binding service


2.2.3 (2020-02-26)
------------------

- Add compatibility Ubuntu 20.04


2.2.2 (2020-02-26)
------------------

- Fix libreoffice conversion


2.2.1 (2020-02-20)
------------------

- Fix Dockerfile for Python 3
- Ubuntu packaging


2.2.0 (2019-11-22)
------------------

- Move from Python 2 to Python 3


1.1.5 (2015-04-01)
------------------

- Fix systematic crash in unoconv converter


1.1.4 (2015-04-01)
------------------

- Serialize parallel libreoffice conversions with flock instead of celery


1.1.3 (2015-01-20)
------------------

- Serialize parallel libreoffice conversions


1.1.2 (2014-12-30)
------------------

- Fix a crash in unoconv error handling
- Log errors
- Add a warning about unoconv not able to work in parallel


1.1.1 (2014-12-18)
------------------

- Send HTTP errors as raw strings instead of HTML documents


1.1.0 (2014-05-21)
------------------

- Use original request header ``Accept-language`` to download the URL

- Add {X_FORWARDED_FOR} placeholder in GET url parameter. Replaced by the
  corresponding header if available.
  It avoids the client initiating the request to be aware of its own address.
  Exemple::

      curl "http://convertit/?url=http://{X_FORWARDED_FOR}/document.odt&to=application/pdf"

1.0 (2013-09-03)
----------------

-  Initial working version
