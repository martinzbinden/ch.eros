#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
MODULE:     r.in.wcs

AUTHOR(S):  Martin Zbinden <martin.zbinden@immerda.ch>, inspired by
            module r.in.wms (GRASS7) by Stepan Turek <stepan.turek AT seznam.cz>

PURPOSE:    Downloads and imports data from WCS server (only version 1.0.0).
            According to http://grasswiki.osgeo.org/wiki/WCS

VERSION:    0.1

DATE:       Mon Jun 16 21:00:00 CET 2014

COPYRIGHT:  (C) 2014 Martin Zbinden and by the GRASS Development Team

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.
'''

#%module
#% description: Downloads and imports coverage from WCS server.
#% keywords: raster
#% keywords: import
#% keywords: OGC web services
#%end

#%option
#% key: url
#% type: string
#% description: Service URL (typically http://.../mapserv? )
#% required: yes
#% answer: http://...?
#%end

#%flag
#% key: c
#% description: Get the server capabilities then exit
#% guisection: Request
#%end

#%flag
#% key: e
#% description: Link as external raster
#% guisection: Request
#%end

#%option
#% key: coverage
#% type: string
#% description: Coverage name to request
#% multiple: no
#% required: no
#% guisection: Request
#%end

#%option
#% key: urlparams
#% type: string
#% description: Additional query parameters to pass to the server
#% guisection: Request
#%end

#%option
#% key: username
#% type:string
#% description: Username for server connection
#% guisection: Request
#%end

#%option
#% key: password
#% type:string
#% description: Password for server connection
#% guisection: Request
#%end

#%option
#% key: output
#% type: string
#% gisprompt: new,cell,raster
#% description: Name for output raster map (default: coveragename)
#% required: no
#%end

#%option
#% key: location
#% type: string
#% description: Name for new location to create
#% required: no
#%end

#%option
#% key: region
#% type: string
#% description: Name for region instead of current region
#% required: no
#%end

import os
import sys
import io
import grass.script as gscript
from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g, display as d
import base64
import urllib2
from httplib import HTTPException
import subprocess
import lxml.etree as etree


class WCSBase:
    def __init__(self):
        # these variables are information for destructor
        self.temp_files_to_cleanup = []
        self.params = {}
        self.temp_map = None

    def __del__(self):

        # tries to remove temporary files, all files should be
        # removed before, implemented just in case of unexpected
        # stop of module
        for temp_file in self.temp_files_to_cleanup:
            gscript.try_remove(temp_file)
            pass

    def _debug(self, fn, msg):
        gscript.debug("%s.%s: %s" %
                    (self.__class__.__name__, fn, msg))

    def _initializeParameters(self, options, flags):
        '''
        Initialize all given and needed parameters. Get region information and
        calculate boundingbox according to it

        '''
        self._debug("_initializeParameters", "started")

        self._env = os.environ.copy()
        self._env['GRASS_MESSAGE_FORMAT'] = 'gui'
        g.gisenv(set="GRASS_MESSAGE_FORMAT=gui")

        for key in ['url', 'coverage','output','location']:
            self.params[key] = options[key].strip()

        if not self.params['output']:
            self.params['output'] = self.params['coverage']
            if not gscript.overwrite():
                result = gscript.find_file(name = self.params['output'], element = 'cell')
                if  result['file']:
                    gscript.fatal("Raster map <%s> does already exist. Choose other output name or toggle flag --o." % self.params['output'])

        for key in ['password', 'username', 'version','region']:
            self.params[key] = options[key]

        # check if authentication information is complete
        if (self.params['password'] and self.params['username'] == '') or \
           (self.params['password'] == '' and self.params['username']):
                gscript.fatal(_("Please insert both %s and %s parameters or none of them." % ('password', 'username')))


        # configure region extent (specified name or current region)
        self.params['region'] = self._getRegionParams(options['region'])
        self.params['boundingbox'] = self._computeBbox(self.params['region'])
        self._debug("_initializeParameters", "finished")


    def _getRegionParams(self,opt_region):
        """!Get region parameters from region specified or active default region

        @return region_params as a dictionary
        """
        self._debug("_getRegionParameters", "started")

        if opt_region:
            reg_spl = opt_region.strip().split('@', 1)
            reg_mapset = '.'
            if len(reg_spl) > 1:
                reg_mapset = reg_spl[1]

            if not gscript.find_file(name = reg_spl[0], element = 'windows',
                                   mapset = reg_mapset)['name']:
                 gscript.fatal(_("Region <%s> not found") % opt_region)

        if opt_region:
            s = gscript.read_command('g.region',
                                    quiet = True,
                                    flags = 'ug',
                                    region = opt_region)
            region_params = gscript.parse_key_val(s, val_type = float)
            gscript.verbose("Using region parameters for region %s" %opt_region)
        else:
            region_params = gscript.region()
            gscript.verbose("Using current grass region")

        self._debug("_getRegionParameters", "finished")
        return region_params


    def _computeBbox(self,region_params):
        """!Get extent for WCS query (bbox) from region parameters

        @return bounding box defined by list [minx,miny,maxx,maxy]
        """
        self._debug("_computeBbox", "started")
        boundingboxvars = ("w","s","e","n")
        boundingbox = list()
        for f in boundingboxvars:
            boundingbox.append(int(self.params['region'][f]))
        gscript.verbose("Boundingbox coordinates:\n %s  \n [West, South, Eest, North]" %boundingbox)
        self._debug("_computeBbox", "finished")
        return boundingbox


    def GetMap(self, options, flags):
        """!Download data from WCS server.

        @return mapname with downloaded data
        """
        self._debug("GetMap", "started")

        self._initializeParameters(options, flags)
        p = self._download()

        if p != 0:
            gscript.fatal("Download or import of WCS data failed.")
            return

        return self.params['output']

    def LinkMap(self, options, flags):
        """!Download data from WCS server.

        @return mapname with downloaded data
        """
        self._debug("GetMap", "started")

        self._initializeParameters(options, flags)
        self.xml_file = self._createXML()
        fin = open(self.xml_file, "r")
        gscript.debug(fin.readlines())

        r.external(input=self.xml_file, output=self.params['output'])
        gscript.try_remove(self.xml_file)


        if p != 0:
            gscript.fatal("Adding WCS as external raster failed.")
            return

        return self.params['output']

    def _fetchCapabilities(self, options, flags):
        """!Download capabilities from WCS server

        @return cap (instance of method _fetchDataFromServer)
        """
        self._debug("_fetchCapabilities", "started")
        cap_url = options['url'].strip()

        if "?" in cap_url:
            cap_url += "&"
        else:
            cap_url += "?"

        cap_url += "SERVICE=WCS&REQUEST=GetCapabilities&VERSION=" + options['version']

        if options['urlparams']:
            cap_url += "&" + options['urlparams']

        gscript.message('Fetching capabilities file\n%s' % cap_url)

        try:
            cap = self._fetchDataFromServer(cap_url, options['username'], options['password'])
            print dir(cap)
        except (IOError, HTTPException), e:
            if urllib2.HTTPError == type(e) and e.code == 401:
                gscript.fatal(_("Authorization failed to <%s> when fetching capabilities") % options['url'])
            else:
                msg = _("Unable to fetch capabilities from <%s>: %s") % (options['url'], e)

                if hasattr(e, 'reason'):
                    msg += _("\nReason: ") + str(e.reason)

                gscript.fatal(msg)
        self._debug("_fetchCapabilities", "finished")
        return cap

    def _fetchDataFromServer(self, url, username = None, password = None):
        """!Fetch data from server

        """
        self._debug("_fetchDataFromServer", "started")

        request = urllib2.Request(url)
        if username and password:
                    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
                    request.add_header("Authorization", "Basic %s" % base64string)

        try:
            return urllib2.urlopen(request)
        except ValueError as error:
            gscript.fatal("%s" % error)

        self._debug("_fetchDataFromServer", "finished")


    def GetCapabilities(self, options,flags):
        """!Get capabilities from WCS server and print to stdout

        """
        self._debug("GetCapabilities", "started")

        cap  = self._fetchCapabilities(options,flags)
        root = etree.fromstringlist(cap.readlines())
        cov_offering = []
        for label in root.iter('{*}CoverageOfferingBrief'):
            cov_offering.append(label.find('{*}name').text + " : " + label.find('{*}label').text)
        gscript.message("Available layers:")
        gscript.message('\n'.join(cov_offering))
        self._debug("GetCapabilities", "finished")



    def _tempfile(self):
        """!Create temp_file and append list self.temp_files_to_cleanup
            with path of file

        @return string path to temp_file
        """
        self._debug("_tempfile", "started")
        temp_file = gscript.tempfile()
        if temp_file is None:
            gscript.fatal(_("Unable to create temporary files"))

        # list of created tempfiles for destructor
        self.temp_files_to_cleanup.append(temp_file)
        self._debug("_tempfile", "finished")

        return temp_file

class WCSGdalDrv(WCSBase):
    def _createXML(self):
        """!Create XML for GDAL WCS driver

        @return path to XML file
        """
        self._debug("_createXML", "started")

        gdal_wcs = etree.Element("WCS_GDAL")
        server_url = etree.SubElement(gdal_wcs, "ServiceUrl")
        server_url.text =self.params['url']

        version = etree.SubElement(gdal_wcs, "Version")
        version.text =self.params['version']

        coverage = etree.SubElement(gdal_wcs, "CoverageName")
        coverage.text = self.params['coverage']

        if self.params['username']:
            userpwd = etree.SubElement(gdal_wcs,'UserPwd')
            userpwd.text = self.params['username']+':'+ self.params['password']

        xml_file = self._tempfile()

        etree_gdal_wcs = etree.ElementTree(gdal_wcs)
        gscript.debug(etree_gdal_wcs)
        etree.ElementTree(gdal_wcs).write(xml_file)

        self._debug("_createXML", "finished -> %s" % xml_file)

        return xml_file

    def _createVRT(self):
        '''! create VRT with help of gdalbuildvrt program
        VRT is a virtual GDAL dataset format

        @return path to VRT file
        '''
        self._debug("_createVRT", "started")
        vrt_file = self._tempfile()
        command = ["gdalbuildvrt", '-te']
        command += self.params['boundingbox']
        command += [vrt_file, self.xml_file]
        command = [str(i) for i in command]

        gscript.verbose(' '.join(command))

        self.process = subprocess.Popen(command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        self.out, self.err = self.process.communicate()
        gscript.verbose(self.out)

        if self.err:
            gscript.verbose(self.err+"\n")
            if "does not exist" in self.err:
                gscript.warning('Coverage "%s" cannot be opened / does not exist.' % self.params['coverage'])
            gscript.fatal("Generation of VRT-File failed (gdalbuildvrt ERROR). Set verbose-flag for details.")

        self._debug("_createVRT", "finished")
        return vrt_file

    def _download(self):
        """!Downloads data from WCS server using GDAL WCS driver

        @return ret (exit code of r.in.gdal module)
        """
        self._debug("_download", "started")
        self.xml_file = self._createXML()
        self.vrt_file = self._createVRT()

        gscript.message('Starting module r.in.gdal ...')
        
        if self.params['location'] == "":
            p = gscript.start_command('r.in.gdal',
                     input=self.vrt_file,
                     output=self.params['output'],
                     stderr = gscript.PIPE,
                     env = self._env
            )
        
        else:
            p = gscript.start_command('r.in.gdal',
                     input=self.vrt_file,
                     output=self.params['output'],
                     location = self.params['location'],
                     stderr = gscript.PIPE,
                     env = self._env
            )
        
        # percent status messagei
        while p.poll() is None:
            line = p.stderr.readline()
            linepercent = line.replace('GRASS_INFO_PERCENT:','').strip()
            if linepercent.isdigit():
                #print linepercent
                gscript.percent(int(linepercent),100,1)
            else:
                gscript.verbose(line)
        
        gscript.percent(100,100,5)

        ret = p.wait()
        if ret != 0:
            gscript.fatal('r.in.gdal for %s failed.' % self.vrt_file )
        else:
            gscript.message('r.in.gdal was successful for new raster map %s ' % self.params['output'] )

        gscript.try_remove(self.vrt_file)
        gscript.try_remove(self.xml_file)
        self._debug("_download", "finished")

        return ret


def main():
    url = options['url']
    coverage = options['coverage']
    output = options['output']
    location = options['location']
    region = options['region']
    urlparams = options['urlparams']
    username = options['username']
    password = options['password']
    flag_c = flags['c']
    flag_e = flags['e']


    options['version']="1.0.0" # right now only supported version, therefore not in GUI

    gscript.debug("Using GDAL WCS driver")
    wcs = WCSGdalDrv()  # only supported driver

    if flag_c:
        wcs.GetCapabilities(options,flags)

    elif flag_e:
        external_map = wcs.LinkMap(options,flags)

    else:
        gscript.message("Importing raster map into GRASS...")
        fetched_map = wcs.GetMap(options,flags)
        if not fetched_map:
            gscript.warning(_("Nothing imported.\n Data not has been downloaded from wcs server."))
            return 1

    return 0

if __name__ == "__main__":
    options, flags = gscript.parser()
    sys.exit(main())
