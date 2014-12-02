#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# MODULE:   r.soilloss.cpmax
# AUTHOR(S):  Martin Zbinden
#
# PURPOSE:  Multiplicate soilloss on bare soil with C- and P-factors
#           to receive soilloss for bare soil.
#
#           @return cpmax raster map
#
#
# VERSION:  0.1
#
# DATE:     So Jun 8 14:00:00 CET 2014
#
'''
#%Module
#%  description: Calculate soilloss t/(ha*a) for grown soil. Instead of input raster maps constant values can also be given.
#%    keywords: Raster, hydrology, erosion, CPmax
#%end

#%option G_OPT_R_INPUT
#%key: soillossbare
#%description: Raster map with soilloss for bare soil
#%end

#%option G_OPT_R_OUTPUT
#%key: cpmax
#%description: Output raster map with CPmax-scenario
#%end

#%option
#%key: maxsoilloss
#%key_desc: float
#%type: string
#%description: maximum tolerable soilloss t/(ha*a)
#%answer: 4
#%required: yes
#%end

import sys
import grass.script as gscript
from grass.pygrass.modules.shortcuts import raster as r


    
def main():
    soillossbare = options['soillossbare']
    cpmax = options['cpmax']
    maxsoilloss = options['maxsoilloss']
    
    r.mapcalc(cpmax + "=" +  maxsoilloss + "/" + soillossbare)
    
    cpmaxrules = '\n '.join([
        "0.00  56:145:37",
        "0.01  128:190:91",
        "0.05  210:233:153",
        "0.1  250:203:147",
        "0.15  225:113:76",
        "0.2  186:20:20",
        "100  0:0:0"
    ])

    r.colors(map = cpmax, rules = '-', stdin = cpmaxrules)
    
    gscript.info('Calculation of CPmax-scenario in <%s> finished.' %cpmax )

if __name__ == "__main__":
    options, flags = gscript.parser()
    sys.exit(main())


