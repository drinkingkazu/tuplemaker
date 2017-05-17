#!/bin/bash

case `uname -n` in
    (uboonedaq-evb.fnal.gov)
    echo "setting up tuplemaker..."
    # datatype version
    dt_version=v6_19_01_e7_tuplemaker
    # set base dir structures
    export TUPLEMAKER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
    export UBOONEDAQ_HOME_DIR=$TUPLEMAKER_DIR/development_daq
    # set secret env
    source /data/kterao/larbys/sigh.sh
    # set ups
    source /uboonenew/setup_online.sh
    setup root v5_34_25 -q debug:e7
    setup postgresql v9_3_6 -q p279
    # set up clocal datatype
    if [ ! -d ${UBOONEDAQ_HOME_DIR} ]; then
	mkdir -p $UBOONEDAQ_HOME_DIR;
	setup-uboone-datatypes-source;
	cd $UBOONEDAQ_HOME_DIR/uboonedaq-datatypes/projects;
	git checkout $dt_version;
	mkdir -p $UBOONEDAQ_HOME_DIR/build-datatypes;
	cd $UBOONEDAQ_HOME_DIR/build-datatypes;
	source ../uboonedaq-datatypes/projects/ups/setup_for_development -d;
	env CC=gcc CXX=g++ FC=gfortran cmake -DCMAKE_INSTALL_PREFIX="${UBOONEDAQ_HOME_DIR}/install" -DCMAKE_BUILD_TYPE=${CETPKG_TYPE} "${CETPKG_SOURCE}";
	make -j;
    else
	cd /tmp;
	source $UBOONEDAQ_HOME_DIR/uboonedaq-datatypes/projects/ups/setup_for_development -d;
	cd -;
    fi
    cd $TUPLEMAKER_DIR;
    export PATH=$UBOONEDAQ_HOME_DIR/build-datatypes/bin:$PATH
    ;;
    (*)
    echo "tuplemaker is to be used on uboonedaq-evb only (needs that ups)"
esac


