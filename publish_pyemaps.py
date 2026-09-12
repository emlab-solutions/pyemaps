'''
Dedicated production-publish entry point for the pyemaps package.

Mirrors emaps-engine/emaps/publish_emaps.py. pyemaps has no free/full build-type
distinction (that's emaps-engine's concern), so there's no EMAPS_BTYPE footgun
here -- the risk this removes is simpler: accidentally publishing to (or
version-numbering against) test.pypi.org instead of the real pypi.org. This
script hardcodes the target to production pypi.org and reuses build_pyemaps's
own build/upload functions (loaded by file path, since build_pyemaps has no
.py extension) rather than duplicating them.

Usage (run from the pyemaps repo root, or from anywhere -- it chdirs to its
own directory first):

    python publish_pyemaps.py                # auto version, build + upload (asks to confirm)
    python publish_pyemaps.py -v 1.1.6        # explicit version instead of auto-increment
    python publish_pyemaps.py -nb             # skip rebuild, upload an existing dist/
    python publish_pyemaps.py --dry-run       # build only, never uploads

The upload step still goes through build_pyemaps.upload_package()'s existing
interactive "About to publish ... Are you sure? [Y|n]" confirmation -- that
safety gate is intentionally not removed.
'''

import importlib.util
from importlib.machinery import SourceFileLoader
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_PYEMAPS_PATH = os.path.join(HERE, 'build_pyemaps')

# build_pyemaps has no .py extension, so spec_from_file_location can't infer a
# loader on its own (it returns None) -- give it one explicitly.
_loader = SourceFileLoader('build_pyemaps', BUILD_PYEMAPS_PATH)
_spec = importlib.util.spec_from_loader('build_pyemaps', _loader)
build_pyemaps = importlib.util.module_from_spec(_spec)
_loader.exec_module(build_pyemaps)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Publish pyemaps to production pypi.org."
    )
    parser.add_argument("-v", "--build-version", type=str, default="",
                        help="explicit version; if omitted, auto-incremented from pypi.org's current latest")
    parser.add_argument("-nb", "--no-build", action="store_true",
                        help="skip the build step and upload an existing dist/ instead")
    parser.add_argument("--dry-run", action="store_true",
                        help="build (unless -nb) but do not upload")
    args = parser.parse_args()

    os.chdir(HERE)

    print("Target repo: pypi.org (production)")

    ver = args.build_version or build_pyemaps.get_bversion(btest=False)
    print(f"Version    : {ver}")

    with open(os.path.join(HERE, '__version__.py'), 'w') as vf:
        vf.write('__version__ = "' + ver + '"')

    if not args.no_build:
        build_pyemaps.build_package()
    else:
        print("Skipping build (--no-build): uploading existing dist/ contents.")

    if args.dry_run:
        print(f"Dry run complete: built pyemaps {ver}; not uploaded.")
        return

    ret = build_pyemaps.upload_package(bRelease=True, ver=ver)
    if ret == 0:
        print("Upload canceled.")
    else:
        print(f"pyemaps {ver} published to pypi.org.")


if __name__ == '__main__':
    main()
