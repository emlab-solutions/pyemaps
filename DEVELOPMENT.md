# Developing pyEMAPS

This guide is for contributors: how to build pyEMAPS from source, run its tests, build its
documentation, and how changes get into `main`. To use pyEMAPS, install it from PyPI instead; see
the [README](https://github.com/emlab-solutions/pyemaps/blob/main/README.md).

pyEMAPS is pure Python, so building it needs no compiler. Its compiled simulation backend,
**emaps**, isn't built from this repository: pip installs it from PyPI with pyEMAPS. emaps
supports 64-bit Windows with Python 3.12 to 3.15, so pyEMAPS does too. We're also looking for
contributors to extend pyEMAPS to other platforms.

## Set up

You need:

- 64-bit Windows
- Python 3.12, 3.13, 3.14 or 3.15, for example from the
  [python.org Windows installers](https://www.python.org/downloads/windows/)
- Git
- An editor. We use VS Code, but any editor works.

Clone the repository, and create a virtual environment for building and testing in it:

```
git clone https://github.com/emlab-solutions/pyemaps.git
cd pyemaps
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install setuptools wheel build
```

Run the commands in the rest of this guide from the `pyemaps` folder, in that environment.

## Repository layout

<pre>
pyemaps
├─ cdata          built-in crystal data (.xtl files)
├─ CifFile        the CIF reader (PyCifRW)
├─ diffract       the simulation methods added to Crystal
├─ docs           the documentation (Sphinx). Document your changes!
├─ samples        the sample scripts that ship with pyEMAPS
├─ scattering     scattering factor data
├─ spg            space group data
├─ test           the test suites and their baselines. Keep adding tests!
├─ *.py           the package modules: crystals.py, display.py, stackimg.py and others
└─ build_pyemaps  the build script
</pre>

## Build

```
python build_pyemaps -v 0.0.0.dev0
```

This builds the wheel and the source package for version `0.0.0.dev0` into `dist`:

- `pyemaps-0.0.0.dev0-py3-none-any.whl`, the package to install
- `pyemaps-0.0.0.dev0.tar.gz`, the source package

Use any version you like. The build writes it into `__version__.py`, which isn't tracked by Git.
Without `-v`, `build_pyemaps` takes the newest version on pypi.org and adds one, or the newest on
test.pypi.org with `-t`. That needs the `requests` package. The build exits with an error, and
prints no wheel name, if either package fails to build.

## Install

```
pip uninstall -y pyemaps
pip install dist\pyemaps-0.0.0.dev0-py3-none-any.whl
```

pip installs emaps, NumPy and matplotlib from PyPI if they aren't installed yet. Uninstall first
when rebuilding the same version; otherwise pip keeps the copy that's already installed.

## Test

With your build installed, run the sanity tests, the same checks that run on every pull request:

```
python test\ci_sanity.py
```

They run the samples, the features and the unit tests and compare the results with the stored
baselines in `test\baseline`. They fail if any result differs. The logs are saved in
`sanity-logs`.

The suites can also be run on their own:

```
python test\run_samples.py -bc all
python test\run_features.py -bc all
python test\run_unittests.py -bc all
```

More checks, which CI doesn't run:

- `python test\run_samples.py -gr all` shows the samples' plots and saves them as PNG files, in
  subfolders such as `dif` and `bloch` of the folder set by the `PYEMAPS_DATA` environment
  variable, or else of the current folder. Look at the images: a run can match the baselines and
  still draw a wrong pattern.
- `python test\performance\run_perf_test.py -r all` compares the run times with a stored
  baseline. Timings depend on the machine.
- `python test\stress\bloch\zone.py -bc` runs a large Bloch wave simulation and compares it with
  its baseline. It takes about 10 minutes.
- `python test\run_stem4d.py -bc` checks the 4D-STEM features. It needs an activated license.

`-bg` regenerates a suite's baselines. Use it only when a change to the results is intended, and
explain the change in your pull request.

## Documentation

The documentation source is in `docs\source`. The API pages are generated from the docstrings, so
the build imports pyEMAPS: install your build first. Then:

```
pip install -r docs\requirements.txt
sphinx-build -E -b html docs\source docs\_build\html
```

Open `docs\_build\html\index.html` in a browser to check the result. GitHub Actions builds the
documentation for every pull request that changes it, and publishes the site when a pyEMAPS
release is published.

## How we work

- **Issues.** Before you change code for a bug fix or a feature, open an
  [issue](https://github.com/emlab-solutions/pyemaps/issues) that describes it. It's a good
  basis for the design, and it tells other contributors what's being worked on.
- **Branches.** Make your changes on your own branch from `main`. `main` is the production
  branch.
- **Tests.** Run the tests above before you open a pull request. They make sure existing
  features still work after your change. Add tests for new features.
- **Pull requests.** Changes reach `main` only through pull requests. The sanity tests must pass
  on Python 3.12 to 3.15 before a pull request can be merged.
- **Code review.** We take code review seriously, whether we're reviewing code or having our code
  reviewed. It's how we keep the implementation sound and catch new bugs.
- **Documentation.** Document what you add or change, in the docstrings and in `docs\source`,
  and add a line to the release notes in `docs\source\rn.rst`.

## Contributor License Agreement and Code of Conduct

Please read and agree to our
[Contributor License Agreement](https://github.com/emlab-solutions/pyemaps/blob/main/CONTRIBUTING.md)
before contributing.

We're committed to a welcoming and inclusive environment for all contributors, and follow the
[Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/) as our
code of conduct. Report unacceptable behavior to support@emlabsoftware.com.
