#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# MODULE:   r.soilloss.stats
#
# AUTHOR(S):  Martin Zbinden
#
# PURPOSE: calculate and print out some simple raster zonal statistics
#
#           @return some statistical outputs (table-like formats)
#
#
# VERSION:  0.2
#
# DATE:     So Jun 8 14:00:00 CET 2014
#
'''
#%Module
#%  description: Calculate statistics of soilloss raster maps.
#%    keywords: Raster, hydrology, erosion, statistics
#%end

#%option G_OPT_R_INPUT
#%key: soilloss
#%description: Raster map with soilloss
#%end

#%option G_OPT_V_MAP
#%key: map
#%description: Name of vector map with parcel data
#%required: yes
#%end

#%option G_OPT_DB_COLUMN
#%key: parcelnumcol
#%description: Column with parcel numbers
#%required: yes
#%end

#%flag
#%key: l
#%description: Export results as latex table
#%end

#%flag
#%key: h
#%description: Frequency of classes (histogram, for classified raster)
#%guisection: Inputs
#%end

import sys
import grass.script as gscript
from grass.pygrass.modules.shortcuts import raster as r, vector as v
from grass.pygrass.modules import Module
    
def main():
    soilloss = options['soilloss']
    soilloss3 = soilloss # + '.3'
    map = options['map']
    parcelnumcol = options['parcelnumcol']
    flag_l = flags['l']
    flag_h = flags['h']
  
    quiet = True
    if gscript.verbosity() > 2:
        quiet=False

    zones = map.split('@')[0] + '.zones'
    v.to_rast( input=map, use='attr', attrcolumn=parcelnumcol,
              output=zones, quiet=quiet)
    
    
    def printStats(table, tablefmt='simple'):
        try:
            from tabulate import tabulate
        except:
            gscript.warning('Install tabulate for pretty printing tabular output ($ pip install tabulate). Using pprint instead...')
            from pprint import pprint
            pprint(statout)
        print tabulate(table,headers='firstrow',tablefmt=tablefmt)
         
    if not flag_h:
        runivar = r.univar(map=soilloss, zones=zones, flags='t', stdout=gscript.PIPE)
        rstats = runivar.outputs.stdout.strip().split('\n')
        #show all available values columns
        #rstats[0].split('|')
        rstatout = []
        for line in range(len(rstats)):
            lineout = []
            for i in (0,7,9,4,5): 
                lineout += (rstats[line].split('|')[i],)
            rstatout.append(lineout)
            
        if flag_l: printStats(rstatout, tablefmt='latex')
        else: printStats(rstatout)
        
    if flag_h:
            
        r.report(map=(zones,soilloss3),units='p',flags='')
      
        
if __name__ == "__main__":
    options, flags = gscript.parser()
    sys.exit(main())


