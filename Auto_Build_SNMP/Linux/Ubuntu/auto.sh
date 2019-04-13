#!/bin/bash
 
#if [ $# -eq 0 ]; then
#  echo "please input IP"
#  echo "EXAMPLE:sh (filename) 127.0.0.1"
#  exit
#else
#  echo $1

while true;
do
 read -p "input librenms IP(EXAMPLE: 127.0.0.1):" IP;

 if [ ! -n "$IP" ]; then
  echo "please input an IP"
  echo "EXAMPLE: 127.0.0.1"
 else
   echo $IP
   break
 fi



done

read -p "input rocommunity: " str;
if [ ! -n "$str" ]; then
  str='imac-iot'
fi


#echo IP: $IP str:$str;

sudo apt update -y 
sudo apt install net-tools -y
sudo apt install snmpd snmp-mibs-downloader -y
sudo sed -i '5c #export MIBS=' /etc/default/snmpd
sudo sed -i '11c SNMPDOPTS="'"-Lsd -Lf /dev/null -u snmp -g snmp -I -smux, -p /run/snmpd.pid"'"' /etc/default/snmpd


##get IP
#MY_IP=$(hostname -I) or 
#IP=$(ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' |cut -d: -f2 | awk '{ print $1}')
#echo $MY_IP

sudo sed -i '15c agentAddress  udp:0.0.0.0:161' /etc/snmp/snmpd.conf
sudo sed -i '49c rocommunity public  localhost ' /etc/snmp/snmpd.conf

                                     #librenmsIP
sudo sed -i '50c rocommunity '$str' '$IP'' /etc/snmp/snmpd.conf

read -p "input location: " loc;
if [ ! -n "$loc" ]; then
  sudo sed -i '81c sysLocation  Sitting on the Dock of the Bay' /etc/snmp/snmpd.conf
else
  sudo sed -i '81c sysLocation  '$loc'' /etc/snmp/snmpd.conf
fi

sudo service snmpd restart
#fi
