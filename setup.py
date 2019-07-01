import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = ['Flask==1.0.3', 'gunicorn==19.0.0', 'WeasyPrint==47']


setup(
    name='convertit',
    version='1.1.5',
    description='A PDF conversion Web API using flask.',
    long_description=README + '\n\n' + CHANGES,
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
    keywords='web flask webservice convert',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
