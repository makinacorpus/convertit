=========
CHANGELOG
=========

1.1.4.dev (unreleased)
------------------

- 


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
