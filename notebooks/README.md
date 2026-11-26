# pyEMAPS notebooks

Jupyter notebooks that walk through pyEMAPS step by step, one step per cell. Each follows one of
the sample scripts in [`samples/`](../samples), with explanations, so you can run them yourself
or use them in class.

| Notebook | Sample | Topic |
|---|---|---|
| [si_dif.ipynb](si_dif.ipynb) | `si_dif.py` | Kinematic diffraction of Silicon: spot and CBED patterns, zone axis, tilt and camera length |
| [si_bloch.ipynb](si_bloch.ipynb) | `si_bloch.py` | Dynamic (Bloch wave) diffraction of Silicon: CBED images, sampling, sample thickness, tilt and zone axis |
| [si_lacbed.ipynb](si_lacbed.ipynb) | `si_lacbed.py` | Large-angle CBED (LACBED) of Silicon: one image per beam, the Bragg lines, sample thickness and zone axis |
| [si_scm.ipynb](si_scm.ipynb) | `si_scm.py` | Inside a Bloch wave calculation: the scattering matrix, absorption, the Bloch waves behind the thickness fringes, and Bethe potentials |
| [si_csf.ipynb](si_csf.ipynb) | `si_csf.py` | Silicon's structure factors: X-ray and electron, forbidden reflections, the Mott-Bethe formula, high voltage and absorption |
| [si_stereo.ipynb](si_stereo.ipynb) | `si_stereo.py` | Stereographic projections of Silicon: poles, the projection's geometry, zone axis and tilt |
| [si_constructor.ipynb](si_constructor.ipynb) | `si_constructor.py` | Building a Silicon supercell: bonds, density, the [110] dumbbells, and saving an .xyz file |
| [powder.ipynb](powder.ipynb) | `powder.py` | Electron powder diffraction of Silicon and Diamond: indexing the peaks, peak shape, high voltage and absorption |
| [al_ediom.ipynb](al_ediom.ipynb) | `al_dpgen.py`, `al_ediom.py` | Indexing an experimental Aluminium diffraction pattern against a simulated database, and checking the result. Licensed |
| [al_orientmap.ipynb](al_orientmap.ipynb) | `al_orientmap.py` | Orientation mapping of a synthetic 4D-STEM scan of Aluminium grains: indexing settings for scans, reading the map, and comparing it with the true orientations. Licensed; experimental |
| [adf.ipynb](adf.ipynb) | `adf.py`, `convert_image.py` | 4D-STEM virtual detectors: bright field, dark field, annular dark field and masked images. Licensed; downloads a 472 MB test scan |
| [probe.ipynb](probe.ipynb) | `ronchigram.py`, `stem_probe.py`, `ctf.py`, `hrem.py`, `crystal_imaging.py` | What a lens with aberrations does: Ronchigrams, STEM probes and their size, the contrast transfer function and its envelopes, HREM images with their Thon rings, and the projected potential of a crystal |
| [si_multislice.ipynb](si_multislice.ipynb) | `crystal_thickness.py` | Thick crystals by the multislice method: the projection against the multislice, slice thickness and pixel size, thickness fringes checked against Bloch waves, and HREM and CBED thickness series of Silicon. Licensed |

GitHub shows each notebook with its results, so you can read it without installing anything.

The 4D-STEM notebooks, `al_ediom`, `al_orientmap` and `adf`, and the multislice notebook, `si_multislice`, need an activated pyEMAPS license. `pyemaps -l trial`
activates a free 7-day trial; for a full license, contact support@emlabsoftware.com.

## Running them

pyEMAPS runs on Windows, with Python 3.12 to 3.15. Install pyEMAPS and Jupyter in the same
environment, then start Jupyter in the folder holding the notebooks:

```
pip install pyemaps jupyter
pyemaps -cp notebooks
jupyter notebook pyemaps_notebooks
```

`pyemaps -cp notebooks` copies the notebooks that come with pyEMAPS into a `pyemaps_notebooks`
folder, without their results, so you see them appear as you run each cell. It doesn't overwrite
notebooks already there, so copying again keeps your changes.

In a notebook, pyEMAPS draws its plots in the notebook.
