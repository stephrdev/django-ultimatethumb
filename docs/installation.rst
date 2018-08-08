Installation
============

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
