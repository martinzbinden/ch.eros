# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 08:25:22 2014

@author: martinz
"""

#!/usr/bin/env python
 
import os
import sys
import subprocess
 
# some predefined variables, name of the GRASS launch script + location/mapset
#grass7bin = 'C:\Program Files (x86)\GRASS GIS 7.0.svn\grass70svn.bat'
grass7bin = 'grass70'
location = "LV03"
mapset   = "fpeb"
 
########### SOFTWARE
# query GRASS 7 itself for its GISBASE
# we assume that GRASS GIS' start script is available and in the PATH
startcmd = grass7bin + ' --config path'
p = subprocess.Popen(startcmd, shell=True, 
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
if p.returncode != 0:
    print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    sys.exit(-1)
gisbase = out.strip('\n')
 
# Set GISBASE environment variable
os.environ['GISBASE'] = gisbase
# define GRASS-Python environment
gpydir = os.path.join(gisbase, "etc", "python")
sys.path.append(gpydir)
 
########### DATA
# define GRASS DATABASE
gisdb = os.path.join(os.path.expanduser("~"), "grassdata")
# Set GISDBASE environment variable
os.environ['GISDBASE'] = gisdb
 
# import GRASS Python bindings (see also pygrass)
import grass.script as gscript
import grass.script.setup as gsetup
 
###########
# launch session
gsetup.init(gisbase,
            gisdb, location, mapset)
 
gscript.message('Current GRASS GIS 7 environment:')
print gscript.gisenv()
 
gscript.message('Available raster maps:')
for rast in gscript.list_strings(type = 'rast'):
    print rast
 
gscript.message('Available vector maps:')
for vect in gscript.list_strings(type = 'vect'):
    print vect
 
sys.exit(0)