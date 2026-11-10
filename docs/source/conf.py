# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyemaps'
copyright = '2022-2025, EMLab Solutions, Inc.'
author = 'EMLab Solutions, Inc.'
release = '2.0.0 Stable'



# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    "sphinx.ext.autosectionlabel",
    'sphinx.ext.autosummary',
]

html_favicon = 'pyemaps.ico'

autodoc_default_options = {
    'members': 'var1, var2',
    'member-order': 'bysource',
    'special-members': '__init__', 
    'undoc-members': True,
    'autosummary_generate': True,
    # 'exclude-members': '__weakref__'
}
autodoc_mock_imports = ['pyemaps.diffract.emaps', 
                        'pyemaps.scattering.scattering', 
                        'pyemaps.spg.spg']
# Make sure the target is unique
autosectionlabel_prefix_document = True
autodoc_preserve_defaults = True

templates_path = ['_templates']
exclude_patterns = ['_build', '**.ipynb_checkpoints']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'bizstyle'  # Okay, but hard to adjust contents size
# html_theme = 'agogo'
html_theme = 'classic'
# html_theme = 'basic'
# html_static_path = ['_static']
html_static_path = []

html_theme_options = {
    "rightsidebar": "false",
    # "relbarbgcolor": "black",
    # "sidebarwidth": "30e", 
    # "bgcolor": "blue",
    'globaltoc_maxdepth': 3,
}

html_sidebars = {
   '**': ['globaltoc.html', 'relations.html', 'searchbox.html'],
}

# Python 3.12+ gives Enum classes a long constructor signature, e.g.
# DW(value, names=_not_given, *values, module=None, ...). Show them as
# DW(value), as the docs built on Python 3.7 did.
import enum


def _enum_signature(app, what, name, obj, options, signature, return_annotation):
    if what == 'class' and isinstance(obj, type) and issubclass(obj, enum.Enum):
        return '(value)', return_annotation
    return signature, return_annotation


def setup(app):
    app.connect('autodoc-process-signature', _enum_signature)
