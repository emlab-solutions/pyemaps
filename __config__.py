import os
import sys

extra_dll_dir = os.path.join(os.path.dirname(__file__), '.libs')

if sys.platform == 'win32' and os.path.isdir(extra_dll_dir):
    if sys.version_info >= (3, 8):
        os.add_dll_directory(extra_dll_dir)
    else:
        os.environ.setdefault('PATH', '')
        os.environ['PATH'] += os.pathsep + extra_dll_dir