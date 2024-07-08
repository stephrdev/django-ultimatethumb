django-ultimatethumb
=======================

.. image:: https://img.shields.io/pypi/v/django-ultimatethumb.svg
   :target: https://pypi.org/project/django-ultimatethumb/
   :alt: Latest Version

.. image:: https://codecov.io/gh/stephrdev/django-ultimatethumb/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stephrdev/django-ultimatethumb
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/django-ultimatethumb/badge/?version=latest
   :target: https://django-ultimatethumb.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/stephrdev/django-ultimatethumb.svg?branch=master
   :target: https://travis-ci.org/stephrdev/django-ultimatethumb


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

django-ultimatethumb supports Python 3 only and requires at least Django 2.2.


Prepare for development
-----------------------

A Python 3.6 interpreter is required in addition to pipenv.

.. code-block:: shell

    $ poetry install


Now you're ready to run the tests:

.. code-block:: shell

    $ make tests


Resources
---------

* `Documentation <https://django-ultimatethumb.readthedocs.io/en/latest/>`_
* `Bug Tracker <https://github.com/stephrdev/django-ultimatethumb/issues>`_
* `Code <https://github.com/stephrdev/django-ultimatethumb/>`_
