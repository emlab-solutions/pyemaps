
Frequently Asked Questions
==========================

What's Likely the Cause of Installation Failure?
------------------------------------------------

**pyEMAPS** installation includes version requirements on pip, 
its setuptools and wheel that make downloading and installing the package correct and fast. 
These tools and their right versions may not come with your *python* installation and environment. 
Without them, pip tries to re-build **pyEMAPS** from source and will fail due to the fact 
that **pyEMAPS** contains extensions modules. 

Make sure you have updated versions of pip, setuptools, and wheel:

.. code-block:: console
    
    pip install -U pip setuptools wheel 

before trying :ref:`installation <installation>` again.

How Do I Install and Run **pyEMAPS** in Anaconda Environment With Jupyter Notebook?
---------------------------------------------------------------------------------

Installing pyemaps in an virtual environment provides isolation and prevents conflicts.
Anaconda and python's own virtual environment are good choices.

Follow the steps below to install and run pyemaps in Anaconda with Jupyter Notebooks:

* Install Anaconda. 
  
  .. note::

    You may need to make a clean install by doing a "Full Uninstall" of existing Anaconda by 
    deleting old environment and packages folders as old packages can cause dependencies issues.

* Create a new environment in Anaconsa called 'pyemaps' in Anaconda command prompt:
  
  .. code-block:: console

    conda create -n pyemaps python=3.7

  .. note::
    
    Python 3.7 is the only supported python version for now, more version support in development.

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
    python -m ipykernel install --user --name pyemaps --display-name "pyemaps (python 3.7)"

  .. note::
    
    replace --display-name value with your own string if desired.

* Run Jupyter local server:
    
  .. code-block:: console
    
    jupyter notebook
    
  Create a new notebook file to run pyemaps tasks.

  
What can I do to speed up dynamic diffraction simulations?
---------------------------------------------------------

**pyEMAPS** Bloch simulation, e. g. dynamic diffraction simulation costs
significant computation resource and operations. As a result, it is much
slower than that of kinematic simulation. 

While pyemaps performance has improved significantly since its inception, 
there are still rooms for enhancements and we are still looking for 
opportunities to make constant progress.

Meanwhile, you can also add to this effort in your simulation with 
**pyEMAPS** by taking advantages of python features such as parallell 
processing. 

For example:

- Using python mutiprocessing if your simulation involves multiple controls input.

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