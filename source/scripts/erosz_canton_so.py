# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 18:32:59 2014

Purpose: Bodenabtragspotenzial für eine Gemeinde in der Schweiz berechnen.

@author: Martin Zbinden
"""

## USER SETTINGS
# Einstellungen für Serververbindung
config_name = 'default'
username='gis' 
password = 'gisHoch3'

#BFS Gemeindenummer
#BFS Gemeindenummer
bfsnum='2461'

owsConnections = {}
owsConnections['default'] = {
    'srs' : 'EPSG:21781',
    'url' : 'https://523.riedackerhof.ch:4433/ows?',
    'username' :'',
    'password' : '',
    'coverages' : {
        'soillossbare' : 'ch.blw.erk2.erosz',
        'kfactor' : 'ch.blw.erk2.k',
        'rfactor' : 'ch.blw.erk2.r',
        'elevation' : 'ch.swisstopo.swissalti3d'
        },
    'dsn' : 'PG:host=523.riedackerhof.ch dbname=gis',
    'layers' : {
        'fieldblocks' : 'ch_blw_erk2_feldblockkarte',
        'cultures' : 'ch_gelan_kulturen_2014',
        'parcels' : 'ebk_parzellenplan',
        'measures' : 'ekb_massnahmenplan',
        'kanton' : 'ch_swisstopo_kantone',
        'gemeinde' : 'ch_swisstopo_gemeinden'
        },
    'colnames' : {
        'cfactor' : 'cfactor',
        'pfactor' : 'pfactor',
        'kfactor' : 'kfactor'
        }
    }
    
params = owsConnections['default']

## END USER SETTINGS
import os
import grass.script as gscript
from grass.pygrass.modules import Module
from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g, display as d


params['username'] += username
params['password'] += password
dsn = params['dsn'] + ' user=%s password=%s' %(username,password)

g.mapset(flags='c',mapset='Gemeinde_'+bfsnum)

v.in_ogr(dsn=dsn, layer=params['layers']['gemeinde'], output='region', 
         where='bfs_nummer = 2461',overwrite=True)
g.region(vect='region',flags='a',res='2')
g.region(flags='p')

v.in_ogr(dsn=dsn, layer=params['layers']['fieldblocks'], output='fieldblocks', flags='r')

rinwcs = Module("r.in.wcs")
rinwcs.inputs.url=params['url']
rinwcs.inputs.username=username
rinwcs.inputs.password=password

rinwcs(coverage=params['coverages']['elevation'])
rinwcs(coverage=params['coverages']['rfactor'])
rinwcs(coverage=params['coverages']['kfactor'])

rsoillossbare = Module("r.soilloss.bare")
rsoillossbare.inputs.flowaccmethod='r.terraflow'
rsoillossbare.inputs.map='fieldblocks'
rsoillossbare.inputs.overwrite=True
rsoillossbare.flags.r=True

rsoillossbare(soillossbare='soillossbare', elevation='ch.swisstopo.swissalti3d', kfactor='ch.blw.erk2.k', rfactor='ch.blw.erk2.r')