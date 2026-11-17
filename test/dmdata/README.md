# DigitalMicrograph test files

Test files for the DM3/DM4 reader (`pyemaps/dmreader.py`), checked by `test/run_expimage.py`.
`make_fixtures.py` writes them; `expected.npz` and `manifest.json` hold what each must read as.

## Third-party data

`dm4_al_crop.dm4` contains data from:

- **Title:** Nanoscale mapping of point defect concentrations with 4D-STEM
- **Source:** Zenodo record 7041997, <https://zenodo.org/records/7041997>, file
  `Al_irradiated.dm4`
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0),
  <https://creativecommons.org/licenses/by/4.0/>
- **Changes:** 4 of the 1600 patterns are kept (a 2 x 2 part of the 40 x 40 scan), cropped to
  the central 128 x 128 pixels, with the original "Microscope Info" tags and a scan shape of
  2 x 2; written to a new file by `make_fixtures.py`.

## Other files

All the other files were written for these tests by `make_fixtures.py` from synthetic data,
with its own DM3/DM4 writer following Chris Boothroyd's description of the formats
(<https://personal.ntu.edu.sg/cbb/info/dmformat/>). They are part of pyEMAPS
(GPL-3.0-or-later, with the linking exception in `license-exception.txt`).
