
Frequently Asked Questions
==========================

What's Likely the Cause of Installation Failure?
------------------------------------------------

**pyemaps** installation includes version requirements on pip, 
its setuptools and wheel that make downloading and installing the package correct and fast. 
These tools and their right versions may not come with your *python* installation and environment. 
Without them, pip tries to re-build **pyemaps** from source and will fail due to the fact 
that **pyemaps** contains extensions modules. 

Make sure you have updated versions of pip, setuptools, and wheel:

.. code-block:: console
    
    pip install -U pip setuptools wheel 

before trying :ref:`installation <installation>` again.

How Do I Install and Run **pyemaps** in Anaconda Environment With Jupyter Notebook?
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