#!/bin/sh


## variables
export SOURCEDIR=$PWD/source
export GISBASE=~/gis

case "$1" in

    fachprogramm)
	$0 gisbase
	$0 grass7
	$0 grassaddon
	$0 qgisconfigure
	$0 chenyx06
	$0 mrsid
	;;

    gisbase)
        sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
        sudo aptitude update

        sudo aptitude install qgis qgis-plugin-grass python-qgis grass-gui r-cran-ggplot2 cmake   qgis-mapserver maptool gpsbabel-gui python-qt4-sql gdal-bin python-pip python-ipdb
	sudo pip install tabulate
        sudo mkdir $GISBASE/geodata -p
	sudo chown $USER: /gis/ -R
        echo "Task finished. Add your geodata in $GISBASE/geodata/"
        ;;


    grass7)
        ## install dependencies
        sudo aptitude install flex bison debhelper dpatch autoconf2.13 \
	autotools-dev python-dev g++ gcc gettext graphviz libcairo2-dev \
	libfftw3-dev libfreetype6-dev libglu1-mesa-dev libglw1-mesa-dev  \
	libncurses5-dev libproj-dev libreadline-dev libsqlite3-dev \
	libtiff5-dev libwxgtk2.8-dev  libxmu-dev libxmu-headers libxt-dev \
	mesa-common-dev proj-bin python-numpy python-wxgtk2.8 subversion \
	wx-common zlib1g-dev libqscintilla2-dev libcairo2-dev \
	xlibmesa-glu-dev libglu1-mesa-dev zlib1g-dev libcairo2-dev \
	libproj-dev postgresql-client postgresql-server-dev-all \
	libgdal1-dev postgis postgresql-9.3 libgeos-dev libgeos-3.4.2\
	netcdf-bin libnetcdf-dev checkinstall


        ## download and extract source code
        cd /tmp/
	if [ ! -d grass-7.0.0beta3 ]; then
	        wget http://grass.osgeo.org/grass70/source/grass-7.0.0beta3.tar.gz
        	tar xfz grass-7.0.0beta3.tar.gz
	fi
        cd grass-7.0.0beta3

        ## configure
        CFLAGS="-g -Wall -Werror-implicit-function-declaration -fno-common -Wextra -Wunused" CXXFLAGS="-g -Wall" \
        ./configure \
        --enable-64bit --enable-largefile=yes --with-wxwidgets \
        --without-tcltk --with-readline --with-freetype=yes \
        --with-freetype-includes="/usr/include/freetype2/" \
        --with-postgres=yes --with-postgresql=yes --with-postgres-includes="/usr/include/postgresql/" \
        --with-proj-share="/usr/share/proj" \
        --with-geos="/usr/bin/geos-config" --with-gdal -with-nls \
        --with-sqlite=yes --with-cxx  --with-cairo --with-python=yes --with-odbc=yes \
        --with-pthread --with-opengl-libs="/usr/include/GL" --with-netcdf \
        --x-includes="/usr/include/" --x-libraries="/usr/lib/"

        ## compile and install
        make -j2
        sudo checkinstall -y
	;;

    grassaddon)
        $SOURCEDIR/installscripts/install_fachprogramm_grasspart.sh
        $SOURCEDIR/installscripts/install_fachprogramm_qgispart.sh
	;;
    
    qgisconfigure)
	$SOURCEDIR/installscripts/configure_qgis.sh
	;;

    chenyx06)
        # source: http://www.camptocamp.com/actualite/mapserver-und-gdalogr-mit-proj4-8-0-und-dem-neuen-schweizer-referenzsystem/
        cd /tmp
        wget http://www.swisstopo.admin.ch/internet/swisstopo/en/home/products/software/products/chenyx06.parsys.00011.downloadList.70576.DownloadFile.tmp/chenyx06ntv2.zip
        unzip chenyx06ntv2.zip
        sudo cp CHENYX06a.* /usr/share/proj/
        ;;

    mrsid)
        wget http://ppa.launchpad.net/ubuntugis/ppa/ubuntu/pool/main/libg/libgdal-mrsid/libgdal-mrsid-src_1.9.0-2~oneiric1_all.deb
        sudo gdebi libgdal-mrsid-src_1.9.0-2~oneiric1_all.deb
        sudo gdal-mrsid-build /opt/Geo_DSDK-7.0.0.2167.linux.x86-64.gcc41
        sudo ln -s /usr/lib/gdalplugins/1.9 /usr/lib/gdalplugins/1.10
        sudo ln -s /usr/lib/gdalplugins/1.9 /usr/lib/gdalplugins/1.11
        ;;

    latex)
        aptitude install texlive-base  texlive-doc-de texlive-lang-german texlive-bibtex-extra texworks texworks-help-en  biber texlive-latex-base-doc texworks-scripting-python geany-plugin-latex
        ;;

    rstudio)
        aptitude install r-recommended r-doc-html
        echo "get rstudio from  http://www.rstudio.com/products/rstudio/download/ and save it to /tmp."
        read -p "Press [Enter] key when done..." fackEnterKey
        gdebi /tmp/rstudio*.deb
        echo "Task rstudio finished"
        ;;

    googlechrome)
        apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7FAC5991
        cat > /etc/apt/sources.list.d/google-chrome.list <<EOF
deb http://dl.google.com/linux/chrome/deb/ stable main
EOF
        aptitude update
        aptitude install google-chrome-stable
        ;;


    x2goclient)
        aptitude install x2goclient 
        ;;

    wine)
        sudo aptitude install winetricks wine64-bin
        ;;

    usefulprogs)
        aptitude install orpie vim-gtk renameutils rsync lftp ecryptfs-utils python-software-properties network-manager-vpnc-gnome dropbox geany geany-plugin-addons fuseiso fuse-zip clipit
        ;;



    *)
        echo "Installation shell script utility \n"
	echo "DANGER: may break your QGIS installation or configuration!"
	echo "Run as user with sudo rights \n"
        echo "Usage: $0 {gisbase|grass7|grass7addons|postgis|mapserv|chenyx06|mrsid|...|}"
        echo "  fachprogramm  : Install Fachprogramm Bodenerosion and recommended tools."
        echo "  gisbase  : Install QGIS and some other GIS tools. Run first!"
        echo "  grass7  : Build and install GRASS GIS 7 from source."
        echo "  grassaddon  : Install Fachprogramm addon for GRASS GIS 7."
        echo "  qgisconfigure  : Make changes to QGIS to enable GRASS GIS 7 addon."
        echo "  chenyx06  : Download and install CH1903LV03 to CH1903+/LV95 datum transformation files."
        echo "  mrsid  : Build and install MrSID-format GDAL plugin."
	echo "  wine  : for running some windows progs directly (e.g. Erosion V2.02)"
	echo "    "
	echo "    "
	echo "Other useful tools for workstations: (not part of fachprogramm)   "
	echo "  usefulprogs  : some mostly tiny but really useful tools"
	echo "  x2goclient  : remote X sessions "
	echo "  latex  : LaTeX (maybe want to try sharelatex.com instead?)"
	echo "  rstudio  : statistics program"
	echo "  googlechrome  : probably best browser for sharelatex.com"
	;;

esac
