#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import sys

from setuptools import find_packages, setup


version = '0.5.0'


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    print('You probably want to also tag the version now:')
    print('  git tag -a %s -m "version %s"' % (version, version))
    print('  git push --tags')
    sys.exit()


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


tests_require = [
    'tox',
    'tox-pyenv',
    'coverage',
    'mock',
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-flakes',
    'pytest-isort',
    'pytest-django',
    'python-coveralls',
    'factory-boy',
]


setup(
    name='django-ultimatethumb',
    description='Generate thumbnails of anything.',
    long_description=read('README.rst'),
    version=version,
    license='BSD',
    author='Moccu GmbH & Co. KG',
    author_email='info@moccu.com',
    url='http://github.com/moccu/django-ultimatethumb/',
    packages=find_packages(exclude=[
        'ultimatethumb.tests',
        'ultimatethumb.tests.factories',
        'ultimatethumb.tests.resources',
        'ultimatethumb.tests.resources.mockapp',
    ]),
    test_suite='.',
    tests_require=tests_require,
    install_requires=[
        'Django>=1.8,<1.10',
        'barbeque>=1.4',
        'Pillow',
    ],
    extras_require={
        'tests': tests_require,
        'docs': ['sphinx'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: Django',
    ],
)
