#!/bin/sh


## variables
export SOURCEDIR=$PWD/source
export GISBASE=~/gis

case "$1" in

    gisbase)
        sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
        sudo aptitude update
        ;;


    postgis)
        sudo aptitude install postgresql-9.3 pgadmin3 postgresql-contrib postgresql-9.3-postgis-2.1 postgis
        cat >> /etc/postgresql/9.3/main/pg_hba.conf <<EOF
host       all          gis             samenet              md5
hostnossl  all          all             0.0.0.0/0            reject
hostssl    all          gis             all                  md5
EOF

        cat >> /etc/postgresql/9.3/main/postgresql.conf <<EOF
listen_addresses = '*'
EOF

        service postgresql restart
        ;;

    mapserver)
        sudo aptitude install cgi-mapserver apache2 libapache2-mod-fcgid libapache2-mod-auth-plain tinyows

        mkdir $GISBASE/mapserver -p
        cd  $GISBASE/mapserver
        ln -s $SOURCEDIR/mapserver/* .
        cd -

        ln -s $SOURCEDIR/apache2/sites-available/* /etc/apache2/sites-available/

        a2ensite 002-mapserv-localhost
        a2enmod fcgid  rewrite

        service apache2 restart

        cd /usr/lib/cgi-bin
        ln -s mapserv mapserv.fcgi
        cd -
        chown www-data:gis /gis/mapserv -R

        echo "Task finished. http://localhost/ows bzw. /wfs ready."
        echo "Steps to enable ssl encryption, authentication and access from internet:"
        echo "1st generate apache-cert.pem apache-key.pem (see http://wiki.ubuntuusers.de/Apache/SSL)"
        echo "2nd $ a2enmod ssl; a2ensite 001-mapserv-ssl.conf"
        echo "3d  $ service apache2 restart "
        ;;

    bcache)
        sudo add-apt-repository ppa:g2p/storage
	sudo aptitude install bcache-tools
        # further preparations needed (make-bcache, edit fstab, ...)
        # see: http://bcache.evilpiepirate.org/
        cat > /etc/fstab.d/10bcachehome <<EOF
/dev/bcache0 /archive ext4 defaults,rw,errors=remount-ro 0 2
EOF
        ;;

    powernap)
        add-apt-repository ppa:linrunner/tlp ;  aptitude update
        aptitude install powernap  tlp tlp-rdw
        echo "Installed. Configure /etc/default/powernap /etc/powernap/config /etc/default/tlp"
        ;;

    samba)
        aptitude -y install samba libpam-smbpass
        cp smb.conf
        smbpasswd -a martinz
        addgroup --system sysadmin
        addgroup --system machines
        smbpasswd -a root
        net rpc rights grant "EXAMPLE\Domain Admins" SeMachineAccountPrivilege SePrintOperatorPrivilege
        SeAddUsersPrivilege SeDiskOperatorPrivilege SeRemoteShutdownPrivilege
        sudo net groupmap add ntgroup="Domain Admins" unixgroup=sysadmin rid=512 type=d

        # add logon-script
        mkdir /home/samba/netlogon -p
        touch /home/samba/netlogon/logon.cmd

        # allow Windows 7
        cat > /home/samba/sambafix.reg << EOF
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\LanManWorkstation\Parameters]

"DomainCompatibilityMode"=dword:00000001
"DNSNameResolutionRequired"=dword:00000000
EOF

        service samba restart
        service smbd restart
        service nmbd restart
        ;;


    x2goserver)
        sudo add-apt-repository ppa:x2go/stable
        aptitude update
        aptitude install x2goclient x2goserver x2goserver-extensions x2goplugin-provider sshfs
        ;;


    gitolite3)
        aptitude install gitolite3
        ;;




    ssh)
        aptitude install openssh-server
            addgroup --system sshlogin
            echo "AllowGroups sshlogin" >> /etc/ssh/sshd_config
            echo "PasswordAuthentication no" >> /etc/ssh/sshd_config
            #open non-default port
            #echo "Port 7922" >> /etc/ssh/sshd_config
            service ssh restart
            adduser martinz sshlogin
        ;;

    virt-manager)
        aptitude install qemu-kvm qemu-utils virt-manager  sharutils
        cpu-checker libvirt-bin
        ;;


    *)
        echo "Installation shell script utility \n"
	echo "Run as user with sudo rights \n"
        echo "Usage: $0 {gisbase|grass7|grass7addons|postgis|mapserv|chenyx06|mrsid|...|}"
        echo "  gisbase  : Add only ubuntugis repository here. Run first!"
        echo "  postgis : Install PostgreSQL/Postgis server."
        echo "  mapserv  : Install UMN Mapserver for WMS/WCS/WFS."
        echo "  chenyx06  : Download and install CH1903LV03 to CH1903+/LV95 datum transformation files."
        echo "  mrsid  : Build and install MrSID-format GDAL plugin."
        echo "  bcache  : Install bcache SSD cache for harddisk."
        echo "  powernap  : Install powernap service for automatic standby when not used."
        echo "  "
        echo "other useful server services  "
        echo "  x2goserver  : remote X sessions"
        echo "  ssh  : Install openssh server "
        echo "  gitolite3  : for own GIT repository "
        echo "  samba  : Install openssh server "
        echo "  virt-manager  : for managing and running virtualized hosts"

        ;;
esac
