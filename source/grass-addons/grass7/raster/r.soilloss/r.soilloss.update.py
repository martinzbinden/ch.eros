#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# MODULE:   r.soilloss.update
#
# AUTHOR(S):  Martin Zbinden
#
# PURPOSE:  update soilloss raster maps with new factors
#           Formula:
#           Anew = Aold / Fold * Fnew
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
#%  description: update soillossbare with new R or K factors (generally or only for parcels)
#%  keywords: Raster, hydrology, erosion, update
#%end

#%option G_OPT_R_MAP
#%key: soillossin
#%description: Old soilloss raster map
#%end

#%option G_OPT_R_MAP
#%key: factorold
#%description: Old factor raster map (corresponding to <soillossin>)
#%end

#%option G_OPT_R_OUTPUT
#%key: soillossout
#%description: New soilloss raster map
#%end

#%option G_OPT_R_MAP
#%key: factornew
#%guisection: Inputs
#%required: no
#%end

#%option G_OPT_V_MAP
#%key: map
#%guisection: Inputs
#%required: no
#%end
#%option G_OPT_DB_COLUMN
#%key: factorcol
#%guisection: Inputs
#%end

#%flag
#%key: k
#%description: calculate k-factor components from % clay p_T, silt p_U, stones p_st, humus p_H
#%guisection: Inputs
#%end

#%flag
#%key: p
#%description: fill NULL values of new factor map with old values?
#%guisection: Inputs
#%end

#%flag
#%key: c
#%  description: Reclass results and apply discrete color rules
#%end

import sys
import grass.script as gscript
from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g
from grass.pygrass.vector import VectorTopo as Vect

# Kb für Bodenarten nach Gisler 2010, S. 33
bodenarten = [ # Nr, Name, Ton von %, Ton bis %, U von %, U bis %, Kb
    [9, 'T',    50, 100,    0, 50,      0.06],
    [8, 'IT',   40, 50,     0, 50,      0.09],
    [1, 'S',    0,  5,      15, 100,    0.13],
    [3, 'IS',   5, 10,      0, 50,      0.18],
    [7, 'tL',   30, 40,     0, 50,      0.20],
    [4, 'IrS',  10, 15,     0, 50,      0.24],
    [6, 'L' ,   20, 30,     0, 50,      0.25],
    [13, 'tU',  30, 50,     50, 100,    0.25],
    [5, 'sL',   15, 20,     0, 50,      0.30],
    [2, 'uS',   0, 5,       15, 50,     0.35],
    [12, 'IU',  10, 30,     50, 100,    0.50],
    [10, 'sU',  0, 10,      50, 70,     0.60],
    [11, 'U',   0, 10,      70, 100,    0.70]
]

# Ks für Skelettgehalt nach Gisler 2010, S. 33
#skelettgehalte = [  # Grobbodenbedeckung %, Code, Ks
#     [2, 1.00],
#    [10, 0.87],
#    [25, 0.64],
#    [50, 0.39],
#    [75, 0.19],
#    [100, 0.10]
#]


# Ks für Skelettgehalt nach Gisler 2010 angepasst an die CH-Klassen, S. 34
skelettgehalte = [  # Grobbodenbedeckung %, Code, Ks
    [5,     0,  1.00],
    [10,    1,  0.87],
    [20,    2,  0.64],
    [20,    3,  0.64],
    [30,    4,  0.39],
    [30,    5,  0.39],
    [50,    6,  0.39],
    [50,    7,  0.39],
    [100,   8,  0.19],
    [100,   9,  0.19]
]

# Ks für Skelettgehalt nach Gisler 2010, S. 34
humusgehalte = [ # Massenanteil %, Kh
    [1,     1.15],
    [2,     1.05],
    [4,     0.90],
    [15,    0.80],
    [100,   'n.d.']
]


def main():
    soillossin = options['soillossin']
    soillossout = options['soillossout']
    factorold = options['factorold']
    
    factornew = options['factornew']
    map = options['map']
    factorcol = options['factorcol']
    
    flag_p = flags['p'] # patch factornew with factorold
    flag_k = flags['k'] # calculate k-factor components from % clay p_T, silt p_U, stones p_st, humus p_H 

     
    if not factornew:
        factors = {}
        if flag_k:
            gscript.message('Using factor derived from \
                soil components.')
            parcelmap = Vect(map)
            parcelmap.open(mode='rw', layer=1)
            parcelmap.table.filters.select()
            cur = parcelmap.table.execute()
            col_names = [cn[0] for cn in cur.description]
            rows = cur.fetchall()
           
            for col in (u'Kb',u'Ks',u'Kh', u'K'):
                if col not in parcelmap.table.columns:
                    parcelmap.table.columns.add(col,u'DOUBLE')
           
            for row in rows:
                rowid = row[1]
                p_T = row[7]
                p_U = row[8]
                p_st = row[9]
                p_H = row[10]
    
                print("Parzelle mit id %d :" %rowid)
                for sublist in bodenarten:
                    # p_T and p_U
                    if p_T in range(sublist[2],sublist[3]) \
                        and p_U in range(sublist[4],sublist[5]) :
                        print('Bodenart "' + sublist[1] 
                            + '", Kb = ' + str(sublist[6]))
                        Kb = sublist[6]
                        break
                
                for sublist in skelettgehalte:
                    if p_st < sublist[0]:
                        print('Skelettgehaltsklasse bis ' + str(sublist[0]) 
                            + ' , Ks = ' + str(sublist[1]))
                        Ks = sublist[1]
                        break
            
                   
                for sublist in humusgehalte:
                    if p_H < sublist[0]:
                        print('Humusgehaltsklasse bis ' + str(sublist[0]) 
                            + ' , Ks = ' + str(sublist[1]))
                        Kh = sublist[1]
                        break
                
                
                K = Kb * Ks * Kh
                print('K = ' + str(K))
        
                if K > 0:
                    parcelmap.table.execute("UPDATE " +  parcelmap.name 
                        + " SET"
                        + " Kb=" + str(Kb)
                        + ", Ks=" + str(Ks)
                        + ", Kh=" + str(Kh)
                        + ", K=" + str(K)
                        + " WHERE id=" + str(rowid) )
                    parcelmap.table.conn.commit()
                
            parcelmap.close()
            factorcol2 = 'K'
            
            factors['k'] = map.split('@')[0]+'.tmp.'+factorcol2
            v.to_rast(input=map, use='attr',
                   attrcolumn=factorcol2,
                   output=factors['k'])
            r.null(map=factors['k'], setnull='0')

        
        if factorcol:
            gscript.message('Using factor from column %s of \
                    vector map <%s>.' % (factorcol, map) )
                    
            factors['factorcol'] = map.split('@')[0]+'.tmp.' + factorcol
            v.to_rast(input=map, use='attr',
                   attrcolumn=factorcol,
                   output=factors['factorcol'])
            r.null(map=factors['factorcol'], setnull='0')
        
        print factors.keys()
        if not 'k' in factors and not 'factorcol' in factors: 
            gscript.fatal('Please provide either factor \
                raster map or valid vector map with factor column \
                (kfactor) or factor components columns (Kb, Ks, Kh)' )
        
        #if 'k' in factors and 'factorcol' in factors: 
    
        factornew = map.split('@')[0]+'.kfactor'
        if 'k' in factors and 'factorcol' in  factors:
            factornew = map.split('@')[0]+'.kfactor'
            r.patch(input=(factors['factorcol'],factors['k']),
                    output=factornew)
            
        elif 'k' in factors:
            g.copy(rast=(factors['k'],factornew))
            
        elif 'factorcol' in factors:
            g.copy(rast=(factors['factorcol'],factornew))

            
    if flag_p:
        #factorcorr = factorold + '.update'
        r.patch(input=(factornew,factorold), output=factornew)
        
    formula = soillossout + '=' + soillossin \
                + '/' + factorold  \
                + '*' + factornew
    r.mapcalc(formula)
            
    r.colors(map=soillossout, raster=soillossin)
    
if __name__ == "__main__":
    options, flags = gscript.parser()
    sys.exit(main())


