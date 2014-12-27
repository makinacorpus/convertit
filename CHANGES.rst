=========
CHANGELOG
=========

1.1.2 (unreleased)
------------------

- Fix crash in unoconv error handling


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
