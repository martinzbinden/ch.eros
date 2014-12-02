CREATE TABLE ebk_parzellenplan (
  pk SERIAL PRIMARY KEY NOT NULL,
  id INTEGER NOT NULL,
  name character varying(255),
  betrieb_id INTEGER NOT NULL,
  cfactor REAL,
  pfactor REAL,
  kfactor REAL,
  p_T REAL,
  p_U REAL,
  p_st REAL,
  p_H REAL,
  flaeche REAL,
  bemerkung character varying(255)
);
SELECT AddGeometryColumn(
  'ebk_parzellenplan', 'geom',
  21781, 'POLYGON','2');
CREATE INDEX ebk_parzellenplan_gix ON ebk_parzellenplan USING GIST (geom);
  
CREATE TABLE ebk_massnahmenplan (
  pk SERIAL PRIMARY KEY NOT NULL,
  id INTEGER NOT NULL,
  bezeichnung  character varying(255),
  betrieb_id INTEGER NOT NULL,
  cfactor REAL,
  pfactor REAL,
  barrier INTEGER,
  flaeche REAL,
  bemerkung  character varying(255)
);
SELECT AddGeometryColumn(
  'ebk_massnahmenplan', 'geom',
  21781, 'POLYGON','2');
CREATE INDEX ebk_massnahmenplan_gix ON ebk_massnahmenplan USING GIST (geom);
