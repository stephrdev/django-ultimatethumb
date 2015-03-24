Welcome to django-ultimatethumb's documentation!
================================================

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


.. toctree::
   :maxdepth: 2

   reference/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
