from ast import keyword
from ensurepip import version
from multiprocessing import AuthenticationError
from nturl2path import url2pathname
from ssl import Options


def configuration(parent_package='',top_path=None):
    from codecs import open
    from os import path
    # from scipy._build_utils.system_info import get_info, NotFoundError
    # lapack_opt = get_info("lapack_opt")
    here = path.abspath(path.dirname(__file__))
    # Get the long description from the README file
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    from numpy.distutils.misc_util import Configuration
    keys = ['kinematic', 'diffraction', 'simulation', 'crystallography','python']
    config = Configuration(
        'pyemaps',parent_package,top_path,
        description = 'Python Module for Electron Diffraction Simulations',
        long_description = long_description,
        long_description_content_type="text/markdown",
        keywords = keys,
        classifiers = [
            'Development Status :: 2 - Pre-Alpha',
            'Programming Language :: Python :: 3.6',
            'Operating System :: Microsoft :: Windows',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )
    config.add_subpackage('diffract','emaps')
    config.add_data_files('license.txt', 'README.md')
    config.add_data_dir('test')
    config.add_data_dir('cdata')
    config.add_data_dir('samples')
    config.make_config_py() #generated automatically by distutil based on supplied __config__.py
    return config

if __name__ == '__main__':
    # import setuptools 
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())