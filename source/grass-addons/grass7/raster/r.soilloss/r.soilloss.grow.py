#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# MODULE:   r.soilloss.grow
#
# AUTHOR(S):  Martin Zbinden
#
# PURPOSE:  Multiplicate soilloss on bare soil with C- and P-factors
#           to receive soilloss for grown soil.
#
#           @return soillossgrow raster map
#
#
# VERSION:  0.2
#
# DATE:     So Jun 8 14:00:00 CET 2014
#
'''
#%Module
#%  description: Calculate soilloss t/(ha*a) for grown soil. Instead of input raster maps constant values can also be given.
#%    keywords: Raster, hydrology, erosion, grown soil
#%end

#%option G_OPT_R_INPUT
#%key: soillossbare
#%description: Raster map with soilloss for bare soil
#%end

#%option G_OPT_R_OUTPUT
#%key: soillossgrow
#%description: Output raster map with soilloss for grown soil
#%end

#%option G_OPT_R_INPUT
#%key: cfactor
#%description: Raster map with C factor (crop and management)
#%required: no
#%guisection: Inputs
#%end

#%option G_OPT_R_INPUT
#%key: pfactor
#%description: Raster map with P factor (soil preservation measures)
#%required: no
#%guisection: Inputs
#%end

#%option G_OPT_V_MAP
#%key: map
#%description: Name of vector map with parcel data
#%guisection: Inputs
#%required: no
#%end

#%option G_OPT_DB_COLUMNS
#%key: factorcols
#%guisection: Inputs
#%description: Choose factor columns to use (C, P)
#%end

import sys
import grass.script as gscript
from grass.pygrass.modules.shortcuts import raster as r, vector as v

colorrules = {}
# (c) Gisler 2010   
colorrules['soillossgrow'] = '\n '.join([
    "0   69:117:183",
    "1  115:146:185",
    "2  163:179:189",
    "4  208:216:193",
    "7.5  255:255:190",
    "10  252:202:146",
    "15  245:153:106",
    "20  233:100:70",
    "30  213:47:39",
    "300  213:47:39"
    ])
    

    
def main():
    soillossbare = options['soillossbare']
    soillossgrow = options['soillossgrow']
    cfactor = options['cfactor']
    pfactor = options['pfactor']    
    map = options['map']
    factorcols = options['factorcols'].split(',')
    
    quiet = True
    if gscript.verbosity() > 2:
        quiet=False

    if not (cfactor or pfactor):
        if not map:
            gscript.fatal('Please give either factor raster map(s) or vector map with factor(s)')
        elif not factorcols:
            gscript.fatal("Please give 'factorcols' (attribute columns with factor(s))  for <%s>" %map)
        
        factors = ()
        for factorcol in factorcols:
            output = map.split('@')[0] + '.' + factorcol
            gscript.message('Rasterize <%s> with attribute <%s>' %(map, factorcol) 
                + '\n to raster map <%s> ...' %(output) )
            v.to_rast(input=map, use='attr', attrcolumn=factorcol, 
                      output=output, quiet=quiet)
            factors += (output,)
    
    else: factors = (cfactor, pfactor)
    
    gscript.message('Multiply factors <%s> with <%s> ...' %(factors, soillossbare) )
    formula = soillossgrow + '=' + soillossbare 
    for factor in factors:
        formula += '*' + factor
    r.mapcalc(formula)
    
    ## apply color rules
    r.colors(map = soillossgrow,
                    rules = '-', stdin = colorrules['soillossgrow'],
                    quiet = quiet)

if __name__ == "__main__":
    options, flags = gscript.parser()
    sys.exit(main())


