import os
from codecs import open

from setuptools import setup, find_packages


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION = __import__('ultimatethumb').__version__


with open(os.path.join(BASE_DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='django-ultimatethumb',
    version=VERSION,
    description='Generate thumbnails of anything.',
    long_description=long_description,
    url='https://github.com/moccu/django-ultimatethumb',
    project_urls={
        'Bug Reports': 'https://github.com/moccu/django-ultimatethumb/issues',
        'Source': 'https://github.com/moccu/django-ultimatethumb',
    },
    author='Moccu GmbH & Co. KG',
    author_email='info@moccu.com',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=['Pillow', 'command-executor'],
    include_package_data=True,
    keywords='django thumbnails imaging',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
