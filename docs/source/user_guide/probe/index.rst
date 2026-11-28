Probes, Ronchigrams, CTF and HREM
=================================

A lens adds a phase error χ(k) to the part of the electron wave travelling at each spatial
frequency k: from the defocus, the spherical aberration Cs (C3) and C5, and in a real lens the
residual aberrations a corrector measures. :py:class:`~pyemaps.probe.Probe` holds such a lens
and computes what it does: the Ronchigram that correctors are aligned on, the STEM probe and its
images, the contrast transfer function of an objective lens, and HREM images, of amorphous
samples and of crystals. These need no license, except thick crystals by the multislice method.

.. grid:: 1 2 3 3
   :gutter: 2

   .. grid-item-card:: The lens and its aberrations
      :link: lens
      :link-type: doc

      A lens's settings, the map its results are computed on, and its aberration function.

   .. grid-item-card:: Ronchigrams
      :link: ronchigram
      :link-type: doc

      The shadow image of a convergent probe through a thin amorphous sample.

   .. grid-item-card:: STEM probes and images
      :link: stem_probe
      :link-type: doc

      The probe and its diameter, the optimum settings, STEM images, the MTF and focal series.

   .. grid-item-card:: The contrast transfer function
      :link: ctf
      :link-type: doc

      The CTF of an objective lens, with its coherence envelopes.

   .. grid-item-card:: HREM images
      :link: hrem
      :link-type: doc

      Images of thin samples through the objective lens, and as a camera records them.

   .. grid-item-card:: Crystal potentials
      :link: crystals
      :link-type: doc

      Crystals in place of amorphous films, and maps that hold whole repeats of the crystal.

   .. grid-item-card:: Thick crystals: the multislice method :bdg-info:`Licensed`
      :link: multislice
      :link-type: doc

      The exit wave and CBED pattern of a crystal through its thickness, slice by slice.

The notebook :doc:`probe.ipynb <../../notebooks/probe>`, the step-by-step guide to this section,
explains the physics and runs each of these in turn, shown here with its plots and output.

The calculations come from the probe program by J. M. Zuo, now part of emaps.

.. toctree::
   :hidden:

   lens
   ronchigram
   stem_probe
   ctf
   hrem
   crystals
   multislice
   ../../notebooks/probe
