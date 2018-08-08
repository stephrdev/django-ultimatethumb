Usage
=====

To use `django-ultimatethumb` in your templates, just load the templatetags and
call the ``ultimatethumb`` tag with proper parameters:

.. code-block:: text

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
