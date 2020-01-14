#!/bin/bash

#go into root
#sudo -i

#change timezone
sudo p /usr/share/zoneinfo/Asia/Taipei /etc/localtime

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
sudo date -s "$time"
sudo apt update -y

#build environmant
sudo apt install acl composer fping git graphviz imagemagick mariadb-client mariadb-server mtr-tiny nginx-full nmap php7.0-cli php7.0-curl php7.0-fpm php7.0-gd php7.0-mbstring php7.0-mcrypt php7.0-mysql php7.0-snmp php7.0-xml php7.0-zip python-memcache python-mysqldb rrdtool snmp snmpd whois -y

#create new user
#read -p "input username:" username;
#useradd $username -d /opt/librenms -M -r
#usermod -a -G $username www-data

#install librenms
cd /opt
sudo composer create-project --no-dev --keep-vcs librenms/librenms librenms 1.48

#change php.ini timezome
sed -i '924c date.timezone = Asia/Taipei' /etc/php/7.0/fpm/php.ini
sed -i '924c date.timezone = Asia/Taipei' /etc/php/7.0/cli/php.ini

sudo phpenmod mcrypt
sudo systemctl restart php7.0-fpm

#edit /etc/nginx/conf.d/librenms.conf

cd
sudo cp School_Monitor_System/Auto_Build_Librenms/Configure_NGINX.txt /etc/nginx/conf.d/librenms.conf

read -p "input DB_HOST:" DB_HOST;
read -p "input DB_DATABASE:" DB_DATABASE;
read -p "input DB_USERNAME:" DB_USERNAME;
read -p "input DB_PASSWORD:" DB_PASSWORD;

cd
sed -i '3c DB_HOST='$DB_HOST''  /opt/librenms/.env
sed -i '4c DB_DATABASE='$DB_DATABASE'' /opt/librenms/.env
sed -i '5c DB_USERNAME='$DB_USERNAME'' /opt/librenms/.env
sed -i '6c DB_PASSWORD='$DB_PASSWORD'' /opt/librenms/.env

cd
sed -i "6c "'$config['"'db_host'""] =""'$DB_HOST';" /opt/librenms/config.php.default
sed -i "7c "'$config['"'db_user'""] =""'$DB_USERNAME';" /opt/librenms/config.php.default
sed -i "8c "'$config['"'db_pass'""] =""'$DB_PASSWORD';" /opt/librenms/config.php.default
sed -i "9c "'$config['"'db_name'""] =""'$DB_DATABASE';" /opt/librenms/config.php.default
sudo cp /opt/librenms/config.php.default /opt/librenms/config.php

sudo chown -R librenms:librenms /opt/librenms
sudo setfacl -d -m g::rwx /opt/librenms/bootstrap/cache /opt/librenms/storage /opt/librenms/logs /opt/librenms/rrd
sudo chmod -R ug=rwX /opt/librenms/bootstrap/cache /opt/librenms/storage /opt/librenms/logs /opt/librenms/rrd
sudo usermod -a -G librenms www-data

sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

sudo cd /opt/librenms
sudo ./scripts/composer_wrapper.php install --no-dev

sudo cd /opt/librenms
sudo ./validate.php
