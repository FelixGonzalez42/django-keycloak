# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Django Keycloak'
copyright = '2018-2024, Peter Slump y colaboradores'
author = 'Peter Slump y colaboradores'

# The short X.Y version
version = '0.2.9'
# The full version, including alpha/beta/rc tags
release = '0.2.9'


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'es'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


# -- Options for HTMLHelp output ---------------------------------------------

htmlhelp_basename = 'DjangoKeycloakdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}

latex_documents = [
    (master_doc, 'DjangoKeycloak.tex', 'Django Keycloak Documentation',
     author, 'manual'),
]


# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, 'djangokeycloak', 'Django Keycloak Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (master_doc, 'DjangoKeycloak', 'Django Keycloak Documentation',
     author, 'DjangoKeycloak', 'Integración Keycloak para Django.',
     'Miscellaneous'),
]


# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
}
