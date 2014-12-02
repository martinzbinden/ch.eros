#!/bin/sh

sudo -s -u postgres

# source: PostGIS cookbook, 2014, 398ff.
psql  -c "CREATE ROLE gisusers NOLOGIN;"
psql  -c "CREATE ROLE superuser LOGIN SUPERUSER PASSWORD 'superuser'"
psql  -c "CREATE ROLE gis LOGIN SUPERUSER PASSWORD 'gis' IN ROLE gisusers;"
createdb postgis_cookbook -O gis;
createdb gis -O gis;
exit

cat > ~/.pgpass <<EOF
#hostname:port:database:username:password
localhost:5432:*:gis:gisHoch3
localhost:5432:*:superuser:supsup
EOF



psql  -h localhost -U superuser -d gis
ALTER SCHEMA public OWNER TO gis;
CREATE SCHEMA postgis;
CREATE EXTENSION postgis WITH SCHEMA postgis;
REASSIGN OWNED BY superuser TO gis;
SET search_path = public, postgis;
ALTER DATABASE gis SET search_path = public, postgis;

GRANT CONNECT, TEMP ON DATABASE gis TO GROUP gisusers;
GRANT ALL ON DATABASE gis TO gisusers;
GRANT INSERT ON spatial_ref_sys TO GROUP gisusers;
GRANT UPDATE, DELETE ON spatial_ref_sys TO GROUP gisusers;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO GROUP gisusers;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT INSERT ON TABLES TO GROUP gisusers;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT UPDATE ON TABLES TO GROUP gisusers;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT DELETE ON TABLES TO GROUP gisusers;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO GROUP gisusers;
GRANT ALL ON ALL TABLES IN SCHEMA public TO GROUP gisusers;

REVOKE ALL ON DATABASE gis FROM public;
GRANT USAGE ON SCHEMA postgis TO public;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA postgis TO public;
REVOKE ALL ON FUNCTION postgis_full_version() FROM public;
GRANT SELECT, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA postgis TO public;

CREATE ROLE map LOGIN PASSWORD 'mapmap';
GRANT CONNECT, TEMP ON DATABASE gis to map; 
GRANT EXECUTE ON FUNCTION postgis_full_version() TO map;
GRANT USAGE ON SCHEMA public TO map;
GRANT SELECT, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA public to map;
GRANT ALL ON TABLE ebk_parzellenplan,ebk_massnahmenplan,ebk_betrieb TO map;


\q

#raster2pgsql -a -I -C -F -e -Y -s 21781 -t 4375x3000  -M -l 4,8,16,32 /gis/geodata/ch.swisstopo.swissalti3d/swissALTI3D_*.tif ch_swisstopo_swissalti3d | psql -d gis


