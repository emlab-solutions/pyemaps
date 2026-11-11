
Frequently Asked Questions
==========================

What's Likely the Cause of Installation Failure?
------------------------------------------------

The most likely cause is an unsupported Python version. pyEMAPS 2.x runs on Python 3.12,
3.13, 3.14 and 3.15 on 64-bit Windows, and its compiled backend, *emaps*, ships one prebuilt
package (wheel) per supported Python version.

On another Python version, pip can't use those wheels. It falls back to an older pyEMAPS
release and tries to build *emaps* from source, which fails with an error like:

.. code-block:: console

    Getting requirements to build wheel: finished with status 'error'
    error: subprocess-exited-with-error
    ...
    `numpy.distutils` is deprecated since NumPy 1.23.0 ...

To fix it, check your Python version with ``python --version``, then install pyEMAPS in an
environment with a supported Python, for example:

.. code-block:: console

    conda create -n pyemaps python=3.12
    conda activate pyemaps
    pip install pyemaps

Python 3.7 users can keep using pyEMAPS 1.1.x, which pip installs there automatically.

How Do I Install and Run **pyEMAPS** in Anaconda Environment With Jupyter Notebook?
-----------------------------------------------------------------------------------

Installing pyEMAPS in an virtual environment provides isolation and prevents conflicts.
Anaconda and python's own virtual environment are good choices.

Follow the steps below to install and run pyEMAPS in Anaconda with Jupyter Notebooks:

* Install Anaconda. 
  
  .. note::

    You may need to make a clean install by doing a "Full Uninstall" of existing Anaconda by 
    deleting old environment and packages folders as old packages can cause dependencies issues.

* Create a new environment in Anaconda called 'pyemaps' in Anaconda command prompt:
  
  .. code-block:: console

    conda create -n pyemaps python=3.12

  .. note::
    
    pyEMAPS supports Python 3.12 to 3.15. On Python 3.7, pip installs pyEMAPS 1.1.x.

* Switch to the new *pyemaps* environment by activating it:

  .. code-block:: console

    conda activate pyemaps
    
* Install latest pyemaps in the new environment:

  .. code-block:: console

    pip install pyemaps (or pyemaps==X.X.X)

* Install Jupyter:

  .. code-block:: console

    pip install jupyter

* Run 
    
  .. code-block:: console

    conda install ipywidgets
    conda install widgetsnbextension
    python -m ipykernel install --user --name pyemaps --display-name "pyemaps (python 3.12)"

  .. note::
    
    replace --display-name value with your own string if desired.

* Run Jupyter local server:
    
  .. code-block:: console
    
    jupyter notebook
    
  Create a new notebook file to run pyemaps tasks.

  
What can I do to speed up dynamic diffraction simulations?
----------------------------------------------------------

**pyEMAPS** Bloch simulation, e. g. dynamic diffraction simulation costs
significant computation resource and operations. As a result, it is much
slower than that of kinematic simulation. 

While pyEMAPS performance has improved significantly since its inception, 
there are still rooms for enhancements and we are still looking for 
opportunities to make constant progress.

Meanwhile, you can also add to this effort in your simulation with 
**pyEMAPS** by taking advantages of python features such as parallel 
processing. 

For example:

- Using python multiprocessing if your simulation involves multiple controls input.

.. code-block:: python

  with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

        for ec in emclist:
            fs.append(e.submit(cr.generateBloch, 
                               disk_size=dsize, 
                               sampling = 20, 
                               sample_thickness=(1750,1750,100),
                               em_controls = ec))

The above code snippet can be found in *samples* folder in *si_bloch.py*.

- Assisting simulation computation by setting %TMPDIR% environment to a file location 
  where file I/O performance is much higher than that of the normal folder. 