import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst'), encoding='utf-8').read()
VERSION = open(os.path.join(here, 'VERSION'), encoding='utf-8').read().strip()

setup(name='convertit',
      version=VERSION,
      description='A file conversion Web API in Pyramid',
      long_description=README,
      license='AGPLV3',
      classifiers=[
          "License :: OSI Approved :: GNU Affero General Public License v3",
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Makina Corpus',
      author_email='python@makina-corpus.org',
      url='https://github.com/makinacorpus/convertit',
      keywords='web pyramid webservice convert',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite="convertit",
      entry_points="""\
      [paste.app_factory]
      main = convertit:main
      """,
      install_requires=[
          "pyramid",
            "python-magic",
            "Pillow",
            "gunicorn"
      ]
      )
