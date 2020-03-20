#! /usr/bin/python3
import os, sys
import time
from subprocess import check_output

os.system("apt-get install -y python3 python3-dev python3-pip")
# os.system("apt-get install -y gcc libssl-dev")
os.system("apt-get install -y libmysqlclient-dev")
# os.system("apt-get install libmariadbclient-dev")
# os.system("apt-get install -y libmysql++-dev")
# os.system("pip3 install https://www.piwheels.org/simple/mysqlclient/mysqlclient-1.4.6-cp35-cp35m-linux_armv7l.whl")
os.system("pip3 install get-mac")
os.system("pip3 install ipgetter2")
# os.system("wget https://files.pythonhosted.org/packages/bd/c6/54f2a8e8a187b537d588a3760b7a14feb5e0057c708b29b8e094a3383021/ipgetter2-1.1.9.zip")
# os.system("apt-get install -y unzip")
# os.system("unzip ipgetter2-1.1.9.zip")
# os.chdir("ipgetter2-1.1.9")
# os.system("python3 setup.py install --user")
# os.chdir("..")
os.system("pip3 install requests")
os.system("pip3 install speedtest-cli")

# supervisor install
os.system("apt-get install -y supervisor")
os.system("cp /home/ubuntu/School_Monitor_System/Client/x86_PC/client.conf /etc/supervisor/conf.d")
os.system("service supervisor restart")
while True:
    if (len(str(check_output(["pidof","python3"]).decode("utf-8")).split("\n")[0].split(" ")) == 2):
        print("supervisor is on")
        break;
    else:
        print("supervisor is dead")
    time.sleep(1)
