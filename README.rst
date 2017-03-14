django-ultimatethumb
====================

.. image:: https://badge.fury.io/py/django-ultimatethumb.png
    :target: http://badge.fury.io/py/django-ultimatethumb

.. image:: https://travis-ci.org/moccu/django-ultimatethumb.svg?branch=master
    :target: https://travis-ci.org/moccu/django-ultimatethumb

.. image:: https://coveralls.io/repos/moccu/django-ultimatethumb/badge.svg
    :target: https://coveralls.io/r/moccu/django-ultimatethumb

.. image:: https://readthedocs.org/projects/django-ultimatethumb/badge/?version=latest
    :target: https://readthedocs.org/projects/django-ultimatethumb/?badge=latest


What is django-ultimatethumb
----------------------------

`django-ultimatethumb` is another Django library for generating thumbnails but
has some advantages:

* Thumbnails are not generated when the templatetag is called. Instead, images
  are generated on demand when they are requested by the browser. This can
  lead to a major speedup of your page response times.
* Thumbnails can be generated from static files too (for example to downscale
  retina-optimized images and therefore reducing traffic).
* Generate multiple thumbnail sizes at once for use in `picture` html tags with
  multiple sources (e.g. with media queries).


.. hint::

    The documentation is still work in progress but the library is already in use
    for a while now. We working hard on providing a better documentation!


Quick start
-----------

To install `django-ultimatethumb` just use your preferred Python package installer::

    $ pip install django-ultimatethumb

Add some stuff  to your Django settings

.. code-block:: python

    INSTALLED_APPS = (
        # some other apps
        'ultimatethumb',
    )

    # This is the path where the generated thumbnail files are cached.
    ULTIMATETHUMB_ROOT = '/filesystem/path/to/thumbnails/'
    # This is the base url for your thumbnails
    ULTIMATETHUMB_URL = '/thumbnails/'

Next, add the `django-ultimatethumb` urls to your ``urls.py``

.. code-block:: python

    urlpatterns += patterns(
        '',
        url(
            r'^{0}/'.format(settings.ULTIMATETHUMB_URL.strip('/')),
            include('ultimatethumb.urls')
        ),

.. hint::

    You can use the ``ULTIMATETHUMB_URL`` setting in your ``urls.py`` to make
    sure that the urls are in sync.

To use `django-ultimatethumb` in your templates, just load the templatetags and
call the ``ultimatethumb`` tag with proper parameters:

.. code-block:: html

    {% load ultimatethumb_tags %}
    {% ultimatethumb 'mythumb' mymodel.imagefield.name sizes='200x0,400x0' %}
    <picture>
    {% for source in mythumb %}
        <source
            srcset="{{ source.url_2x }} 2x, {{ source.url }} 1x"
            {% if not forloop.last %}media="(max-width: {{ source.viewport.width }}px)"{% endif %}
        />
        {% if forloop.last %}<img src="{{ source.url }}" />{% endif %}
    {% endfor %}
    </picture>

This gives you a full-featured picture tag including multiple sources with
media queries for different browser sizes and also provides retina images.

You can also use `django-ultimatethumb` in a much simpler way:

.. code-block:: html

    {% load ultimatethumb_tags %}
    {% ultimatethumb 'mythumb' mymodel.imagefield.name sizes='400x0' %}
    <img src="{{ mythumb.0.url }}" />

To resize static images, just prefix the path with ``static:``, for example:

.. code-block:: html

    {% load ultimatethumb_tags %}
    {% ultimatethumb 'mythumb' 'static:img/logo.jpg' sizes='400x0' %}
    <img src="{{ mythumb.0.url }}" />

There are many other options/parameters to pass to the templatetag. Please refer
to the codebase until the documentation is more complete.

You can also pass the viewport size in addition to the requested thumbnail size:

.. code-block:: html

    {% load ultimatethumb_tags %}
    {% ultimatethumb 'mythumb' 'static:img/logo.jpg' sizes='400x0:600x0' %}
    <img src="{{ mythumb.0.url }}" />

This will set the `thumbnail.viewport.width` to 600.

If you want so save some characters, you might short cut the sizes by leaving out
the "x0" for the auto'ed dimesion.

.. code-block:: html

    {% load ultimatethumb_tags %}
    {% ultimatethumb 'mythumb' 'static:img/logo.jpg' sizes='400:600' %}
    <img src="{{ mythumb.0.url }}" />

The sizes are now the same as if you would use sizes='400x0,600x0'.


Options
-------

You can pass some options to the thumbnail tag:

* upscale: Configures if the input should be upscaled if requested sizes are larger than source.
* retina: Option to enable retina support (by providing both url and url_2x)
* crop: Deside if images should be cropped if requested sizes doesn't fit source aspect ratio.
* quality: Configures quality for image compression
* pngquant: Configures the pngquant compression factor

.. hint::

    The `crop` option can be set to True for default gravity when cropping (which is `Center`).
    You can also pass valid GraphicsMagick gravities (North, NorthEeast, East, SouthEast, ...)
    or their abbreviation (N, NE, E, SE, ...)
