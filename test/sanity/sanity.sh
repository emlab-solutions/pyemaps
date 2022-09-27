#!/bin/sh
python3 -m pyemaps -s ;
python3 -m pyemaps -c ;
python3 -m pyemaps -v ;

if [ $1 = "local"] ; then 
    echo n | python3 -m pyemaps -cp ;
    python3 ./si_csf.py ;
    python3 ./powder.py ;
    python3 ./si_dif.py ;
    python3 ./si_bloch.py ;
    python3 ./import_calc_sanity ; 
else 
    echo y | python3 -m pyemaps -cp ;
    python3 ./pyemaps_samples/si_csf.py ;
    python3 ./pyemaps_samples/powder.py ;
    python3 ./pyemaps_samples/si_dif.py ;
    python3 ./pyemaps_samples/si_bloch.py ;
    python3 test/sanity/import_calc_sanity ;
    rm -rf pyemaps_samples ;
fi
