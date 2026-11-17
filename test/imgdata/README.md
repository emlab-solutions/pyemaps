# MRC, Merlin, picture and NumPy test files

Test files for the MRC, Merlin, picture and NumPy readers (`pyemaps/mrcreader.py`,
`pyemaps/mibreader.py`, `pyemaps/picreader.py`), checked by `test/run_expimage.py`.
`make_fixtures.py` writes them; `expected.npz` and `manifest.json` hold what each must read as.

## Third-party data

`mib_quad_real.mib` contains data from:

- **Title:** MerlinEM quad 4D-STEM dataset
- **Author:** Mohsen Danaie
- **Source:** Zenodo record 10813049, <https://zenodo.org/records/10813049>, file
  `20230724_110150_data.mib`
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0),
  <https://creativecommons.org/licenses/by/4.0/>
- **Changes:** the first 4 frames are kept, cropped to the central 128 x 128 pixels, with the
  frame headers' sizes changed to match; written to a new file by `make_fixtures.py`.

## Other files

All the other files were written for these tests by `make_fixtures.py` from synthetic data:

- the MRC files by mrcfile (BSD license), used only to write them;
- the Merlin files by the script's own writer, following the frame header described in
  Diamond Light Source's mib_props (MIT license, <https://github.com/ePSIC-DLS/mib_props>);
- the pictures by Pillow, and the NumPy files by numpy.

They are part of pyEMAPS (GPL-3.0-or-later, with the linking exception in
`license-exception.txt`).
