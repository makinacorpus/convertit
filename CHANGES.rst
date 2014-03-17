=========
CHANGELOG
=========

1.0.1 (unreleased)
------------------

- Add {X_FORWARDED_FOR} placeholder in GET url parameter. Replaced by the
  corresponding header if available.
  It avoids the client initiating the request to be aware of its own address.
  Exemple::

      curl "http://convertit/?url=http://{X_FORWARDED_FOR}/document.odt&to=application/pdf"

1.0 (2013-09-03)
----------------

-  Initial working version
