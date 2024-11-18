import os

from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst'), encoding='utf-8').read()
CHANGES = open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8').read()

install_reqs = parse_requirements('./requirements.txt', session=PipSession())

reqs = [str(ir.req) for ir in install_reqs]

test_reqs = reqs + [str(ir.req) for ir in parse_requirements('./dev-requirements.txt', session=PipSession())]


setup(name='convertit',
      version='2.2.6.dev0',
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
      #install_requires=reqs,
      tests_require=test_requires,
      extras_require={
          'test': test_reqs,
      },
      test_suite="convertit",
      entry_points="""\
      [paste.app_factory]
      main = convertit:main
      """,
      )
