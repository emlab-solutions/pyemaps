# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyemaps'
# The end year is the year the docs are built.
import datetime
copyright = f'2022-{datetime.date.today().year}, EMLab Solutions, Inc.'
author = 'EMLab Solutions, Inc.'
release = '2.2.0 Stable'



# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    "sphinx.ext.autosectionlabel",
    'sphinx.ext.autosummary',
    'sphinx_design',
    'sphinx_copybutton',
    'sphinx_reredirects',
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

exclude_patterns = ['_build', '**.ipynb_checkpoints']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'bizstyle'  # Okay, but hard to adjust contents size
# html_theme = 'agogo'
html_theme = 'pydata_sphinx_theme'
html_title = 'pyEMAPS'
# _static/custom.css: brand colours and landing layout. _static/fonts: the self-hosted
# Source fonts (OFL), whose @font-face rules are in fonts/fonts.css.
html_static_path = ['_static']
html_css_files = ['fonts/fonts.css', 'custom.css']
html_theme_options = {
    'logo': {'text': 'pyEMAPS'},
    'navbar_align': 'left',
    'header_links_before_dropdown': 6,
    'show_toc_level': 2,
    'show_prev_next': True,
    'secondary_sidebar_items': ['page-toc'],
    'footer_start': ['copyright'],
    'footer_end': [],
    'icon_links': [
        {'name': 'GitHub', 'url': 'https://github.com/emlab-solutions/pyemaps',
         'icon': 'fa-brands fa-github'},
        {'name': 'PyPI', 'url': 'https://pypi.org/project/pyemaps/',
         'icon': 'fa-brands fa-python'},
    ],
}
html_sidebars = {
    'index': [],
    'getting_started': [],
    'examples': [],
    'help': [],
}
# Copy buttons skip prompts and comments
copybutton_prompt_text = r'\(\.venv\) \$ |\$ '
copybutton_prompt_is_regexp = True


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


# Pages from the old one-page-per-topic layout (pyemaps 2.0.0 and earlier) redirect to
# their new place. _redirect.html also sends old #anchors to the page that now holds them.
redirect_html_template_file = '_redirect.html'
_api_dec = ['bloch_dec', 'csf_dec', 'dif_dec', 'dpgen_dec', 'mxtal_dec', 'powder_dec', 'stereo_dec']
redirects = {
    'overview': 'about.html',
    'requirements': 'getting_started.html#install',
    'usage': 'getting_started.html',
    'visualization': 'user_guide/index.html',
    'modules': 'api/index.html',
    'pyemaps_modules': 'api/index.html',
    'pyemaps': 'api/index.html',
    'pyemaps.crystals': 'api/crystals.html',
    'pyemaps.ddiffs': 'api/dynamic.html',
    'pyemaps.display': 'api/display.html',
    'pyemaps.emcontrols': 'api/controls.html',
    'pyemaps.errors': 'api/errors.html',
    'pyemaps.fileutils': 'api/fileutils.html',
    'pyemaps.kdiffs': 'api/kinematic.html',
    'pyemaps.diffract': 'api/crystals.html',
    'pyemaps.diffract.emaps': 'api/crystals.html',
    'pyemaps.scattering': 'api/index.html',
    'pyemaps.scattering.scattering': 'api/index.html',
    'pyemaps.spg': 'api/index.html',
    'pyemaps.spg.spg': 'api/index.html',
    **{f'pyemaps.diffract.{d}': 'api/crystals.html' for d in _api_dec},
}
