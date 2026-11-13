# pyEMAPS notebooks

Jupyter notebooks that walk through pyEMAPS step by step, one step per cell. Each follows one of
the sample scripts in [`samples/`](../samples), with explanations, so you can run them yourself
or use them in class.

| Notebook | Sample | Topic |
|---|---|---|
| [si_dif.ipynb](si_dif.ipynb) | `si_dif.py` | Kinematic diffraction of Silicon: spot and CBED patterns, zone axis, tilt and camera length |
| [si_bloch.ipynb](si_bloch.ipynb) | `si_bloch.py` | Dynamic (Bloch wave) diffraction of Silicon: CBED images, sampling, sample thickness, tilt and zone axis |

GitHub shows each notebook with its results, so you can read it without installing anything.

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
