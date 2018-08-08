django-ultimatethumb
=======================

.. image:: https://img.shields.io/pypi/v/django-ultimatethumb.svg
   :target: https://pypi.org/project/django-ultimatethumb/
   :alt: Latest Version

.. image:: https://codecov.io/gh/moccu/django-ultimatethumb/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/moccu/django-ultimatethumb
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/django-ultimatethumb/badge/?version=latest
   :target: https://django-ultimatethumb.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/moccu/django-ultimatethumb.svg?branch=master
   :target: https://travis-ci.org/moccu/django-ultimatethumb


`django-ultimatethumb` is another Django library for generating thumbnails but
has some advantages:

* Thumbnails are not generated when the templatetag is called. Instead, images
  are generated on demand when they are requested by the browser. This can
  lead to a major speedup of your page response times.
* Thumbnails can be generated from static files too (for example to downscale
  retina-optimized images and therefore reducing traffic).
* Generate multiple thumbnail sizes at once for use in `picture` html tags with
  multiple sources (e.g. with media queries).


Requirements
------------

django-ultimatethumb supports Python 3 only and requires at least Django 1.11.


Prepare for development
-----------------------

A Python 3.6 interpreter is required in addition to pipenv.

.. code-block:: shell

    $ pipenv install --python 3.6 --dev
    $ pipenv shell
    $ pip install -e .


Now you're ready to run the tests:

.. code-block:: shell

    $ pipenv run py.test


Resources
---------

* `Documentation <https://django-ultimatethumb.readthedocs.org/>`_
* `Bug Tracker <https://github.com/moccu/django-ultimatethumb/issues>`_
* `Code <https://github.com/moccu/django-ultimatethumb/>`_
