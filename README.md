Convertit
=========

A conversion webservice

Companies
---------

  * [Planet Makina Corpus](http://www.makina-corpus.org) [Contact us](mailto:python@makina-corpus.org>)

Authors
--------

  * Antoine Cezar
  * Alex Marandon

Feedback
========

Open an [Issue](https://github.com/makinacorpus/convertit/issues) to report a bug or request a new feature.

Dependencies
============

  * for OpenDocument support: unoconv
  * for SVG support: inkscape

Install
=======

  * Throught regular easy_install / buildout:

      ```
      easy_install convertit
      ```

  * The bleeding edge version is hosted on github:

      ```
      git clone https://github.com/makinacorpus/convertit.git
      cd convertit
      python setup.py install
      ```

Development
===========

```
git clone https://github.com/makinacorpus/convertit.git
cd convertit
python setup.py develop
python setup.py test
pserve development.ini --reload
```

Once the application is running, you may visit http://localhost:6543/ in your browser.
