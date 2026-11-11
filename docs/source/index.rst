:html_theme.sidebar_secondary.remove: true

.. container:: pe-hero

   .. rubric:: pyEMAPS
      :heading-level: 1

   .. rst-class:: pe-lead

   Electron diffraction simulation and crystallography in Python: kinematic and
   dynamical (Bloch wave) diffraction, stereodiagrams, powder patterns, structure
   factors, supercells and 4D-STEM pattern indexing.

   .. container:: pe-install

      .. code-block:: console

         pip install pyemaps

   .. rst-class:: pe-meta

   Version |release| · Python 3.12–3.15 · Windows 64-bit · Free base features, licensed 4D-STEM

   .. container:: pe-buttons

      .. button-ref:: getting_started
         :ref-type: doc
         :color: primary
         :shadow:

         Get started

      .. button-ref:: examples
         :ref-type: doc
         :color: primary
         :outline:

         Browse examples

      .. button-ref:: api/index
         :ref-type: doc
         :color: primary
         :outline:

         API reference

What you can simulate
---------------------

.. container:: pe-features

   .. grid:: 1 2 3 3
      :gutter: 3

      .. grid-item-card:: Kinematic diffraction
         :img-top: _static/images/si_dif1.png
         :link: user_guide/kinematic
         :link-type: doc

         Spot patterns, Kikuchi and HOLZ lines, and CBED disks for any zone axis.

      .. grid-item-card:: Dynamic diffraction
         :img-top: _static/images/bloch_table.png
         :link: user_guide/dynamic
         :link-type: doc

         Bloch-wave CBED and large-angle CBED, with the scattering matrix and thickness series.

      .. grid-item-card:: Stereodiagrams
         :img-top: _static/images/si_stereo.png
         :link: user_guide/stereo
         :link-type: doc

         Indexed stereographic projections for any orientation.

      .. grid-item-card:: Powder diffraction
         :img-top: _static/images/powder.png
         :link: examples
         :link-type: doc

         Electron powder profiles, with and without absorption.

      .. grid-item-card:: Crystal structures
         :img-top: _static/images/mxtal01.png
         :link: user_guide/crystals
         :link-type: doc

         41 built-in crystals, CIF import, structure factors and supercells.

      .. grid-item-card:: 4D-STEM indexing :bdg-info:`Licensed`
         :img-top: _static/images/ediom_img1.png
         :link: user_guide/indexing
         :link-type: doc

         Index experimental patterns against a simulated database to find orientation and phase.

Your first diffraction pattern
------------------------------

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item::

      Load Silicon from the built-in library and simulate its kinematic diffraction pattern:

      .. code-block:: python

         from pyemaps import Crystal, DPList, showDif

         if __name__ == '__main__':
             si = Crystal.from_builtin('Silicon')
             emc, dp = si.generateDP()

             dpl = DPList('Silicon')
             dpl.add(emc, dp)
             showDif(dpl)

      Continue with :doc:`getting_started`.

   .. grid-item::

      .. image:: _static/images/si_dif2.png
         :alt: Kinematic diffraction pattern of Silicon
         :width: 360px
         :align: center

Learn more
----------

.. grid:: 1 2 4 4
   :gutter: 2

   .. grid-item-card:: :fas:`rocket` Get Started
      :link: getting_started
      :link-type: doc

      Install, check the setup and run a first simulation.

   .. grid-item-card:: :fas:`book` User Guide
      :link: user_guide/index
      :link-type: doc

      Each feature explained, with examples.

   .. grid-item-card:: :fas:`images` Examples
      :link: examples
      :link-type: doc

      Sample scripts with their output.

   .. grid-item-card:: :fas:`code` API Reference
      :link: api/index
      :link-type: doc

      Every class and function.

pyEMAPS is developed by `EMLab Solutions <https://www.emlabsolutions.com>`_. The simulations
follow the kinematic and dynamical theory in Spence and Zuo, *Electron Microdiffraction*
(Plenum, 1992). Questions: support@emlabsoftware.com.

.. toctree::
   :hidden:

   Get Started <getting_started>
   User Guide <user_guide/index>
   Examples <examples>
   API Reference <api/index>
   Help <help>
