#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
MODULE:     g.gui.soilloss

AUTHOR(S):  Martin Zbinden <martin.zbinden@immerda.ch>

PURPOSE:    

VERSION:    0.2

DATE:       Mon Aug 03 12:00:00 CET 2014

COPYRIGHT:  (C) 2014 Martin Zbinden and by the GRASS Development Team

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.
'''
#%module
#%  description: Calculate potential and realized soilloss for Switzerland (cantons BE, FR, SO). Change region automatically to parcels of <betriebid>. Automatically imports needed data from OWS-server (preconfigured in module).
#%    keywords: gui, hydrology, erosion, Switzerland, extension
#%end

#%option
#%  type: string
#%  key: betriebid
#%  key_desc: name
#%  description: Farm number
#%  required: yes
#%end

#%option
#%  key: task   
#%  key_desc: name
#%  description: Task
#%  options: soilloss.bare,soilloss.bare.update,soilloss.grow,soilloss.grow.measure, soilloss.cpmax,slope.stats
#%  required: yes
#%  multiple:no
#%end

#%option
#%  type: string
#%  key: maxsoilloss
#%  key_desc: float
#%  description: maximal soilloss for CPmax-scenario
#%  answer:  4
#%  required: yes
#%end

#%option
#%  key: output
#%  type: string
#%  key_desc: name
#%  gisprompt: new,cell,raster
#%  description: output raster map
#%  answer:  output
#%  required: yes
#%end

#%option
#%  key: configuration
#%  type: string
#%  key_desc: name
#%  description: server configuration name
#%  answer: default
#%  guisection: server
#%  required: no
#%end

#%option
#%  key: username
#%  type: string
#%  key_desc: name
#%  description: Benutzername
#%  guisection: server
#%  required: no
#%end

#%option
#%  key: password
#%  type: string
#%  key_desc: name
#%  description: Passwort
#%  guisection: server
#%  required: no
#%end

#%flag
#%  key: b
#%  description: use newly defined barriers
#%end
#%flag
#%  key: g
#%  description: don't change region
#%end
#%flag
#%  key: i
#%  description: force reimport of all base data
#%end
#%flag
#%  key: n
#%  description: don't import anything ("offline mode")
#%end
#%flag
#%  key: s
#%  description: calculate per-parcel statistics
#%end
#%flag
#%  key: c
#%  description: don't copy result map to output map
#%end

#USER SETTINGS
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
        'measures' : 'ebk_massnahmenplan'
        },
    'colnames' : {
        'cfactor' : 'cfactor',
        'pfactor' : 'pfactor',
        'kfactor' : 'kfactor'
        }
    }    

#END OF USER SETTINGS
###DO NOT CHANGE ANYTHING AFTER THIS LINE !

import grass.script as gscript
from grass.pygrass.gis import Mapset
from grass.pygrass.gis.region import Region
from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g
from grass.pygrass.modules import Module

quiet = True
if gscript.verbosity() > 2:
    quiet=False

## define own modules in pygrass
rsoillossbare = Module("r.soilloss.bare")
rsoillossupdate = Module("r.soilloss.update")
rsoillossgrow = Module("r.soilloss.grow")
rsoillosscpmax = Module("r.soilloss.cpmax")
rsoillossreclass = Module("r.soilloss.reclass")
rsoillossstats = Module("r.soilloss.stats")
vinogr = Module("v.in.ogr")

def main(options, flags):
    config_name = options['configuration']
    params = owsConnections[config_name]
    
    output = options['output']
    betriebid = options['betriebid']
    basename = 'B' + betriebid + '_'
    task = options['task']
    maxsoilloss = options['maxsoilloss']

    params['username'] = options['username']
    params['password'] = options['password']
    params['dsn'] = params['dsn'] + ' user=%s password=%s' \
        %(params['username'],params['password'])
        
    flag_b = flags['b'] #use newly defined barriers
    flag_g = flags['g'] #don't set region according to parcel data
    flag_i = flags['i'] #force reimport of base data
    flag_n = flags['n'] #don't import anything ('offline')
    flag_c = flags['c'] #don't copy results to output raster map
    flag_s = flags['s'] #calculate statistics for results

    ## define own methods for Vect and Rast classes
    from grass.pygrass.vector import VectorTopo as Vect
    # some monkey patching with own methods
    #autoimport vector data from PostGIS
        
    def autoimport(self, layer, *args, **kwargs):
        if not layer in params['layers'].keys():
            print('Coverage <%s> not available/not configured on server.' %layer )
        vinogr(dsn = params['dsn'], snap = 0.01,
            layer=params['layers'][layer],
            output=self.name, **kwargs)
    Vect.autoimport = autoimport
    
    from grass.pygrass.raster import RasterAbstractBase as Rast
    #autoimport raster from WCS
    def autoimport(self, coverage, *args, **kwargs):
        if not coverage in params['coverages'].keys():
            print('Coverage <%s> not available/not configured on server.' %coverage )
        r.in_wcs(url = params['url'], 
                username = params['username'], 
                password = params['password'],
                coverage=params['coverages'][coverage],
                output=self.name, **kwargs)
    Rast.autoimport = autoimport

    def setRegion(parcelmap,betriebid):
        ## set region to parcel layer extent + buffer
        reg = Region()
        reg.vect(parcelmap.name)
        regbuffer = 100
        reg.north += regbuffer
        reg.east += regbuffer
        reg.south -= regbuffer
        reg.west -= regbuffer
        reg.set_current()
        # set_current() not working right now
        # so using g.region() :
        g.region(n=str(reg.north), s=str(reg.south), w=str(reg.west), e=str(reg.east), res='2', flags='a',quiet=quiet)
        g.region(save='B'+betriebid,overwrite=True,quiet=quiet)
    
    def slopestats():
        slopemap = Rast(maps['elevation'].name + '.slope')
        r.slope_aspect(elevation=maps['elevation'].name, slope=slopemap.name, format='percent') 
        print('\n \n Statistics for slope <%s> (slope in %%): '%(slopemap.name))
        rsoillossstats(soilloss=slopemap.name, map=parcelmap.name, parcelnumcol='id')
        
    
    def sbare():
        rsoillossreclass.flags.u = True
        rsoillossreclass(maps['soillossbare'].name, 'soillossbare',flags='')
        
        if flag_s:
            print('\n \n Statistics for soilloss <%s> : '%(soillossbaremap.name))
            rsoillossstats(soilloss=soillossbaremap.name, 
                           map=parcelmap.name, parcelnumcol='id')
        if not flag_c:
            g.copy(rast=(soillossbaremap.name,output))
            gscript.message('Copy made to <%s> for automatic output' %(output))
    
    def sbareupdate():
        rsoillossupdate.inputs.map = parcelmap.name
        rsoillossupdate.inputs.factorold = maps['kfactor'].name
        rsoillossupdate.inputs.factorcol = 'kfactor'
        rsoillossupdate.flags.k = True
        rsoillossupdate.flags.p = True
        rsoillossupdate(soillossin=maps['soillossbare'].name, 
                        soillossout=soillossbarecorrmap.name)
        gscript.message('Soilloss for bare soil successfully updated to <%s> using parcelwise kfactor.' %(soillossbarecorrmap.name))
        if not flag_c:
            g.copy(rast=(soillossbarecorrmap.name,output))
            gscript.message('Copy made to <%s> for automatic output' %(output))
            
        rsoillossreclass(soillossbarecorrmap.name, 'soillossbare',flags='')
        gscript.message('Reclassified and colored maps found in <%s.3> and <%s.9> .'%(soillossbarecorrmap.name, soillossbarecorrmap.name))
        
        if flag_s:
            print('\n \n Statistics for soilloss on bare soil <%s> : '%(soillossgrowmap))
            rsoillossstats(soilloss=soillossbarecorrmap.name, map=parcelmap.name, parcelnumcol='id')
      
    def sgrow():
        if soillossbarecorrmap.exist():
            rsoillossgrow.inputs.soillossbare = soillossbarecorrmap.name
        else: rsoillossgrow.inputs.soillossbare = soillossbaremap.name
        rsoillossgrow.inputs.map = parcelmap.name
        rsoillossgrow.inputs.factorcols = (params['colnames'][('cfactor')],)
        rsoillossgrow.inputs.factorcols += (params['colnames'][('pfactor')],)
        rsoillossgrow(soillossgrow=soillossgrowmap.name)
        gscript.message('Soilloss for grown soil successfully calculated to <%s> using parcelwise C and P factor.' %(soillossgrowmap))
                
        if not flag_c:
            g.copy(rast=(soillossgrowmap.name,output))
            gscript.message('Copy made to <%s> for automatic output' %(output))

        rsoillossreclass(soillossgrowmap.name, 'soillossgrow',flags='')
        gscript.message('Reclassified and colored maps found in <%s.3> and <%s.9> .'%(soillossgrowmap.name, soillossgrowmap.name))

        if flag_s:
            print('\n \n Statistics for soilloss on grown soil <%s> : '%(soillossgrowmap))
            rsoillossstats(soilloss=soillossgrowmap.name, map=parcelmap.name, parcelnumcol='id')
                    
    def scpmax():
        if soillossbarecorrmap.exist():
            rsoillosscpmax.inputs.soillossbare = soillossbarecorrmap.name
        else: rsoillosscpmax.inputs.soillossbare = soillossbaremap.name
        
        rsoillosscpmax.inputs.maxsoilloss=maxsoilloss
        rsoillosscpmax(cpmax=soillosscpmaxmap.name)
        
        if not flag_c:
            g.copy(rast=(soillosscpmaxmap.name,output))
            gscript.message('Copy made to <%s> for automatic output' %(output))
        
        if flag_s:
            print('\n \n Statistics for <%s> : '%(soillosscpmaxmap))
            rsoillossstats(soilloss=soillosscpmaxmap.name, map=parcelmap.name, parcelnumcol='id')
             
    def smeasure():
        gscript.message('Import <%s>' % measuremap.name)
        measuremap.autoimport('measures', overwrite=True, quiet=quiet,
                              where="betrieb_id = %s" % betriebid)
        
        soillossbaremap = maps['soillossbare']
        kfactormap = maps['kfactor']

        if soillossbarecorrmap.exist():
            gscript.message('Using updated soillossbare map.')
            soillossbaremap = soillossbarecorrmap
            kfactormap = Rast(parcelmap.name + '.kfactor')
        
        if flag_b:
            measurebarriermap = Vect(measuremap.name + '_barrier')
            v.extract(input=measuremap.name, where="barrier = 1",
                      output=measurebarriermap.name)
            
            measurefieldblockmap = Vect(measuremap.name + '_fieldblocks')
            v.overlay(ainput=maps['fieldblocks'].name,
                      binput=measurebarriermap.name,\
                      operator='not', 
                      output=measurefieldblockmap.name)
            
            rsoillossbare.inputs.elevation = maps['elevation'].name
            rsoillossbare.inputs.rfactor = maps['rfactor'].name
            rsoillossbare.inputs.kfactor = kfactormap.name
            rsoillossbare.inputs.map = measurefieldblockmap.name
            rsoillossbare.inputs.constant_m = '0.6'
            rsoillossbare.inputs.constant_n = '1.4'


            rsoillossbare.flags.r = True
            rsoillossbare(soillossbare=soillossbarebarriermap.name)
            soillossbaremap = soillossbarebarriermap

        parcelpfactor = parcelmap.name + '.pfactor'
        parcelcfactor = parcelmap.name + '.cfactor'
        v.to_rast(input=parcelmap.name, use='attr', attrcolumn='pfactor',
                  output=parcelpfactor)
        v.to_rast(input=parcelmap.name, use='attr', attrcolumn='cfactor',
                  output=parcelcfactor)
                  
        measurepfactor = measuremap.name + '.pfactor'
        measurecfactor = measuremap.name + '.cfactor'
        v.to_rast(input=measuremap.name, use='attr', attrcolumn='pfactor',
                  output=measurepfactor)
        v.to_rast(input=measuremap.name, use='attr', attrcolumn='cfactor',
                  output=measurecfactor)

        pfactor = parcelmap.name + '.pfactor.measure'
        cfactor = parcelmap.name + '.cfactor.measure'

        r.patch(input=(measurepfactor,parcelpfactor), output=pfactor)
        r.patch(input=(measurecfactor,parcelcfactor), output=cfactor)
        rsoillossgrow.inputs.soillossbare = soillossbaremap.name
        rsoillossgrow.inputs.cfactor = pfactor
        rsoillossgrow.inputs.pfactor = cfactor
        rsoillossgrow(soillossgrow=soillossmeasuremap.name)
        
        rsoillossreclass(soillossmeasuremap.name, 'soillossgrow',flags='')
        gscript.message('Reclassified and colored maps found in <%s.3> and <%s.9> .'%(soillossmeasuremap.name, soillossmeasuremap.name))

        if flag_s:
            gscript.message('\n \n Statistics for soilloss on grown soil <%s> : '%(soillossgrowmap))
            rsoillossstats(soilloss=soillossmeasuremap.name, map=parcelmap.name, parcelnumcol='id')
        
        if not flag_c:
            g.copy(rast=(soillossmeasuremap.name,output))
            gscript.message('Copy made to <%s> for automatic output' %(output))
    
#######################################################################
## BEGIN main controls
    curregion = Mapset()
    permanent = Mapset('PERMANENT')
    if curregion.name == permanent.name:
        gscript.fatal("Please change mapset. It can be dangerous to use this prealpha-module in PERMANENT")
            
    parcelmap = Vect(basename+'parcels')  
    if not flag_n:
        parcelmap.autoimport('parcels', overwrite=True, quiet=quiet,
                             where="betrieb_id = %s" % betriebid)
        #if parcelmap.popen.returncode <> 0:
        #   gscript.fatal('Import der Parzellendaten gescheitert.')
        
    if not flag_g: 
        setRegion(parcelmap,betriebid)
        gscript.verbose('Region set to parcels extent + 100 raster cells. \
            \n Resolution: raster cell = 2 x 2 meter.')
            
    basedata_rast = ('elevation','soillossbare','kfactor','rfactor')
    basedata_vect = ('fieldblocks',)
    
    maps = {}
    for map in (basedata_rast):
        mapname = basename + map
        maps[map] = Rast(mapname)
        
    for map in (basedata_vect):
        mapname = basename + map
        maps[map] = Vect(mapname)
      
    if not flag_n:
        vinogr.flags.r = True
        vinogr.inputs.where = ""

        for mapname in maps.keys():
            map = maps[mapname]
            if map.exist() and flag_i:
                map.remove()
            if not map.exist():
                map.autoimport(mapname)
                
    
    soillossbaremap = maps['soillossbare']
    
    soillossbarecorrmap = Rast(maps['soillossbare'].name +'.update')
    soillossgrowmap = Rast(basename+'soillossgrow')
    soillosscpmaxmap = Rast(basename+'cpmax')
    measuremap = Vect(basename+'measures')
    soillossmeasuremap = Rast(basename+'soillossgrow.measure')
    soillossbarebarriermap = Rast(basename+'soillossbare.barrier')
    
    
    gscript.error('Import ok. Beginning task %s ...' %task)

    tasks = {'soilloss.bare' : sbare,
        'soilloss.bare.update': sbareupdate,
        'soilloss.grow' : sgrow,
        'soilloss.grow.measure' : smeasure,
        'soilloss.cpmax' : scpmax,
        'slope.stats' : slopestats
        }
    
    if task in tasks:
        tasks[task]()
    else:
        gscript.fatal('Please choose a valid task')
        #default
        

'''
END main
'''
    

if __name__ == "__main__":
    options, flags = gscript.parser()
    main(options, flags)



