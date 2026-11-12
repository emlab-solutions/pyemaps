Data folder and license
=======================

.. _Environment Variables:

Environment Variables
---------------------

The *PYEMAPS_DATA* environment variable names pyEMAPS' data folder: one place for your own
crystal files and for the results pyEMAPS saves. pyEMAPS creates the folder if it doesn't exist.
If *PYEMAPS_DATA* isn't set, or its folder can't be created, the current working directory is
the data folder.

When you give a crystal file name without a folder, pyEMAPS looks for it:

1. in the current working directory, then
2. in the *crystals* subfolder of the data folder.

pyEMAPS saves each kind of result in its own subfolder of the data folder, and creates the
subfolder when it's first needed:

.. code-block:: text

    %PYEMAPS_DATA%            the data folder, which needs read and write permission
    %PYEMAPS_DATA%\crystals   your crystal files (.xtl, .cif, .json)
    %PYEMAPS_DATA%\dif        kinematic diffraction plots
    %PYEMAPS_DATA%loch      dynamic diffraction images and plots
    %PYEMAPS_DATA%\stereo     stereodiagram plots
    %PYEMAPS_DATA%\mxtal      crystal structures (.xyz)
    %PYEMAPS_DATA%\dpdb       diffraction pattern databases

.. note::

   The older *PYEMAPS_CRYSTALS* variable is still supported. If it's set, pyEMAPS uses its
   folder as the data folder instead, and keeps everything in that folder itself, without
   subfolders.


.. _License Activation:

License Activation
------------------

**pyEMAPS**' base features need no license. Its extended features, such as 4D-STEM, need an
activated license. Activation also works offline, and once a license is activated, all license
checks are offline. ``-l`` is the short form of ``--license`` in the commands below.

* **Trial license**: a 7-day trial license lets you try the extended features before you buy.
  It can be converted or upgraded to a production license later. Activating it needs an
  internet connection:

  .. code-block:: console

     pyemaps --license trial

* **License activation token**: activates a trial or production license, online or offline.
  Write to support@emlabsoftware.com for a token. It has 19 characters, in the form
  ``XXXX-XXXX-XXXX-XXXX``, where each X is a letter or digit:

  .. code-block:: console

     pyemaps --license XXXX-XXXX-XXXX-XXXX

* **License information**: shows whether a license is activated and valid, and if it is, its
  details:

  .. code-block:: console

     pyemaps --license info
