import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst'), encoding='utf-8').read()
CHANGES = open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8').read()

requires = [
    'pyramid<=1.10.5',
    'gunicorn',
    'python-magic',
    'Pillow',
]

test_requires = requires + [
    'webtest',
    'mock',
    'coverage',
    'freezegun',
]


setup(name='convertit',
      version='2.2.5.dev0',
      description='A file conversion Web API in Pyramid',
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
      keywords='web pyramid webservice convert',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={
          'test': test_requires,
      },
      test_suite="convertit",
      entry_points="""\
      [paste.app_factory]
      main = convertit:main
      """,
      )
