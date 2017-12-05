Changelog
=========

0.8.0 - 2017-12-05
------------------

* Add support for base64 output of thumbnails

0.7.0 - 2017-11-03
------------------

* Fixed thumbnail size when cropping with exact target sizes
* Added support for Django 1.11

0.6.0 - 2017-07-31
------------------

* Added viewport support to pass viewport max-width/max-height in addition to size
* Added support for crop gravity ("crop" now accepts True (fallback to "Center")
  or a gravity orientation according to the GraphicsMagick documentation)

0.5.0 - 2017-02-14
------------------

* Fix bug when using static: sources in DEBUG=False and not using django-compressor
* Drop support for Django <1.8

0.4.1 - 2016-05-04
------------------

* Added support for Django 1.9

0.3.0 - 2015-11-03
------------------

* Added pngquant support
* Bugfix for retina / factor2x mode
* Improved option passing in templatetag.

0.2.0 - 2015-10-20
------------------

* Added domain support to allow serving of thumbnails from a different domain
* Fixed handling of staticfiles when using CachedStaticFilesStorage
* Bugfix for path quoting
* Added Django 1.8 support

0.1.0 - 2015-03-24
------------------

* Initial release.
