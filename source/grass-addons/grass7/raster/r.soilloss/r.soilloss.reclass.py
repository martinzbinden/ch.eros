#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# MODULE:   r.soilloss.reclass
#
# AUTHOR(S):  Martin Zbinden
#
# PURPOSE:  reclass soilloss values for statistics and for pretty printing (3 or 9 discrete classes) and apply color rules to theme
#
#           @return classified soilloss raster maps
#
#
# VERSION:  0.2
#
# DATE:     So Jun 8 14:00:00 CET 2014
#
'''
#%Module
#%  description: Reclass soilloss maps into 3 and 9 classes. Appends .3 and .9 to original rastermap name and applies color rules to them.
#%  keywords: Raster, hydrology, erosion, reclass
#%end

#%option G_OPT_R_INPUT
#%  key: soilloss
#%  description: Input raster map
#%end

#%option
#%  key: colorschema
#%  key_desc: name
#%  description: Module for flowaccumulation calculation
#%  options: soillossbare, soillossgrow
#%  answer: soillossbare
#%  required: yes
#%  multiple:no
#%end


#%flag
#%  key: f
#%  description: Flatten 3-class raster with 'r.neighbors' (-.3f map)
#%end

#%flag
#%  key: u
#%  description: Also apply continuous color rules to input raster
#%end

import sys
import grass.script as gscript
from grass.pygrass.modules.shortcuts import raster as r


def main():
    soilloss = options['soilloss']
    soilloss9 = soilloss.split('@')[0] + '.9'
    soilloss3 = soilloss.split('@')[0] + '.3'
    colorschema = options['colorschema']
    flag_u = flags['u']
    flag_f = flags['f']

    
    quiet = True
    if gscript.verbosity() > 2:
        quiet=False
    
    #color shemes - contents:
    classrules = {  'soillossbare9' : {},
                    'soillossbare3' : {},
                    'soillossgrow9' : {},
                    'cfactor6' : {},
                    'kfactor6' : {}                
                    }
    
    colorrules = {  'soillossbare9': {},
                    'soillossbare3': {},
                    'soillossbare' : {},
                    'soillossgrow9' : {},
                    'soillossgrow' : {},
                    'cfactor6' : {},
                    'cfactor' : {},
                    'kfactor6' : {},
                    'kfactor' : {}
                    }
                    
    # (c) Gisler 2010                       
    classrules['soillossbare9'] =  '\n '.join([
        "0 thru 20 = 1 < 20",
        "20 thru 30 = 2 20 - 30",
        "30 thru 40 = 3 30 - 40",
        "40 thru 55 = 4 40 - 55",
        "55 thru 100 = 5 55 - 100",
        "100 thru 150 = 6 100 - 150",
        "150 thru 250 = 7 150 - 250",
        "250 thru 500 = 8 250 - 500",
        "500 thru 50000 = 9 > 500",
        ])
    
    # (c) Gisler 2010       
    classrules['soillossbare3'] =  '\n '.join([
        "0 thru 30 = 1 keine Gefährdung",
        "30 thru 55 = 2 Gefährdung",
        "55 thru 50000 = 3  grosse Gefährdung",
        ])
    
    # (c) BLW 2011
    colorrules['soillossbare9'] = '\n '.join([
        "1    0:102:0",
        "2   51:153:0",
        "3   204:255:0",
        "4  255:255:0",
        "5   255:102:0",
        "6  255:0:0",
        "7  204:0:0",
        "8  153:0:0",
        "9  102:0:0",
        ])
    
    # (c) BLW 2011
    colorrules['soillossbare3'] = '\n '.join([
        "1   51:153:0",
        "2  255:255:0",
        "3  255:0:0"
        ])
    
    # (c) BLW 2011
    colorrules['soillossbare'] = '\n '.join([
        "0    0:102:0",
        "20   51:153:0",
        "30   204:255:0",
        "40  255:255:0",
        "55   255:102:0",
        "100  255:0:0",
        "150  204:0:0",
        "250  153:0:0",
        "500  102:0:0",
        "5000  102:0:0"
        ])
    
    # (c) Gisler 2010       
    colorrules['soillossgrow9'] = '\n '.join([
        "1   69:117:183",
        "2  115:146:185",
        "3  163:179:189",
        "4  208:216:193",
        "5  255:255:190",
        "6  252:202:146",
        "7  245:153:106",
        "8  233:100:70",
        "9  213:47:39"
        ])
        
    # (c) Gisler 2010    
    colorrules['soillossgrow9'] = '\n '.join([
        "1   69:117:183",
        "2  115:146:185",
        "3  163:179:189",
        "4  208:216:193",
        "5  255:255:190",
        "6  252:202:146",
        "7  245:153:106",
        "8  233:100:70",
        "9  213:47:39"
        ])
    
    # (c) Gisler 2010    
    colorrules['soillossgrow3'] = '\n '.join([
        "1   69:117:183",
        "2  163:179:189",
        "3  208:216:193",
        "4  245:153:106"
        ])
     
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
        
    # (c) Gisler 2010   
    classrules['soillossgrow9'] = '\n '.join([
        "0 thru 1 = 1 < 1 ",
        "1 thru 2 = 2 1 - 2 ",
        "2 thru 4 = 3 2 - 4 ",
        "4 thru 7.5 = 4 4 - 7.5",
        "7.5 thru 10 = 5 7.5 - 10",
        "10 thru 15 = 6 10 - 15",
        "15 thru 20 = 7 15 - 20",
        "20 thru 30 = 8  20 - 30",
        "30 thru 5000 = 9  > 30"
        ])
    
    # (c) Gisler 2010   
    classrules['soillossgrow3'] = '\n '.join([
        "0 thru 2 = 1 Toleranz mittelgründige Böden",
        "2 thru 4 = 2 Toleranz tiefgründige Böden",
        "4 thru 7.5 = 3 leichte Überschreitung",
        "7.5 thru 5000 = 4 starke Überschreitung"
        ])
       
    # Gisler 2010
    colorrules['cfactor6']  = '\n '.join([
        "1  56:145:37",
        "2  128:190:91",
        "3  210:233:153",
        "4  250:203:147",
        "5  225:113:76",
        "6  186:20:20"
        ])
        
    # Gisler 2010
    colorrules['cfactor']  = '\n '.join([
        "0.00  56:145:37",
        "0.01  128:190:91",
        "0.05  210:233:153",
        "0.1  250:203:147",
        "0.15  225:113:76",
        "0.2  186:20:20",
        "1  186:20:20",
        ])
        
    # (c) Gisler 2010
    classrules['kfactor5'] = '\n '.join([
        "0 thru 0.20 = 1 < 0.20",
        "0.20 thru 0.25 = 2 0.20 - 0.25",
        "0.25 thru 0.30 = 3 0.25 - 0.3",
        "0.3  thru 0.35 = 4 0.3 - 0.35",
        "0.35 thru 1 = 5 > 0.30"
        ])
    
    # (c) Gisler 2010
    colorrules['kfactor6'] = '\n '.join([
        "1  15:70:15",
        "2  98:131:52",
        "3  204:204:104",
        "4  151:101:50",
        "5  98:21:15"
        ])
        
    # (c) Gisler 2010
    colorrules['kfactor'] = '\n '.join([
        "0.00  15:70:15",
        "0.20  98:131:52",
        "0.25  204:204:104",
        "0.30  151:101:50",
        "0.35  98:21:15"
        ])
        
    # own definitions
    colorrules['cpmax'] = '\n '.join([
        "0.01  102:0:0",
        "0.01  153:0:0",
        "0.02  204:0:0",
        "0.04  255:0:0",
        "0.06   255:102:0",
        "0.08   255:255:0",
        "0.10  204:255:0",
        "0.12   51:153:0",
        "0.15    0:102:0",
        "1000.00    0:102:0"
        ])
            
    classrules9 =  '\n '.join([
        "0 thru 20 = 1 <20",
        "20 thru 30 = 2 20 - 30",
        "30 thru 40 = 3 30 - 40",
        "40 thru 55 = 4 40 - 55",
        "55 thru 100 = 5 55 - 100",
        "100 thru 150 = 6 100 - 150",
        "150 thru 250 = 7 150 - 250",
        "250 thru 500 = 8 250 - 500",
        "500 thru 50000 = 9 >500",
        ])
    
    if colorschema == 'soillossbare':
        classrules9 = classrules['soillossbare9']
        colorrules9 = colorrules['soillossbare9']
        classrules3 = classrules['soillossbare3']
        colorrules3 = colorrules['soillossbare3']
        colorrules = colorrules['soillossbare']

    if colorschema == 'soillossgrow':
        classrules9 = classrules['soillossgrow9']
        colorrules9 = colorrules['soillossgrow9']
        classrules3 = classrules['soillossgrow3']
        colorrules3 = colorrules['soillossgrow3']
        colorrules = colorrules['soillossgrow']
        
    r.reclass(input=soilloss, rules='-', stdin = classrules9, output=soilloss9)
    r.colors(map = soilloss9, rules = '-', stdin = colorrules9, quiet = quiet)
    r.reclass(input=soilloss, rules='-', stdin = classrules3, output=soilloss3)
    r.colors(map = soilloss3, rules = '-', stdin = colorrules3, quiet = quiet)

    if flag_f:
            soilloss3f = soilloss3 + 'f'
            r.neighbors(method='mode', input=soilloss3, selection=soilloss3,
                    output=soilloss3f, size=7)
            soilloss3 = soilloss3f


    if flag_u:
        r.colors(map = soilloss, rules = '-', stdin = colorrules, quiet = quiet)

if __name__ == "__main__":
    options, flags = gscript.parser()
    sys.exit(main())
