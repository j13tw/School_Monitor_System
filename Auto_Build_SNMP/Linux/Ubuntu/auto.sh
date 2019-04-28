#!/bin/bash
 
#if [ $# -eq 0 ]; then
#  echo "please input IP"
#  echo "EXAMPLE:sh (filename) 127.0.0.1"
#  exit
#else
#  echo $1

error=1
ip_count=0
ip_a=0
ip_b=0
ip_c=0
ip_d=0

while [ $error -eq 1 ];
do
 read -p "input librenms IP(EXAMPLE: 127.0.0.1):" IP;
 ip_count=$(echo $IP | awk -F'.' '{ print NF }')
# echo $ip_count
 if [ $ip_count -eq 4 ]; then
   ip_a=$(echo $IP | awk -F'.' '{ print $1 }')
   ip_b=$(echo $IP | awk -F'.' '{ print $2 }')
   ip_c=$(echo $IP | awk -F'.' '{ print $3 }')
   ip_d=$(echo $IP | awk -F'.' '{ print $4 }')
   #echo $ip_a $ip_b $ip_c $ip_d
   if [ ! -n $ip_a ] || [ ! -n $ip_b ] || [ ! -n $ip_c ] || [ ! -n $ip_d ]; then
     error=1
   else
     if [ $ip_a -ge 0 ] && [ $ip_a -le 255 ]  && [ $ip_b -ge 0 ] && [ $ip_b -le 255 ] && [ $ip_c -ge 0 ] && [ $ip_c -le 255 ] && [ $ip_d -ge 0 ] && [ $ip_d -le 255 ]; then
       error=0
     else
       error=1
     fi
   fi
 fi
 if [ $error -eq 1 ]; then
   echo "please input an IP"
   echo "EXAMPLE: 127.0.0.1"
 fi
done

read -p "input rocommunity(default is imac): " str;
if [ ! -n "$str" ]; then
  str='imac'
fi

read -p "input group-team: " group;
while [ ! -n "$group" ];
do
  echo "please key in group-team!"
  read -p "input group-team: " group;
done

read -p "input manage-user: " owner;
while [ ! -n "$owner" ];
do
  echo "please key in device owner!"
  read -p "input manage-user: " owner;
done

read -p "where is the device: " loc;
while [ ! -n "$loc" ];
do
  echo "please key in where is the device!"
  read -p "where is the device: " loc;
done

#echo IP: $IP str:$str;

apt update -y
apt install net-tools -y
apt install snmpd snmp-mibs-downloader -y
sed -i '5c #export MIBS=' /etc/default/snmpd
sed -i '11c SNMPDOPTS="'"-Lsd -Lf /dev/null -u snmp -g snmp -I -smux, -p /run/snmpd.pid"'"' /etc/default/snmpd

##get IP
#MY_IP=$(hostname -I) or
#IP=$(ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' |cut -d: -f2 | awk '{ print $1}')
#echo $MY_IP

# change snmp.conf configure
sed -i '15c agentAddress  udp:0.0.0.0:161' /etc/snmp/snmpd.conf
sed -i '49c #rocommunity public  localhost' /etc/snmp/snmpd.conf
sed -i '51c #rocommunity public  localhost    -V systemonly' /etc/snmp/snmpd.conf
sed -i '53c #rocommunity6 public  localhost   -V systemonly' /etc/snmp/snmpd.conf

# config snmp listen IP
sed -i '50c rocommunity '$str' '$IP'' /etc/snmp/snmpd.conf
# config device location
sed -i '79c sysLocation '$loc', [24.1494806,120.6838636]' /etc/snmp/snmpd.conf
# config device owner && group
sed -i '80c sysContact '$owner'<'$group'-team>' /etc/snmp/snmpd.conf
# reboot snmp service
service snmpd restart
#fi
