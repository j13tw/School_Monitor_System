import os, sys
import requests
import datetime, time
from subprocess import check_output
import json

print("[School Monitoring System Installer]")

# setup install log placement
logPath = "/tmp/server.log"

# system time setup
os.system("timedatectl set-timezone Asia/Taipei")

# system update
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [system update step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tsystem update step:")

# mysql install
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [mysql service install step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tmysql service install step:")
os.system("apt-get install -y mysql-server >> " + logPath)
os.system("apt-get install -y mysql-client >> " + logPath)
os.system("apt-get install -y libmysqlclient-dev >> " + logPath)
os.system("service mysql start")

# python3-install
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [python3 install step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tpython3 install step:")
os.system("apt-get install -y python3-dev python3-pip libmysqlclient-dev >> " + logPath)
os.system("apt-get install -y build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev >> " + logPath)
os.system("apt-get install -y curl >> " + logPath)

# python3 package install
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [python3 package install step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tpython3 package install step:")
os.system("pip3 install flask >> " + logPath)
os.system("pip3 install requests >> " + logPath)
os.system("pip3 install mysqlclient >> " + logPath)
os.system("pip3 install xlrd==1.2.0 >> " + logPath)

# grafana-install
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [grafana install step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tgrafana install step:")
os.system("apt-get install -y apt-transport-https >> " + logPath)
os.system("apt-get install -y software-properties-common wget >> " + logPath)
os.system('add-apt-repository "deb https://packages.grafana.com/oss/deb stable main" >>' + logPath)
os.system("wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -")
os.system("apt-get update >> " + logPath)
os.system("apt-get install -y grafana=6.7.3 >> " + logPath)

# grafana initial
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [grafana initial step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tgrafana initial step:")
os.system("systemctl daemon-reload")
os.system("systemctl start grafana-server")
os.system("systemctl enable grafana-server")
os.system("service grafana-server start")
os.system("grafana-cli plugins install grafana-clock-panel >> " + logPath)
os.system("service grafana-server restart")

# grafana setup
f = open('/etc/mysql/debian.cnf', 'r')
fr = f.read()
mysql_user = fr.split(" = ")[2].split("\n")[0]
mysql_passwd = fr.split(" = ")[3].split("\n")[0]

create_grafana_datasource = 0
create_grafana_dashboard = 0

# fix mysql user/passwd
mysql_datasources_info = open("./grafana-import/mysql-datasource.json", "r").read()
mysql_datasources_info_json = json.loads(str(mysql_datasources_info))
mysql_datasources_info_json["user"] = mysql_user
mysql_datasources_info_json["password"] = mysql_passwd
mysql_datasources_info = json.dumps(mysql_datasources_info_json)
# print(mysql_datasources_info)

# prometheus setup
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [prometheus monitoring service initial step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tprometheus monitoring service initial step:")
os.system("curl -OL -s https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz >> " + logPath)
os.system("tar -zxvf node_exporter-1.0.1.linux-amd64.tar.gz >> " + logPath)
os.system("cp node_exporter-1.0.1.linux-amd64/node_exporter /usr/local/bin/")
os.system("cp ./prometheus-monitoring/node.service /etc/systemd/system/node.service")
os.system("curl -OL -s https://github.com/prometheus/prometheus/releases/download/v2.22.0/prometheus-2.22.0.linux-amd64.tar.gz >> " + logPath)
os.system("tar -zxvf prometheus-2.22.0.linux-amd64.tar.gz >> " + logPath)
os.system("cp -r prometheus-2.22.0.linux-amd64/prometheus /usr/local/bin/")
os.system("mkdir /etc/prometheus")
os.system("cp ./prometheus-2.22.0.linux-amd64/prometheus.yml /etc/prometheus/prometheus.yml")
os.system("cp ./prometheus-monitoring/prometheus.service /etc/systemd/system/prometheus.service")
os.system("systemctl daemon-reload")
os.system("systemctl enable node")
os.system("systemctl enable prometheus")
os.system("systemctl start node")
os.system("systemctl start prometheus")

# remove update notifier
os.system("rm /usr/bin/update-manager")
os.system("rm /usr/bin/update-notifier")
os.system("echo update-manager hold | dpkg --set-selections")

# auto backup
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [inject auto_backup_db service step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tinject auto_backup_db service step:")
cronpath = os.path.abspath(os.getcwd())
os.system("grep 'roor python3 " + cronpath +"/k12eabk.py' /etc/crontab || echo '0 0 1 * * root python3 " + cronpath + "/k12eabk.py' >> /etc/crontab")

# grafana initial step
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [grafana initial step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tgrafana initial step:")
while (not (create_grafana_datasource == 0 and create_grafana_dashboard == 0)):
    try: 
        if (requests.get("http://127.0.0.1:3000/login").status_code == 200):
            if (create_grafana_datasource == 0):
                print("\tcreate datasource step:")
                # main service database mysql
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/datasources", data=mysql_datasources_info.encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate mysql datasource")
                    create_grafana_datasource = 1
                except:
                    print("\t\tcreate mysql datasource error")
                # monitoring service database prometheus
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/datasources", data=open("./grafana-import/prometheus-datasource.json", "r").read().encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate prometheus datasource")
                    create_grafana_datasource = create_grafana_datasource * 1
                except:
                    print("\t\tcreate prometheus datasource error")
                    create_grafana_datasource = 0
            if (create_grafana_dashboard == 0):
                print("\tcreate datasource step:")
                # librenms-cloud-dashboard-v1 (2020-02).json
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/dashboards/db", data=open("./grafana-import/librenms-cloud-dashboard-v1 (2020-02).json", "r").read().encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate librenms-cloud-dashboard-v1 (2020-02) dashboard")
                    create_grafana_dashboard = 1
                except:
                    print("\t\tcreate librenms-cloud-dashboard-v1 (2020-02) dashboard error")
                # librenms-cloud-dashboard-v1 (2020-02) for school.json
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/dashboards/db", data=open("./grafana-import/librenms-cloud-dashBoard-v1 (2020-02) for school.json", "r").read().encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate librenms-cloud-dashboard-v1 (2020-02) for school dashboard")
                    create_grafana_dashboard = create_grafana_dashboard*1
                except:
                    print("\t\tcreate librenms-cloud-dashboard-v1 (2020-02) for school dashboard error")
                    create_grafana_dashboard = 0
                # librenms-cloud-dashboard-v1 (2020-05).json
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/dashboards/db", data=open("./grafana-import/librenms-cloud-dashboard-v1.1 (2020-05).json", "r").read().encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate librenms-cloud-dashboard-v1.1 (2020-05) dashboard")
                    create_grafana_dashboard = create_grafana_dashboard*1
                except:
                    print("\t\tcreate librenms-cloud-dashboard-v1 (2020-05) dashboard error")
                    create_grafana_dashboard = 0
                # librenms-cloud-dashboard-v1 (2020-05) for school.json
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/dashboards/db", data=open("./grafana-import/librenms-cloud-dashboard-v1.1 (2020-05) for school.json", "r").read().encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate librenms-cloud-dashboard-v1.1 (2020-05) for school dashboard")
                    create_grafana_dashboard = create_grafana_dashboard*1
                except:
                    print("\t\tcreate librenms-cloud-dashboard-v1 (2020-05) for school dashboard error")
                    create_grafana_dashboard = 0
                # nutpes_test.json
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/dashboards/db", data=open("./grafana-import/nutpes_test.json", "r").read().encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate nutpes_test dashboard")
                    create_grafana_dashboard = create_grafana_dashboard*1
                except:
                    print("\t\tcreate nutpes_test dashboard error")
                    create_grafana_dashboard = 0
                # nutpes_test.json
                try:
                    requests.post("http://admin:admin@127.0.0.1:3000/api/dashboards/db", data=open("./grafana-import/prometheus-node-exporter-dashboard.json", "r").read().encode('utf-8'), headers={"Content-Type": "application/json"})
                    print("\t\tcreate prometheus-node-exporter-dashboard dashboard")
                    create_grafana_dashboard = create_grafana_dashboard*1
                except:
                    print("\t\tcreate prometheus-node-exporter-dashboard error")
                    create_grafana_dashboard = 0
        else:
            try:
                os.system("service grafana-server start")
            except:
                print("grafana_service error")
    except:
        print("grafana_service error")
    print("create_grafana_datasource", create_grafana_datasource)
    print("create_grafana_dashboard", create_grafana_dashboard)
    if (create_grafana_dashboard * create_grafana_datasource == 0): time.sleep(10)
        
#Preprocess
#os.system('sed -i \'0,/"id": .*/{s/"id": .*/"id": null,/}\' *.json')

# # datasources
# os.system("curl 'http://admin:admin@127.0.0.1:3000/api/datasources' -X POST -H 'Content-Type: application/json;charset=UTF-8' --data-binary @./grafana-import/prometheus-datasource.json")

# # dashboards
# os.system('curl --user admin:admin "http://127.0.0.1:3000/api/dashboards/db" -X POST -H "Content-Type:application/json" --data @$(pwd)/librenms-cloud-dashboard-v1.1\(2020-05\)-1607310113421.json')
# os.system('curl --user admin:admin "http://127.0.0.1:3000/api/dashboards/db" -X POST -H "Content-Type:application/json" --data @$(pwd)/Prometheus\ Node\ Exporter\ Dashboard-1607310144755.json')
# os.system('curl --user admin:admin "http://127.0.0.1:3000/api/dashboards/db" -X POST -H "Content-Type:application/json" --data @$(pwd)/librenms-cloud-dashboard-v1.1\(2020-05\)\ for\ school-1607310121646.json')
# os.system('curl --user admin:admin "http://127.0.0.1:3000/api/dashboards/db" -X POST -H "Content-Type:application/json" --data @$(pwd)/LibreNMS-Cloud-DashBoard-V1\ \(2020-02\)-1607310058540.json')
# os.system('curl --user admin:admin "http://127.0.0.1:3000/api/dashboards/db" -X POST -H "Content-Type:application/json" --data @$(pwd)/LibreNMS-Cloud-DashBoard-V1\ \(2020-02\)\ for\ school-1607310087189.json')
# os.system('curl --user admin:admin "http://127.0.0.1:3000/api/dashboards/db" -X POST -H "Content-Type:application/json" --data @$(pwd)/nutpes_test-1607310133406.json')

# supervisor install 
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [inject supervisor daemon service step] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tinject supervisor daemon service step:")
os.system("apt-get -y install supervisor >> " + logPath)
os.system("cp ./supervisor-daemon/server.conf /etc/supervisor/conf.d")
os.system("service supervisor restart")

# supervisor check startup 
os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [supervisor check startup ] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tsupervisor check startup step:")
while True:
    # print(str(check_output(["pidof","python3"]).decode("utf-8")).split("\n")[0].split(" "))
    if (len(str(check_output(["pidof","python3"]).decode("utf-8")).split("\n")[0].split(" ")) >= 2):
        print("\tsupervisor is on")
        break;
    else:
        print("\tsupervisor is dead")
    time.sleep(5)

os.system("echo ---\t" + str(datetime.datetime.now()).split(".")[0] + "\t [wait for system check] \t--- >> " + logPath)
print(str(datetime.datetime.now()).split(".")[0] + "\tInstall Success !")
time.sleep(10)
