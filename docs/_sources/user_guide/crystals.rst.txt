Crystals
========

All pyEMAPS simulations and calculations start from its 
:py:obj:`Crystal class <pyemaps.crystals.Crystal>`. 
To import the class:

.. code-block:: python

   from pyemaps import Crystal

Before starting pyEMAPS diffraction simulation, the crystal
object must be created and data loaded. The following example
creates a *si* crystal object by loading it from pyEMAPS 
built-in database for Silicon crystal using 
:py:obj:`from_builtin <pyemaps.crystals.Crystal.from_builtin>` 

.. code-block:: python
 
    from pyemaps import Crystal as cr  

    si = cr.from_builtin('Silicon')

.. note::
   
   Pyemaps also provides methods for creating crystal objects from other 
   data sources, including imports from CIF, JSON formatted files. Go to 
   :py:obj:`Crystal class <pyemaps.crystals.Crystal>`
   for more details.


Once a crystal object is created and loaded, it is ready for simulations
and calculations.

Built-in crystals
-----------------

To see all crystal names in the *pyEMAPS* built-in database, call 
:py:obj:`list_all_builtin_crystals <pyemaps.crystals.Crystal.list_all_builtin_crystals>`:

.. code-block:: python

   from pyemaps import Crystal as cr
   cr.list_all_builtin_crystals()

Current list of built-in crystals in *pyEMAPS*:

::

   'Aluminium', 'AluminiumOxide', 'Aluminium_FCC', 'BariumTitanate_180k', 'BariumTitanate_270k', 
   'BariumTitanate_Tetra', 'Boron_Tetra', 'CadmiumSelenide_Hex', 'CadmiumSulfide_Cubic', 
   'CadmiumSulfide_Hex', 'Chromium_BCC', 'CopperOxide', 'Copper_FCC', 'Cu2O_Cuprite', 'Diamond', 
   'ErbiumPyrogermanate', 'FePd_Tetra', 'FeS2_Pyrite', 'GalliumAntimonide', 'GalliumArsenide', 
   'GalliumNitride', 'Germanium', 'Gold_FCC', 'IndiumArsenide', 'LaMnO3', 'LeadZirconateTitanate', 
   'Li2MnO3', 'limno2', 'NaFeO2', 'Nb3Sn', 'Silicon', 'StrontiumTitanate', 'TelluriumDioxide', 
   'TinDioxide_RT', 'TitaniumDioxide_Anatase', 'TitaniumDioxide_Rutile', 'TungstenDiselenide', 
   'VanadiumDioxide_RT', 'ZincOxide', 'Zinc_HCP', 'ZirconiumNitride'

Constructing crystal structures
-------------------------------

*pyEMAPS*' :py:obj:`generateMxtal <pyemaps.crystals.Crystal.generateMxtal>`
function produces .XYZ file that can be improted into 
`Jmol <http://www.jmol.org/>`_ and visualize the 
crystal in 3D atomic structure. The following is an example of such rendering:


.. image:: https://github.com/emlab-solutions/imagepypy/raw/main/mxtal01.png
