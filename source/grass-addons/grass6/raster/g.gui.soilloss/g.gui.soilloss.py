#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
MODULE:     g.gui.soilloss (helper for GRASS 6)

AUTHOR(S):  Martin Zbinden <martin.zbinden@immerda.ch>

PURPOSE:    Used by QGIS GRASS plugin to run module g.gui.soilloss in GRASS 7, which has actually all the functionality.

VERSION:    0.2

DATE:       Mon Aug 04 16:00:00 CET 2014

COPYRIGHT:  (C) 2014 Martin Zbinden and by the GRASS Development Team

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.
'''
#%module
#%  description: Calculate potential and realized soilloss for Switzerland (cantons BE, FR, SO). Change region automatically to parcels of <betriebid>. Automatically imports needed data from OWS-server (preconfigured in module). (This is only a helper module which is actually going to use GRASS 7).
#%    keywords: gui, hydrology, erosion, Switzerland, extension
#%end

#%option
#%  type: string
#%  key: betriebid
#%  key_desc: name
#%  description: Betriebsnummer/Fallnummer
#%  required: yes
#%end

#%option
#%  key: task   
#%  key_desc: name
#%  description: Aufgabe
#%  options: soilloss.bare,soilloss.bare.update,soilloss.grow,soilloss.grow.measure, soilloss.cpmax,slope.stats
#%  required: yes
#%  multiple:no
#%end

#%option
#%  key: output
#%  type: string
#%  key_desc: name
#%  gisprompt: new,cell,raster
#%  description: Ausgabekarte (v.a. für Anzeige)
#%  answer:  output
#%  required: yes
#%end

#%option
#%  key: configuration
#%  type: string
#%  key_desc: name
#%  description: Server-Konfiguration
#%  answer: default
#%  guisection: server
#%  required: no
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
#%  description:  neu definierte Barrieren berücksichtigen
#%end
#%flag
#%  key: g
#%  description:  Region nicht den Parzellen anpassen
#%end
#%flag
#%  key: i
#%  description:  Alle Daten nochmals importieren
#%end
#%flag
#%  key: n
#%  description: Keine Daten importieren (offline)
#%end
#%flag
#%  key: c
#%  description: Nicht Resultate nach Ausgabekarte kopieren
#%end
#%flag
#%  key: s
#%  description: Parzellenweise Statistik ausgeben
#%end

#%flag
#%  key: o
#%  description: Vorhandene Karten überschreiben
#%end
#%flag
#%  key: v
#%  description: Mehr Ausgaben anzeigen (verbose)
#%end


#END OF USER SETTINGS
###DO NOT CHANGE ANYTHING AFTER THIS LINE !

import os
import grass.script as gscript
import subprocess



def main(options, flags):
    configuration = options['configuration']    
    output = options['output']
    betriebid = options['betriebid']
    task = options['task']
    username = options['username']
    password = options['password']
    maxsoilloss = options['maxsoilloss']
        
    flag_b = flags['b'] #use newly defined barriers
    flag_g = flags['g'] #don't set region according to parcel data
    flag_i = flags['i'] #force reimport of base data
    flag_n = flags['n'] #don't import anything (offline mode)
    flag_c = flags['c'] #don't copy results to output raster map
    flag_s = flags['s'] #calculate statistics for results
    flag_v = flags['v'] #verbose
    flag_o = flags['o'] #overwrite

    
    #os.path.expanduser(path)
    env = gscript.parse_command("g.gisenv", flags='s')
    gisdbase = env['GISDBASE'].strip(";'").lstrip("'")
    location = env['LOCATION_NAME'].strip(";'").lstrip("'")
    mapset = env['MAPSET'].strip(";'").lstrip("'")
    
    try:
        gislock = os.path.join(gisdbase,location,mapset,'.gislock')
        os.remove(gislock)
    except OSError:
        pass

    gcommands = []
    #gcommands += ['g.version']
    #gcommands += ['g.mapset %s --q' %mapset]
    gcommands += ['db.connect -d --q']
    if flag_v:
        gcommands += ['g.gisenv']

    gexecute = 'g.gui.soilloss output='+output +' betriebid=' + betriebid \
        + ' task=' + task + ' maxsoilloss=' + maxsoilloss + ' username=' + username \
        + ' password=' + password
    
    
    if flag_b: gexecute += ' -b'
    if flag_s: gexecute += ' -s'
    if flag_i: gexecute += ' -i'
    if flag_n: gexecute += ' -n'
    if flag_o: gexecute += ' --o'
    if gscript.overwrite(): gexecute += ' --o'
    if gscript.verbosity() > 2 or flag_v: gexecute += ' --v'
    else: gexecute += ' --q'

    gcommands += [gexecute]
    gcommands += ['exit']
    
    batchjob = os.getenv('HOME') + '/.qgis2/processing/grass7_batch_job.sh'
    with open(batchjob, 'w') as f:
        for s in gcommands:
            print s
            f.write(s + '\n')
        f.close()
        
    rclines = []
    rclines += ['MAPSET: ' + mapset]
    rclines += ['GISDBASE: ' + gisdbase]
    rclines += ['LOCATION_NAME: ' +  location]
    rclines += ['GUI: text']
    
    rcfile = os.getenv('HOME') + '/.grass7/rc'
    with open(rcfile, 'w') as f:
        for s in rclines:
            print s
            f.write(s + '\n')
        f.close()
        
    st = os.stat(batchjob)
    os.chmod(batchjob, st.st_mode | 0111)
    os.environ['GRASS_BATCH_JOB'] = batchjob
    del os.environ['LD_LIBRARY_PATH']
    del os.environ['GISBASE']
    
    command = ['grass70 ']  + [gisdbase + '/' \
        + location + '/' + mapset]
    subprocess.call(command, shell=True)

'''
END main
'''
if __name__ == "__main__":
    options, flags = gscript.parser()
    main(options, flags)



