#!/bin/bash
# setup default user configuration of QGIS, prepare for Fachprogramm Erosionsrisiko
echo $SHELL

echo Geodatenserver Fachprogramm Erosionsberatung
echo -n Benutzername:
read USR
echo -n Passwort:
read -s PSWD

echo " "
echo swisstopo geoservices WMS:
echo Gratisregistration: http://www.toposhop.admin.ch/de/shop/products/geoservice/swisstopoWMS
echo -n Benutzername:
read SWISSTOPOUSR

echo -n Passwort:
read -s SWISSTOPOPSWD

echo ""

CONFFILE="$HOME/.config/QGIS/QGIS2.conf"
TMPFILE=`tempfile`

echo Mache Sicherheitskopie von $CONFFILE
cp $CONFFILE $CONFFILE.bak

DBS="
gis
"
cat << EOF >> "$TMPFILE"
[PostgreSQL]
connections\selected=523.riedackerhof.ch
EOF

for DBNAME in $DBS ; do
    cat << EOF >> "$TMPFILE"
connections\\523.riedackerhof.ch $DBNAME\\service=
connections\\523.riedackerhof.ch $DBNAME\\host=523.riedackerhof.ch
connections\\523.riedackerhof.ch $DBNAME\\database=$DBNAME
connections\\523.riedackerhof.ch $DBNAME\\port=5432
connections\\523.riedackerhof.ch $DBNAME\\username=$USR
connections\\523.riedackerhof.ch $DBNAME\\password=$PSWD
connections\\523.riedackerhof.ch $DBNAME\\publicOnly=false
connections\\523.riedackerhof.ch $DBNAME\\allowGeometrylessTables=false
connections\\523.riedackerhof.ch $DBNAME\\sslmode=3
connections\\523.riedackerhof.ch $DBNAME\\saveUsername=true
connections\\523.riedackerhof.ch $DBNAME\\savePassword=true
connections\\523.riedackerhof.ch $DBNAME\\estimatedMetadata=false
EOF
done
 

cat << EOF >> $TMPFILE
[General]
Themes=default
IconSize=16

[Plugins]
libgrassplugin=true

[GRASS]
gisbase=/gis/grass
lastGisdbase=/gis/grass
lastMapset=fpeb
region\on=true

[PythonPlugins]
GeoSearch=true

[UI]
recentProjectionsProj4="+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +towgs84=674.4,15.1,405.3,0,0,0,0 +units=m +no_defs", "+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs"
recentProjectionsAuthId=EPSG:21781, USER:100000
recentProjectsList=/home/gis/.qgis2/project_templates/FachprogrammErosionsberatung.qgs, /home/gis/gis/ch.eros.bth/source/qgis/FachprogrammErosionsberatung.qgs
lastProjectDir=/home/gis/gis/ch.eros.bth/source/qgis

[qgis]
showTips=false
connections-wms\523.riedackerhof.ch\url=https://523.riedackerhof.ch:4433/ows?
connections-wms\523.riedackerhof.ch\ignoreGetMapURI=false
connections-wms\523.riedackerhof.ch\ignoreAxisOrientation=false
connections-wms\523.riedackerhof.ch\invertAxisOrientation=false
connections-wms\523.riedackerhof.ch\smoothPixmapTransform=false
connections-wms\523.riedackerhof.ch\dpiMode=2
connections-wms\523.riedackerhof.ch\ignoreGetFeatureInfoURI=false
connections-wms\523.riedackerhof.ch\referer=
WMS\523.riedackerhof.ch\username=$USR
WMS\523.riedackerhof.ch\password=$PSWD
connections-wms\selected=523.riedackerhof.ch
connections-wfs\523.riedackerhof.ch\url=https://523.riedackerhof.ch:4433/wfs?
connections-wfs\523.riedackerhof.ch\referer=
WFS\523.riedackerhof.ch\username=$USR
WFS\523.riedackerhof.ch\password=$PSWD
connections-wfs\selected=523.riedackerhof.ch
connections-wcs\523.riedackerhof.ch\url=https://523.riedackerhof.ch:4433/ows?
connections-wcs\523.riedackerhof.ch\ignoreGetMapURI=false
connections-wcs\523.riedackerhof.ch\ignoreAxisOrientation=false
connections-wcs\523.riedackerhof.ch\invertAxisOrientation=false
connections-wcs\523.riedackerhof.ch\smoothPixmapTransform=false
connections-wcs\523.riedackerhof.ch\dpiMode=7
connections-wcs\523.riedackerhof.ch\referer=
WCS\523.riedackerhof.ch\username=$USR
WCS\523.riedackerhof.ch\password=$PSWD
connections-wcs\selected=523.riedackerhof.ch
connections-wfs\wfs.geo.admin.ch\url=http://wfs.geo.admin.ch/
connections-wfs\wfs.geo.admin.ch\referer=
WFS\wfs.geo.admin.ch\username=
WFS\wfs.geo.admin.ch\password=
connections-wms\wms.geo.admin.ch\url=http://wms.geo.admin.ch/
connections-wms\wms.geo.admin.ch\ignoreGetMapURI=false
connections-wms\wms.geo.admin.ch\ignoreAxisOrientation=false
connections-wms\wms.geo.admin.ch\invertAxisOrientation=false
connections-wms\wms.geo.admin.ch\smoothPixmapTransform=false
connections-wms\wms.geo.admin.ch\dpiMode=2
connections-wms\wms.geo.admin.ch\ignoreGetFeatureInfoURI=false
connections-wms\wms.geo.admin.ch\referer=
connections-wms\wms.swisstopo.admin.ch\url=https://wms.swisstopo.admin.ch/
connections-wms\wms.swisstopo.admin.ch\ignoreGetMapURI=false
connections-wms\wms.swisstopo.admin.ch\ignoreAxisOrientation=false
connections-wms\wms.swisstopo.admin.ch\invertAxisOrientation=false
connections-wms\wms.swisstopo.admin.ch\smoothPixmapTransform=false
connections-wms\wms.swisstopo.admin.ch\dpiMode=7
connections-wms\wms.swisstopo.admin.ch\ignoreGetFeatureInfoURI=false
connections-wms\wms.swisstopo.admin.ch\referer=
WMS\wms.swisstopo.admin.ch\username=$SWISSTOPOUSR
WMS\wms.swisstopo.admin.ch\password=$SWISSTOPOPSWD
newProjectDefault=true
projectTemplateDir=/home/martinz/.qgis2/project_templates
customEnvVarsUse=true
customEnvVars="prepend|GRASS_ADDON_PATH=$HOME/.grass6/addons", "prepend|PATH=$HOME/.grass6/addons:"

[Projections]
defaultBehaviour=prompt
layerDefaultCrs=EPSG:21781
otfTransformAutoEnable=true
otfTransformEnabled=false
projectDefaultCrs=EPSG:21781
showDatumTransformDialog=false

EOF

tail -n +3 "$CONFFILE" > "$TMPFILE".b
cat "$TMPFILE" "$TMPFILE".b > "$CONFFILE"
rm -f "$TMPFILE" "$TMPFILE".b

echo "Anpassungen von QGIS beendet! QGIS kann jetzt gestartet werden."
