#!/bin/bash

#go into root
sudo -i

#change timezone
cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime

#change time
while true;
do
 read -p "input now time(EXAMPLE:2019-04-20 17:41:30):" time;

 if [ ! -n "$time" ]; then
  echo "please input a time"
  echo "EXAMPLE: 2019-04-20 17:41:30"
 else
   echo $time
   break
 fi
done
date -s "$time"
apt update -y

#build environmant
apt install acl composer fping git graphviz imagemagick mariadb-client mariadb-server mtr-tiny nginx-full nmap php7.0-cli php7.0-curl php7.0-fpm php7.0-gd php7.0-mbstring php7.0-mcrypt php7.0-mysql php7.0-snmp php7.0-xml php7.0-zip python-memcache python-mysqldb rrdtool snmp snmpd whois

#create new user
read -p "input username:" username;
useradd $username -d /opt/librenms -M -r
usermod -a -G $username www-data

#install librenms
cd /opt
composer create-project --no-dev --keep-vcs librenms/librenms librenms 1.48

