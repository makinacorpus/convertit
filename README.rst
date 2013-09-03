**Convertit** is a format conversion webservice. 

Retrieve your document in an other format using a dead simple ``GET`` request. 
Documents are pulled, converted and served back !

.. image:: https://secure.travis-ci.org/makinacorpus/convertit.png?branch=master

.. contents::


Supported conversions:
- odt -> pdf
- odt -> doc
- ods -> xls
- csv -> ods
- csv -> xls
- svg -> pdf
- svg -> png

Previously converted documents are cleaned along the way (on each request).


=====
USAGE
=====

Using GET request
-----------------

Example, convert from *odt* to *pdf* :

::

    curl http://convertit/?url=http://server/document.odt&to=application/pdf
    HTTP/1.1 302 Found
    Content-Disposition: attachement; filename=document.pdf
    ...

GET parameters:

**url**: absolute url of the document to be converted;


Using POST request
------------------

Upload data in POST parameter named ``file``:

::

    curl -F "file=@tiger.svg" http://convertit/?to=image/png
    HTTP/1.1 302 Found
    Content-Disposition: attachement; filename=tiger.png



Query parameters
----------------

- **to**: output mimetype (optionnal, default to ``application/pdf`` if not provided); 
- **from**: input mimetype (optionnal, guessed from input url or file if not provided).


=======
INSTALL
=======

System dependencies
-------------------
* for *OpenDocument* support: ``unoconv``
* for *SVG* support: ``inkscape``

Conversion binaries should be in system ``PATH`` (``which`` is used internally.)

Download
---------
* Download and extract a released tarball from `pypi <http://pypi.python.org/pypi/convertit>`_
* The bleeding edge version is hosted on `github <https://github.com/makinacorpus/convertit>`_ ::

    git clone https://github.com/makinacorpus/convertit.git
    cd convertit

Development
-----------

::

    python setup.py develop
    pserve --reload development.ini

Once the application is running, you may visit http://localhost:6543/ in your browser.

Run tests: ::

    python setup.py test


Production
----------

Using *gunicorn* for example :

::

    gunicorn_paster --workers=4 production.ini


Feedback
--------

Open `an issue <https://github.com/makinacorpus/convertit/issues>`_ to report a 
bug or request a new feature.


=======
CREDITS
=======

Companies
---------
|makinacom|_

  * `Planet Makina Corpus <http://www.makina-corpus.org>`_
  * `Contact us <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com

Authors
-------
* Antoine Cezar
* Alex Marandon

Contributors
-------------
* kiorky  <kiorky@cryptelium.net>
* Mathieu Leplatre <mathieu.leplatre@makina-corpus.com>
