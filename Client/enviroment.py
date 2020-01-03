#! /usr/bin/python3
import os, sys
import time
from subprocess import check_output

os.system("apt-get install -y python3 python3-dev python3-pip")
#os.system("apt-get install -y gcc libssl-dev")
#os.system("apt-get install -y libmysqlclient-dev")
#os.system("apt-get install libmariadbclient-dev")
os.system("pip3 install mysqlclient")
os.system("pip3 install get-mac")
os.system("sudo pip3 install ipgetter2==1.1.9")
os.system("pip3 install requests")

# supervisor install 
os.system("apt-get install -y supervisor")
os.system("cp /home/pi/School_Monitor_System/Client/client.conf /etc/supervisor/conf.d")
os.system("service supervisor restart")
while True:
    if (len(str(check_output(["pidof","python3"]).decode("utf-8")).split("\n")[0].split(" ")) == 2):
        print("supervisor is on")
        break;
    else:
        print("supervisor is dead")
    time.sleep(1)