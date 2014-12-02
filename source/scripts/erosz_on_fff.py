# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 18:32:59 2014

@author: martinz
"""

import sys
import os
import atexit
import grass.script as gscript

from grass.pygrass.gis import Gisdbase
from grass.pygrass.gis import Location
from grass.pygrass.gis import Mapset
from grass.pygrass.gis.region import Region
from grass.pygrass.vector.basic import Bbox
from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g, display as d
from grass.pygrass.modules import Module
import subprocess as sub



owsConnections = {}
owsConnections['default'] = {
    'dsn' : 'PG:host=523.riedackerhof.ch dbname=gis user=gis password=gisHoch3',
    'url' : 'https://523.riedackerhof.ch:4433/ows?',
    'username' :'gis',
    'password' : 'gisHoch3',
    'layers' : {
        'cultures' : 'ch_gelan_kulturen_2014',
        'fieldblocks' : 'ch_blw_erk2_feldblockkarte',
        'borders' : 'ch_swisstopo_kantone'
        },
    }
    
params = owsConnections['default']

dsn = params['dsn']

g.mapset(flags='c',mapset='solothurn')

v.in_ogr(dsn=dsn, layer=params['layers']['borders'], output='region', 
         where="kantonsnum = 11")
g.region(vect='region')
g.region(flags='p')

v.in_ogr(dsn=dsn, layer=params['layers']['cultures'], output='cultures', flags='r')
v.in_ogr(dsn=dsn, layer=params['layers']['fieldblocks'],output='fieldblocks', flags='r')
v.overlay(ainput='fieldblocks', binput = 'cultures', operator='not', output='fff')
