# pyEMAPS

**pyEMAPS** is a Python package for transmission electron diffraction simulations and
crystallographic computing, for all crystal systems. Its simulations are based on the theories of
kinematical and dynamical electron diffraction described by J. C. H. Spence and J. M. Zuo in
*Electron Microdiffraction* (Plenum Press, New York, 1992).

[Documentation](https://emlab-solutions.github.io/pyemaps/) ·
[Get started](https://emlab-solutions.github.io/pyemaps/getting_started.html) ·
[Examples](https://emlab-solutions.github.io/pyemaps/examples.html) ·
[Release notes](https://emlab-solutions.github.io/pyemaps/rn.html) ·
[Issues](https://github.com/emlab-solutions/pyemaps/issues)

## Features

The base features are free, under the GNU General Public License v3.0:

- **Crystallography**
  - Crystal construction, from your own data or the built-in crystal library
  - CIF import
  - Crystallographic transformations
  - Real and reciprocal space vector calculations
  - Stereodiagrams
  - Crystal structure factors
- **Kinematical electron diffraction**
  - Selected area diffraction
  - Kikuchi and higher order Laue zone (HOLZ) line geometry
  - Convergent beam electron diffraction (CBED)
  - Electron powder diffraction
- **Dynamical electron diffraction** (Bloch wave)
  - Convergent beam electron diffraction, including large-angle CBED
  - The electron scattering matrix
  - Electron dispersion (the eigenvalues of the Bloch wave solution)

The extended 4D-STEM features need a license:

- Building and searching diffraction pattern databases
- Indexing experimental diffraction patterns
- Annular bright and dark field images
- Masked images

## Requirements

- 64-bit Windows
- Python 3.12, 3.13, 3.14 or 3.15
- 8 GB of RAM or more is recommended

pip also installs NumPy (2.0 or later), matplotlib (3.8.4 or later) and **emaps**, the compiled
simulation backend for your Python version. On Python 3.7, pip installs pyEMAPS 1.1.x.

## Installation

Install pyEMAPS in its own virtual environment, so its dependencies don't clash with your other
packages:

```
python -m venv .venv
.venv\Scripts\activate
pip install pyemaps
```

Check the installation:

```
pyemaps --version
pyemaps --sample
```

`--version` prints the pyEMAPS version, and `--sample` runs a short kinematical simulation and
shows the pattern. If the installation fails, see the
[FAQ](https://emlab-solutions.github.io/pyemaps/faq.html).

## Quick start

Load Silicon from the built-in crystal library, generate its kinematical diffraction pattern with
the default settings, and show it:

```python
from pyemaps import Crystal, DPList, showDif

if __name__ == '__main__':
    si = Crystal.from_builtin('Silicon')
    emc, si_dp = si.generateDP()

    dpl = DPList('Silicon')
    dpl.add(emc, si_dp)
    showDif(dpl)
```

Keep the `if __name__ == '__main__':` line in scripts. The `show` functions draw in a separate
process, which on Windows runs your script again. Jupyter notebooks don't need it.

`pyemaps -cp` copies the sample scripts into a `pyemaps_samples` folder and the Jupyter
notebooks into `pyemaps_notebooks`; `pyemaps -cp samples` or `pyemaps -cp notebooks` copies just
one set.

The [documentation](https://emlab-solutions.github.io/pyemaps/) has a user guide, an examples
gallery and the full API reference.

## Licensing

The base features are free software under the
[GNU General Public License v3.0](https://emlab-solutions.github.io/pyemaps/license.html), for
personal and commercial use. The extended 4D-STEM features need a license:

- `pyemaps --license trial` activates a 7-day trial license. It needs an internet connection.
- `pyemaps --license <token>` activates a trial or production license with a license activation
  token, online or offline. Write to support@emlabsoftware.com for a token.
- `pyemaps --license info` shows the current license.

After activation, all license checks are offline. See
[License Activation](https://emlab-solutions.github.io/pyemaps/user_guide/configuration.html#license-activation)
for details.

## Support

Report bugs and request features on [GitHub](https://github.com/emlab-solutions/pyemaps/issues),
and send other questions to support@emlabsoftware.com.

If pyEMAPS helps your microscopy and crystallography research or teaching, please consider a
[donation](https://www.paypal.com/paypalme/pyemaps22). Donations keep us providing software
tools to the education and research communities.

## Contributing

We're looking for experts in electron microscopy and crystallography, and Python enthusiasts, to
join the project. Contact us at support@emlabsoftware.com if you're interested.

- [DEVELOPMENT.md](https://github.com/emlab-solutions/pyemaps/blob/main/DEVELOPMENT.md)
  explains how to build pyEMAPS, run its tests and build the documentation, and how we work.
- Please read and agree to our
  [Contributor License Agreement](https://github.com/emlab-solutions/pyemaps/blob/main/CONTRIBUTING.md)
  before contributing.
- We follow the
  [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/) as our
  code of conduct. Report unacceptable behavior to support@emlabsoftware.com.

pyEMAPS is developed by EMLab Solutions, Inc.
