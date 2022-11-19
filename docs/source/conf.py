# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyemaps'
copyright = '2022, EMLab Solutions, Inc.'
author = 'EMLab Solutions, Inc.'
release = '0.4.7 Beta'



# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    "sphinx.ext.autosectionlabel",
    'sphinx.ext.autosummary',
]
autodoc_default_options = {
    'members': 'var1, var2',
    'member-order': 'bysource',
    'special-members': '__init__', 
    'undoc-members': True,
    'autosummary_generate': True,
    # 'exclude-members': '__weakref__'
}
# Make sure the target is unique
autosectionlabel_prefix_document = True
autodoc_preserve_defaults = True

templates_path = ['_templates']
exclude_patterns = []



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