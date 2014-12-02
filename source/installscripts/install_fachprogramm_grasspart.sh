# install grass add-ons (symlinks)
mkdir -p ~/.grass7/addons/scripts/
mkdir -p ~/.grass6/addons/

SOURCEDIR=$PWD/source

ln -s $SOURCEDIR/grass-addons/grass7/raster/g.gui.soilloss/g.gui.soilloss.py ~/.grass7/addons/scripts/g.gui.soilloss
ln -s $SOURCEDIR/grass-addons/grass7/raster/r.in.wcs/r.in.wcs.py ~/.grass7/addons/scripts/r.in.wcs
ln -s $SOURCEDIR/grass-addons/grass7/raster/r.soilloss/r.soilloss.bare.py ~/.grass7/addons/scripts/r.soilloss.bare
ln -s $SOURCEDIR/grass-addons/grass7/raster/r.soilloss/r.soilloss.cpmax.py ~/.grass7/addons/scripts/r.soilloss.cpmax
ln -s $SOURCEDIR/grass-addons/grass7/raster/r.soilloss/r.soilloss.grow.py ~/.grass7/addons/scripts/r.soilloss.grow
ln -s $SOURCEDIR/grass-addons/grass7/raster/r.soilloss/r.soilloss.reclass.py ~/.grass7/addons/scripts/r.soilloss.reclass
ln -s $SOURCEDIR/grass-addons/grass7/raster/r.soilloss/r.soilloss.stats.py ~/.grass7/addons/scripts/r.soilloss.stats
ln -s $SOURCEDIR/grass-addons/grass7/raster/r.soilloss/r.soilloss.update.py ~/.grass7/addons/scripts/r.soilloss.update

ln -s $SOURCEDIR/grass-addons/grass6/raster/g.gui.soilloss/g.gui.soilloss.py  ~/.grass6/addons/g.gui.soilloss

mkdir /gis/grass 
export GRASS_BATCH_JOB=$SOURCEDIR/installscripts/initializegrass_batchjob.sh
grass70 -c EPSG:21781 /gis/grass/LV03  



