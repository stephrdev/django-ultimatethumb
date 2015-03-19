#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ultimatethumb.tests.settings')

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'ultimatethumb'
copyright = '2014, Moccu GmbH & Co. KG'
version = '0.1.0'
release = '0.1.0'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'default'
# html_static_path = ['_static']
htmlhelp_basename = 'ultimatethumbdoc'
latex_documents = [(
    'index', 'ultimatethumb.tex', 'ultimatethumb Documentation',
    'Moccu GmbH & Co. KG', 'manual'
)]
man_pages = [(
    'index', 'ultimatethumb', 'ultimatethumb Documentation',
    ['Moccu GmbH & Co. KG'], 1
)]
texinfo_documents = [(
    'index', 'ultimatethumb', 'ultimatethumb Documentation',
    'Moccu GmbH & Co. KG', 'ultimatethumb', 'Generate thumbnails of anything.',
    'Miscellaneous'
)]
intersphinx_mapping = {'http://docs.python.org/': None}
