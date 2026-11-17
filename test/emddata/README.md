# EMD test files

Test files for the EMD reader (`pyemaps/emdreader.py`), checked by `test/run_expimage.py`.
`make_fixtures.py` writes them; `expected.npz` and `manifest.json` hold what each must read as.

## Third-party data

`velox_iliad_dfs.emd` contains data from:

- **Title:** DSO: STEM EELS EMD
- **Author:** Daen Jannis
- **Source:** Zenodo record 18267156, <https://zenodo.org/records/18267156>
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0),
  <https://creativecommons.org/licenses/by/4.0/>
- **Changes:** only the DF-S STEM image, its metadata and Velox's thumbnail are kept from
  `STEM_EELS_1.emd`; everything else in the file was removed.

## Other files

All the other files were written for these tests by `make_fixtures.py`, with h5py: Velox-layout
files from synthetic data, and Berkeley EMD files following the EMD specification
(<https://emdatasets.com/format/>). They are part of pyEMAPS (GPL-3.0-or-later, with the linking
exception in `license-exception.txt`).
