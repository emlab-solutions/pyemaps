Examples
========

pyEMAPS ships with sample scripts for each feature. ``pyemaps -cp samples`` copies them into a
*pyemaps_samples* folder in the current directory, after asking you to confirm. Then run any of
them with ``python``:

.. code-block:: console

   pyemaps -cp samples
   cd pyemaps_samples
   python si_dif.py

pyEMAPS also ships with Jupyter notebooks that walk through the samples step by step.
``pyemaps -cp notebooks`` copies them into a *pyemaps_notebooks* folder, and ``pyemaps -cp``
copies both. Files already in those folders aren't overwritten, so copying again keeps your
changes. To read them with their results, without running anything, see the
`notebooks folder <https://github.com/emlab-solutions/pyemaps/tree/main/notebooks>`_ on GitHub.
The 4D-STEM indexing notebooks are also shown here with their results:
:doc:`al_ediom.ipynb <notebooks/al_ediom>`, :doc:`al_orientmap.ipynb <notebooks/al_orientmap>`
and :doc:`al_cu_phasemap.ipynb <notebooks/al_cu_phasemap>`.

.. container:: pe-gallery

   .. grid:: 1 2 3 3
      :gutter: 3

      .. grid-item-card:: si_dif.py
         :img-top: _static/images/dif_table.png

         Kinematic diffraction patterns for Silicon, varying one microscope control at a
         time: tilt, zone axis, deflection, high voltage or camera length.
         Rendered with matplotlib.

         Guide: :doc:`user_guide/kinematic`

      .. grid-item-card:: si_bloch.py
         :img-top: _static/images/bloch_table.png

         Dynamic (Bloch wave) CBED patterns for Silicon, in parallel processes.

         Guide: :doc:`user_guide/dynamic`

      .. grid-item-card:: si_stereo.py
         :img-top: _static/images/stereo_zones.gif

         Indexed stereodiagrams for Silicon over a series of tilts and a series of zone
         axes.

         Guide: :doc:`user_guide/stereo`

      .. grid-item-card:: powder.py
         :img-top: _static/images/powder.png

         Electron powder diffraction profiles for Silicon and Diamond.

      .. grid-item-card:: si_constructor.py
         :img-top: _static/images/mxtal01.png
         :class-img-top: pe-cover

         Builds a Silicon supercell and saves it as an *.xyz* file.

         Guide: :doc:`user_guide/crystals`

      .. grid-item-card:: ronchigram.py
         :img-top: _static/images/probe_ronchigram.png

         Ronchigrams of a corrected probe, with astigmatism, and of an uncorrected one.

         Guide: :doc:`user_guide/probe/ronchigram`.
         Notebook: :doc:`probe.ipynb <notebooks/probe>`

      .. grid-item-card:: stem_probe.py
         :img-top: _static/images/probe_stem_probe.png

         STEM probes and their sizes: uncorrected, corrected, and with a corrector's
         residual aberrations.

         Guide: :doc:`user_guide/probe/stem_probe`

      .. grid-item-card:: ctf.py
         :img-top: _static/images/probe_ctf.png

         The contrast transfer function at and around the Scherzer defocus, with its
         envelopes, and for a corrected lens.

         Guide: :doc:`user_guide/probe/ctf`

      .. grid-item-card:: hrem.py
         :img-top: _static/images/probe_hrem.png

         HREM images of amorphous carbon and their Thon rings.

         Guide: :doc:`user_guide/probe/hrem`

      .. grid-item-card:: crystal_thickness.py :bdg-info:`Licensed`
         :img-top: _static/images/probe_multislice.png

         Silicon [110] through the thickness by the multislice method: HREM images and CBED
         patterns at several thicknesses.

         Guide: :doc:`user_guide/probe/multislice`.
         Notebook: :doc:`si_multislice.ipynb <notebooks/si_multislice>`

      .. grid-item-card:: al_ediom.py :bdg-info:`Licensed`
         :img-top: _static/images/ediom_img1.png
         :class-img-top: pe-cover

         Generates an Aluminium pattern database and indexes the sample image *al.img*.

         Guide: :doc:`user_guide/stem4d/indexing`.
         Notebook: :doc:`al_ediom.ipynb <notebooks/al_ediom>`

      .. grid-item-card:: al_orientmap.py :bdg-info:`Licensed`
         :img-top: _static/images/orientmap.png

         An orientation map of a synthetic Aluminium 4D-STEM scan, compared with the true
         orientations. Experimental.

         Guide: :doc:`user_guide/stem4d/orientation`.
         Notebook: :doc:`al_orientmap.ipynb <notebooks/al_orientmap>`

      .. grid-item-card:: al_cu_phasemap.py :bdg-info:`Licensed`
         :img-top: _static/images/al_cu_phasemap.png

         A phase map of a synthetic 4D-STEM scan of aluminium and copper grains, compared with
         the true phases. Experimental.

         Guide: :doc:`user_guide/stem4d/phase`.
         Notebook: :doc:`al_cu_phasemap.ipynb <notebooks/al_cu_phasemap>`

More samples
------------

* *si_lacbed.py*: large-angle CBED, one image per diffracted beam.
* *si_csf.py*: crystal structure factors.
* *si_scm.py*: the scattering matrix, eigenvalues and diffracted beams of a Bloch session.
* *al_dpgen.py*: generates a diffraction pattern database for Aluminium, used by 4D-STEM
  indexing. :bdg-info:`Licensed`
* *convert_image.py*: converts a raw image into pyEMAPS' small-header image format.
  :bdg-info:`Licensed`
* *adf.py*: annular bright and dark field images and a masked image from an experimental
  image. It needs *adftest900.im3*, available from
  `Zenodo <https://zenodo.org/records/14028793/files/adftest900.im3?download=1>`_; save it
  in the *pyemaps_samples* folder. See :doc:`user_guide/stem4d/imaging`. :bdg-info:`Licensed`
* *dm_diff.py*: draws kinematic diffraction patterns in DigitalMicrograph; run it inside DM.
  See :doc:`user_guide/third_party`.
