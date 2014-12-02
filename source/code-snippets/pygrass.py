
#!/usr/bin/env python
#-*- coding: utf-8 -*-


    parcels.open('r')
    grass.verbose(parcels.table.columns.names())

    v.to_rast(input=parcels.name, use='attr', attrcolumn=params['colnames']['cfactor'], output=parcels.name+'.'+params['colnames']['cfactor'])

    factors =  {}
    for factor in ('cfactor','pfactor','kfactor'):
        attrcolumn=params['colnames'][factor]
        factors[factor] = Rast(factor+'.'+attrcolumn)
        v.to_rast(input=parcels.name, use='attr', attrcolumn=attrcolumn,
            output=factors[factor].name)



p = gscript.read_command(input=self.vrt_file, output=self.params['output'],
                      env_=self._env, stderr = gscript.PIPE)
#not yet working like this, use gscript.start_command

while p.popen.poll() is None:
            line = p.popen.stderr.readline()
            linepercent = line.replace('GRASS_INFO_PERCENT:','').strip()
            if linepercent.isdigit():
                #print linepercent
                gscript.percent(int(linepercent),100,1)
            else:
                gscript.verbose(line)

        gscript.percent(100,100,5)


if __name__ == "__main__":
    opts, flgs = parser()
    main(opts, flgs)



