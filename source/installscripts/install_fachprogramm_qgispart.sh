# install grass add-ons (symlinks)

sudo mv /usr/share/qgis/grass/config/default.qgc /usr/share/qgis/grass/config/default.qgc.orig
sudo ln  -s $SOURCEDIR/qgis/default.qgc  /usr/share/qgis/grass/config/default.qgc
sudo ln  -s $SOURCEDIR/qgis/g.gui.soilloss.qgm  /usr/share/qgis/grass/modules/
sudo ln  -s $SOURCEDIR/qgis/g.gui.soilloss.1.png  /usr/share/qgis/grass/modules/
mkdir ~/.qgis2/project_templates/ -p
ln  -s $SOURCEDIR/qgis/FachprogrammErosionsberatung.qgs ~/.qgis2/project_templates/

sudo mkdir /gis/
sudo chmod 777 /gis/


