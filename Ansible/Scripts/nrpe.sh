#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
sudo apt-get install -y autoconf gcc libc6 libmcrypt-dev make libssl-dev wget
cd /tmp

echo "NRPE Installing Process Start"
wget --no-check-certificate -O nrpe.tar.gz https://github.com/NagiosEnterprises/nrpe/archive/nrpe-4.0.3.tar.gz
tar xzf nrpe.tar.gz
cd /tmp/nrpe-nrpe-4.0.3/

echo "Start Compile NRPE"
sudo ./configure --enable-command-args --with-ssl-lib=/usr/lib/x86_64-linux-gnu/
sudo make all
sudo make install-groups-users
sudo make install
sudo make install-config

sudo sh -c "echo >> /etc/services"
sudo sh -c "sudo echo '# Nagios services' >> /etc/services"
sudo sh -c "sudo echo 'nrpe    5666/tcp' >> /etc/services"

echo "start NRPE service"
sudo make install-init
sudo systemctl enable nrpe.service

echo "Firewalls Setup"
sudo mkdir -p /etc/ufw/applications.d
sudo sh -c "echo '[NRPE]' > /etc/ufw/applications.d/nagios"
sudo sh -c "echo 'title=Nagios Remote Plugin Executor' >> /etc/ufw/applications.d/nagios"
sudo sh -c "echo 'description=Allows remote execution of Nagios plugins' >> /etc/ufw/applications.d/nagios"
sudo sh -c "echo 'ports=5666/tcp' >> /etc/ufw/applications.d/nagios"
sudo ufw allow NRPE
sudo ufw reload

echo "Configure NRPE.CFG & Allow Hosts"
sudo sh -c "sed -i '/^allowed_hosts=/s/$/,nagios.rezo.ai,nagios-azure.rezo.ai/' /usr/local/nagios/etc/nrpe.cfg"

echo ""
sudo service nrpe start
/usr/local/nagios/libexec/check_nrpe -H 127.0.0.1

echo "Install Dependency"
cd ~
sudo apt-get install -y autoconf gcc libc6 libmcrypt-dev make libssl-dev wget bc gawk dc build-essential snmp libnet-snmp-perl gettext

echo "Install Service-Plugin "
cd /tmp
wget --no-check-certificate -O nagios-plugins.tar.gz https://github.com/nagios-plugins/nagios-plugins/archive/release-2.3.3.tar.gz
tar zxf nagios-plugins.tar.gz
cd /tmp/nagios-plugins-release-2.3.3/
sudo ./tools/setup
sudo ./configure
sudo make
sudo make install
/usr/local/nagios/libexec/check_nrpe -H 127.0.0.1 -c check_load
/usr/local/nagios/libexec/check_nrpe -H 127.0.0.1

echo "Install Memory Plugin"
cd /usr/local/nagios/libexec/
sudo wget https://raw.githubusercontent.com/justintime/nagios-plugins/master/check_mem/check_mem.pl
sudo mv check_mem.pl check_mem
sudo chmod +x check_mem

sudo apt-get install -y libsys-statistics-linux-perl

echo "Install Linux_stats.pl Plugin"
cd /usr/local/nagios/libexec/
sudo wget "https://exchange.nagios.org/components/com_mtree/attachment.php?link_id=2516&cf_id=24" -O check_linux_stats.pl
sudo mv check_linux_stats.pl check_linux_stats
sudo chmod +x check_linux_stats

echo "Install Check_ps.sh Plugin"
cd /usr/local/nagios/libexec/
sudo wget "https://exchange.nagios.org/components/com_mtree/attachment.php?link_id=623&cf_id=24" -O check_ps.sh
sudo mv check_ps.sh check_ps
sudo chmod +x check_ps
sudo cp check_load check_linux_stats





###### Manual

#dir to register
sudo vim /usr/local/nagios/etc/nrpe.cfg

#add these as required
command[check_users]=/usr/local/nagios/libexec/check_users -w 2 -c 3
command[check_load]=/usr/local/nagios/libexec/check_linux_stats  -w 80 -c 90
command[check_hda1]=/usr/local/nagios/libexec/check_disk -w 20% -c 10% -p /
command[check_zombie_procs]=/usr/local/nagios/libexec/check_procs -w 1 -c 2 -s Z
command[check_total_procs]=/usr/local/nagios/libexec/check_procs -w 150 -c 200
command[check_mem]=/usr/local/nagios/libexec/check_mem -C -f -w 20 -c 15
command[check_ping]=/usr/local/nagios/libexec/check_ping -H localhost -w 100,20% -c 500,40%
command[check_procs_percent]=/usr/local/nagios/libexec/check_procs -w 70 -c 80 --metric=CPU
command[check_swap]=/usr/local/nagios/libexec/check_swap -w 30% -c 20%
command[check_process]=/usr/local/nagios/libexec/check_ps -p java -w 10 -c 20 -t cpu

#change the command as per need
command[check_http]=/usr/local/nagios/libexec/check_http -I localhost -p 80
command[check_http]=/usr/local/nagios/libexec/check_http -H delhivery.rezo.ai -u "http://delhivery.rezo.ai/scp/login.php"


https://exchange.nagios.org/components/com_mtree/attachment.php?link_id=2516&cf_id=24

sudo service nrpe restart
/usr/local/nagios/libexec/check_mem -C -f -w 20 -c 15

/usr/local/nagios/libexec/check_ps -p java -w 10 -c 20 -t cpu
/usr/local/nagios/libexec/check_error_count