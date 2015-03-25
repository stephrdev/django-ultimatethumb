#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'django-ultimatethumb'
copyright = '2015, Moccu GmbH & Co. KG'
version = '0.1.0'
release = '0.1.0'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'default'
# html_static_path = ['_static']
htmlhelp_basename = 'ultimatethumbdoc'
latex_documents = [(
    'index', 'ultimatethumb.tex', 'django-ultimatethumb Documentation',
    'Moccu GmbH & Co. KG', 'manual'
)]
man_pages = [(
    'index', 'ultimatethumb', 'django-ultimatethumb Documentation',
    ['Moccu GmbH & Co. KG'], 1
)]
texinfo_documents = [(
    'index', 'ultimatethumb', 'django-ultimatethumb Documentation',
    'Moccu GmbH & Co. KG', 'django-ultimatethumb', 'Generate thumbnails of anything.',
    'Miscellaneous'
)]
intersphinx_mapping = {'http://docs.python.org/': None}

# Ugly hack to provide some sane Django settings for autodoc.
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'django.conf.project_template.project_name.settings'
)
from django.conf import settings
settings.ULTIMATETHUMB_ROOT = '/docs/'
settings.ULTIMATETHUMB_URL = '/docs/'
