import os, sys
import requests
import time
from subprocess import check_output
import json

# system time setup
os.system("timedatectl set-timezone Asia/Taipei")

# mysql install
os.system("apt-get update")
os.system("apt-get install -y mysql-server")
os.system("apt-get install -y mysql-client")
os.system("apt-get install -y libmysqlclient-dev")
os.system("service mysql start")

# python3-install
os.system("apt-get install -y python3-dev python3-pip libmysqlclient-dev")
os.system("apt-get install -y build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev")
os.system("pip3 install flask")
os.system("pip3 install requests")
os.system("pip3 install mysqlclient")
os.system("pip3 install xlrd")

# grafana-install
os.system("apt-get install -y apt-transport-https")
os.system("apt-get install -y software-properties-common wget")
os.system('add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"')
os.system("wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -")
os.system("apt-get update")
os.system("apt-get install -y grafana=6.7.3")
os.system("systemctl daemon-reload")
os.system("systemctl start grafana-server")
os.system("systemctl enable grafana-server")
os.system("service grafana-server start")
os.system("grafana-cli plugins install grafana-clock-panel")
os.system("service grafana-server restart")

# grafana setup
f = open('/etc/mysql/debian.cnf', 'r')
fr = f.read()
mysql_user = fr.split(" = ")[2].split("\n")[0]
mysql_passwd = fr.split(" = ")[3].split("\n")[0]

create_grafana_datasource = 0
create_grafana_dashboard = 0
datasources = open("./datasource.json", "r")
dashboard = open("./dashboard.json", "r")
datasources_info = datasources.read()
dashboard_info = dashboard.read()
datasources_info_json = json.loads(str(datasources_info))
datasources_info_json["user"] = mysql_user
datasources_info_json["password"] = mysql_passwd
datasources_info = json.dumps(datasources_info_json)
# print(datasources_info)
# print(dashboard_info)

# prometheus setup
os.system("curl -OL https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz")
os.system("tar -zxvf node_exporter-1.0.1.linux-amd64.tar.gz")
os.system("sudo cp node_exporter-1.0.1.linux-amd64/node_exporter /usr/local/bin/")
os.system("sudo cp node.service /etc/systemd/system/node.service")
os.system("curl -OL https://github.com/prometheus/prometheus/releases/download/v2.22.0/prometheus-2.22.0.linux-amd64.tar.gz")
os.system("tar -zxvf prometheus-2.22.0.linux-amd64.tar.gz")
os.system("sudo cp -r prometheus-2.22.0.linux-amd64 /usr/local/bin/")
os.system("sudo mkdir /etc/prometheus")
os.system("sudo cp prometheus.yml /etc/prometheus/prometheus.yml")
os.system("sudo cp prometheus.service /etc/systemd/system/prometheus.service")

os.system("sudo systemctl daemon-reload")
os.system("sudo systemctl enable node")
os.system("sudo systemctl enable prometheus")
os.system("sudo systemctl start node")
os.system("sudo systemctl start prometheus")

# remove update notifier
os.system("sudo rm /usr/bin/update-manager")
os.system("sudo rm /usr/bin/update-notifier")
os.system("sudo echo update-manager hold | sudo dpkg --set-selections")

while (not (create_grafana_datasource and create_grafana_dashboard)):
    try: 
        if (requests.get("http://127.0.0.1:3000/login").status_code == 200):
            '''
            try:
                if(requests.get("http://admin:admin@127.0.0.1:3000/api/datasources/name/librenms-cloud-mysql").status_code == 200)
                    print("datasource exist")
                    create_grafana_datasource = 1
            except:
                print("datasource not exist")
            try:
                if(requests.get("http://admin:admin@127.0.0.1:3000/api/dashboard/name/Librenms").status_code == 200)
                print("dashboard exist")
                create_grafana_dashboard = 1
            except:
                print("dashboard not exist")
            '''
            if (create_grafana_datasource == 0):
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/datasources", data=datasources_info.encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("create datasource")
                    create_grafana_datasource = 1
                except:
                    print("add datasource error")
            if (create_grafana_dashboard == 0):
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/dashboards/db", data=dashboard_info.encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("create dashboard")
                    create_grafana_dashboard = 1
                except:
                    print("add dashboard error")
        else:
            try:
                os.system("service grafana-server start")
            except:
                print("grafana_service error")
    except:
        print("grafana_service error")
        time.sleep(10)

# supervisor install 
os.system("apt-get -y install supervisor")
os.system("cp ./server.conf /etc/supervisor/conf.d")
os.system("service supervisor restart")
while True:
    print(str(check_output(["pidof","python3"]).decode("utf-8")).split("\n")[0].split(" "))
    if (len(str(check_output(["pidof","python3"]).decode("utf-8")).split("\n")[0].split(" ")) >= 2):
        print("supervisor is on")
        break;
    else:
        print("supervisor is dead")
    time.sleep(1)

print("wait for system check")
time.sleep(10)
