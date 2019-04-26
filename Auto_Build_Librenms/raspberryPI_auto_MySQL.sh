#!/bin/bash

#go into root
#sudo -i

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
apt install mariadb-client mariadb-server
#apt install acl composer fping git graphviz imagemagick mariadb-client mariadb-server mtr-tiny nginx-full nmap php7.0-cli php7.0-curl php7.0-fpm php7.0-gd php7.0-mbstring php7.0-mcrypt php7.0-mysql php7.0-snmp php7.0-xml php7.0-zip python-memcache python-mysqldb rrdtool snmp snmpd whois -y
#apt install mysql -y

#creare mysql
#read -p "Please input DBname"DBname;
read -p "Please input username:"username;
read -p "Please input librenms IP:"IP;
read -p "Please input password:"password;
                                     #DBname                                                                                                                             DBname
mysql -uroot -p  <<< 'CREATE DATABASE librenms CHARACTER SET utf8 COLLATE utf8_unicode_ci;CREATE USER '$username'@'$IP'IDENTIFIED BY '$password';GRANT ALL PRIVILEGES ON librenms.* TO '$username'@'$IP';FLUSH PRIVILEGES;exit'

echo >> "innodb_file_per_table=1" /etc/mysql/mariadb.conf.d/50-server.cnf
echo >> "lower_case_table_names=0" /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl restart mysql

