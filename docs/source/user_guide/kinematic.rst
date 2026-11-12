Kinematic diffraction
=====================

.. code-block:: python

   from pyemaps import Crystal             # pyemaps crystal module
   from pyemaps import DPList, showDif     # helper modules

   if __name__ == '__main__':              # needed in scripts, see the note below
       si = Crystal.from_builtin('Silicon')    # load Silicon from the built-in database
       emc, si_dp = si.generateDP()            # generate a kinematic diffraction pattern
                                               # emc: the microscope and simulation controls used
                                               # si_dp: the diffraction pattern
       print(si_dp)                            # raw representation of the pattern

       dpl = DPList('Silicon')                 # a list to hold the results
       dpl.add(emc, si_dp)                     # add more if desired

       showDif(dpl, bClose=False)              # show the diffraction pattern

.. note::

   Keep the ``if __name__ == '__main__':`` line in scripts. *showDif*, *showBloch* and
   *showStereo* draw in a separate process, and on Windows that process re-runs your script.
   Without the line, Python stops with a ``RuntimeError`` about the bootstrapping phase.
   Jupyter notebooks don't need it.


:py:meth:`~pyemaps.crystals.Crystal.generateDP` returns the microscope and simulation controls
it used (*emc*) and the kinematic diffraction pattern (*si_dp*), a
:py:class:`~pyemaps.kdiffs.diffPattern`. Called without arguments, it uses the default controls.
For all its parameters, see :py:meth:`~pyemaps.crystals.Crystal.generateDP`.

:py:func:`~pyemaps.display.showDif`, from the :py:mod:`display module <pyemaps.display>`, shows
the patterns in a :py:class:`DPList <pyemaps.kdiffs.Diffraction>`. Its options show or hide the
Kikuchi lines (*kShow*), the Miller indices of the diffracted beams (*iShow*) and the non-default
controls (*cShow*).

Displaying a series of patterns
-------------------------------

This example makes CBED patterns of Silicon at six zone axes, with a camera length of 2500 mm.
It runs the simulations in parallel processes, then shows the patterns as a table:

.. image:: ../_static/images/dif_table.png
   :alt: Kinematic CBED patterns of Silicon at six zone axes
   :target: ../_static/images/dif_table.png

.. code-block:: python

    from pyemaps import DEF_MODE
    from pyemaps import EMC

    MAX_PROCWORKERS = 4

    def generate_difs(name = 'Silicon', mode = DEF_MODE):
        
        from pyemaps import DPList
        import concurrent.futures
        from pyemaps import Crystal as cryst

        cr = cryst.from_builtin(name)

        zlist=[(0,0,1), (1,1,2), (1,1,1),
               (1,3,3), (0,1,2), (0,1,3)]
        
        fs=[]

        difs = DPList(name, mode = mode)

        emclist =[EMC(zone=z, cl=2500) for z in zlist] 

        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCWORKERS) as e:

            for ec in emclist:
                fs.append(e.submit(cr.generateDP, mode=mode, em_controls = ec))

            for f in concurrent.futures.as_completed(fs):
                try:
                    emc, diffP = f.result()
                    difs.add(emc, diffP)
                    
                except Exception as e:
                    print(f'{f} generated an exception: {e}')
                    exit(1)
        difs.sort()
        return difs

    if __name__ == '__main__':
        
        from pyemaps import showDif

        dpl = generate_difs(mode = 2)
        showDif(dpl, cShow = True, iShow=True, layout='table', bSave = True)
