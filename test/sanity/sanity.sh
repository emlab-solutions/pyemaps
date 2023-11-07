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
    python3 ./feature_sanity.py ; 
else 
    echo y | python3 -m pyemaps -cp ;
    # python3 ./pyemaps_samples/si_csf.py ;
    # python3 ./pyemaps_samples/powder.py ;
    # python3 ./pyemaps_samples/si_dif.py ;
    # python3 ./pyemaps_samples/si_bloch.py ;
    # python3 ./pyemaps_samples/si_stereo.py ;
    # python3 ./test/sanity/feature_sanity.py
    # rm -rf pyemaps_samples ;
    python3 ./pyemaps_samples/si_csf.py
    python3 ./pyemaps_samples/powder.py
    python3 ./pyemaps_samples/si_dif.py
    python3 ./pyemaps_samples/si_bloch.py
    python3 ./pyemaps_samples/si_lacbed.py
    python3 ./pyemaps_samples/si_rawblochimgs.py
    python3 ./pyemaps_samples/si_constructor.py
    python3 ./pyemaps_samples/si_stereo.py
    python3 ./pyemaps_samples/si_scm.py
    python3 ./pyemaps_samples/al_dpgen.py
    python3 ./pyemaps_samples/al_ediom.py
    python3 test/sanity/feature_sanity.py
    @REM performance test - all includes all types: dif, bloch and stereo
     python3 test/sanity/run_perf_test.py -r all
    @REM unit test: EMC SIMC class basic function tests
     python3 test/unittests/emc/test1.py
     python3 test/unittests/package_test/type_test.py
     python3 test/unittests/kdif/sanity_doc.py
     python3 test/unittests/bloch/si_bloch_docs.py
     python3 test/unittests/bloch/disk_size.py
    # rm -rf pyemaps_samples
fi
