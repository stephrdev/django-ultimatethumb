#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
from setuptools import setup, find_packages


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


tests_require = [
    'coverage',
    'mock',
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-flakes',
    'pytest-django',
    'python-coveralls',
    'factory-boy',
    'Pillow',
]


setup(
    name='django-ultimatethumb',
    description='Generate thumbnails of anything.',
    long_description=read('README.rst') + u'\n\n' + read('CHANGELOG.rst'),
    version='0.1.0',
    license='BSD',
    author='Moccu GmbH & Co. KG',
    author_email='info@moccu.com',
    url='http://github.com/moccu/django-ultimatethumb/',
    packages=find_packages(exclude=['ultimatethumb.tests']),
    test_suite='.',
    tests_require=tests_require,
    install_requires=[
        'Django>=1.6,<1.8',
        'barbeque>=0.2.1'
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
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django',
    ],
)
