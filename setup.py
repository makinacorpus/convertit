import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()
VERSION = open(os.path.join(here, 'convertit', 'VERSION'), encoding='utf-8').read().strip().replace('~', '.')

setup(
    name='convertit',
    version=VERSION,
    description='A file conversion Web API in Django',
    long_description=README,
    long_description_content_type='text/markdown',
    license='AGPLV3',
    classifiers=[
      "License :: OSI Approved :: GNU Affero General Public License v3",
      "Programming Language :: Python",
      "Framework :: Django",
      "Framework :: Django :: 5.2",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Makina Corpus',
    author_email='python@makina-corpus.org',
    url='https://github.com/makinacorpus/convertit',
    keywords='web django webservice convert',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="convertit",
    install_requires=[
      "Django>=5.2,<5.3",
      "python-magic",
      "Pillow",
      "gunicorn",
      "CairoSVG",
    ]
)
