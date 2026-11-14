Frequently Asked Questions
==========================

What's Likely the Cause of Installation Failure?
------------------------------------------------

The most likely cause is an unsupported Python. pyEMAPS 2.x runs on Python 3.12, 3.13, 3.14 and
3.15 on 64-bit Windows, and its compiled backend, *emaps*, ships one prebuilt package (wheel) per
supported Python version.

On another Python version, on a 32-bit Python, or on another operating system, pip can't use
those wheels. It falls back to an older pyEMAPS release and tries to build *emaps* from source,
which fails with an error like:

.. code-block:: console

    Getting requirements to build wheel: finished with status 'error'
    error: subprocess-exited-with-error
    ...
    `numpy.distutils` is deprecated since NumPy 1.23.0 ...

To fix it, check your Python with ``python --version``, then install pyEMAPS in an environment
with a supported Python, for example:

.. code-block:: console

    conda create -n pyemaps python=3.12
    conda activate pyemaps
    pip install pyemaps

Python 3.7 users can keep using pyEMAPS 1.1.x, which pip installs there automatically.

.. _how-do-i-install-and-run-pyemaps-in-anaconda-environment-with-jupyter-notebook:

How Do I Use **pyEMAPS** in Jupyter Notebook?
---------------------------------------------

Install pyEMAPS and Jupyter in their own environment, so they don't conflict with your other
packages. With Anaconda, in the Anaconda Prompt:

.. code-block:: console

    conda create -n pyemaps python=3.12
    conda activate pyemaps
    pip install pyemaps jupyter
    jupyter notebook

Then create a notebook and run pyEMAPS in it. pyEMAPS draws its plots in the notebook. To
install a particular version, use ``pip install pyemaps==X.Y.Z``.

pyEMAPS comes with notebooks that walk through the samples step by step.
``pyemaps -cp notebooks`` copies them into a *pyemaps_notebooks* folder, ready to run; the
`notebooks folder <https://github.com/emlab-solutions/pyemaps/tree/main/notebooks>`_ on GitHub
shows them with their results.

If you start Jupyter from another environment instead, register this one as a kernel first, and
choose the *pyemaps* kernel in your notebook:

.. code-block:: console

    python -m ipykernel install --user --name pyemaps --display-name "pyemaps (Python 3.12)"

What Can I Do to Speed Up Dynamic Diffraction Simulations?
----------------------------------------------------------

A Bloch (dynamic diffraction) simulation takes much more computation than a kinematic one, so
it's much slower. Large simulations, with more than 512 beams, already run parts of the
calculation in parallel threads.

When you run several simulations, for example with different microscope controls, run them in
parallel processes with Python's ``concurrent.futures``:

.. code-block:: python

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(crystal.generateBloch,
                                   disk_size=disk_size,
                                   sampling=20,
                                   sample_thickness=(1750, 1750, 100),
                                   em_controls=emc)
                   for emc in make_controls(control, random_sim)]

This is an excerpt from the *si_bloch.py* sample, which has the complete script. ``pyemaps -cp
samples`` copies the samples into a *pyemaps_samples* folder; see :doc:`examples`.

We keep working on pyEMAPS' performance, and welcome suggestions at support@emlabsoftware.com.
