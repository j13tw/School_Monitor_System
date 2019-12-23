#! /usr/bin/python3
import os, sys

os.system("apt-get install -y python3 python3-dev python3-pip")
#os.system("apt-get install gcc libssl-dev")
#os.system("apt-get install -y libmysqlclient-dev")
#os.system("apt-get install libmariadbclient-dev")
os.system("pip3 install mysqlclient")
os.system("pip3 install get-mac")
os.system("pip3 install ipgetter2")
os.system("pip3 install requests")

# supervisor install 
os.system("apt-get install supervisor")
os.system("cp ./client.conf /etc/supervisor/conf.d")
os.system("service supervisor restart")
while True:
    if (len(str(check_output(["pidof","python3"]).decode("utf-8")).split("\n")[0].split(" ")) == 2):
        print("supervisor is on")
        break;
    else:
        print("supervisor is dead")
    time.sleep(1)