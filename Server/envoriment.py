import os, sys

os.system("apt-get install -y python3-dev python3-pip libmysqlclient-dev")
os.system("apt-get install python3 python-dev python3-dev \
     build-essential libssl-dev libffi-dev \
     libxml2-dev libxslt1-dev zlib1g-dev \
     python-pip")
os.system("pip3 install flask")
os.system("pip3 install request")
os.system("pip3 install requests")
os.system("pip3 install mysqlclient")
os.system("pip3 install docker")