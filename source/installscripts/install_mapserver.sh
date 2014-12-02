
cd /gis/geodata
gdaltindex -write_absolute_path tindex/r ch.blw.erk2.r/r_*.tif
gdaltindex -write_absolute_path tindex/k ch.blw.erk2.k/k_*.tif
gdaltindex -write_absolute_path tindex/erosz ch.blw.erk2.erosz/eros_z*.tif
gdaltindex -write_absolute_path tindex/pk15 ch.swisstopo.pk25/komb*.tif
gdaltindex -write_absolute_path tindex/swissalti3d ch.swisstopo.swissalti3d/swissALTI3D*.tif
gdaltindex -write_absolute_path tindex/hillshade ch.swisstopo.swissalti3d.hillshade/swissALTI3D*.tif
gdaltindex -write_absolute_path tindex/chillshade ch.swisstopo.swissalti3d.color-hillshade/swissALTI3D*.tif
gdaltindex -write_absolute_path tindex/swissimage2004 ch.swisstopo.swissimage.2004/1*.sid

for i in tindex/*; do shptree $i/*.shp; done
cd -


