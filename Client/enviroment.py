#! /usr/bin/python3
import os, sys

os.system("apt-get install -y python3 python3-dev python3-pip")
#os.system("apt-get install -y libmysqlclient-dev")
os.system("pip3 install mysqlclient")
os.system("pip3 install get-mac")
os.system("pip3 install ipgetter2")
os.system("pip3 install requests")