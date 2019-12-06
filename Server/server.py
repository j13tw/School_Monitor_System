#! /usr/bin/python3

from flask import Flask, request
# import MySQLdb
import docker
import json

# define Mysql status
mysql_host = "172.20.10.2"
mysql_port = 3306
mysql_db = ""
mysql_user = "imac"
mysql_passwd = "imacuser"
mysql_error = 0
mysql_output = ""
mysql_status = 0
mysql_connection = None

# define edge node return values
edge_school_id = 0
edge_school_ip = ""
edge_school_mac = ""
edge_school_port = 0
edge_school_container_id = ""

# define mysql command
mysql_create_service_db = "create database edge-regist"
mysql_create_edge_db = "create database "
mysql_create_service_table = "CREATE TABLE school (\
    School_Id           int AUTO_INCREMENT, \
    School_Ip           varchar(17) NOT NULL, \
    School_MAC          varchar(17) NOT NULL, \
    School_Port         int NOT NULL, \
    School_ContainerId  varchar(64) NOT NULL, \
    PRIMARY KEY(School_Id));')"
mysql_push_edge_data = ""
'''
def mysql_connect():
    global mysql_connection
    try:
        conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd, \
            charset="utf8")
        mysql_connection = conn.cursor()
        return 1
    except:
        return 0
'''
# 切換資料庫
#mysql_connection.select_db('edge-regist')

# docker container 啟動
docker_client = docker.from_env()
#docker_create = docker_client.containers.run(image='grafana/grafana', name=1234, ports={'3000/tcp': 1234}, detach=True).id
#docker_delete = client.containers.get(edge_school_container_id).remove(force=True)
app = Flask(__name__)

@app.route('/listContainer', methods=['GET'])
def listContainer():
    x = 0
    container_list = [0]*len(docker_client.containers.list())
    for y in docker_client.containers.list():
        print(y.id, y.name, y.status, y.image.tags[0])
        container_list[x] = {"id": y.short_id, "name": y.name, "status": y.status, "image": y.image.tags[0]}
        x += 1
    print(container_list)
    return str(container_list)

@app.route('/edgeNodeRegist', methods=['POST'])
def edgeNodeRegist():
    if request.method == 'POST':
        try:
            edgedata = json.loads(str(request.json).replace("'", '"'))
            edge_school_id = int(edgedata["school"])
            edge_school_ip = str(edgedata["ip"])
            edge_school_mac = str(edgedata["mac"])
            edge_school_port = 30000 + int(edgedata["school"])
            edge_school_container_id = docker_client.containers.run(image='grafana/grafana', name=str(edge_school_id), ports={'3000/tcp': edge_school_port}, detach=True).short_id
        
            print("School_Id = "+ str(edge_school_id))
            print("School_Ip = "+ edge_school_ip)
            print("School_Port = "+ str(edge_school_port))
            print("School_MAC = "+ edge_school_mac)
            print("School_ContainerId = "+ edge_school_container_id)
            # mysql_connection.select_db('edge-regist')

            # try:
            #    mysql_connection.excute('Insert INTO School (School_Id, School_Ip, School_MAC, School_Port, School_ContainerId) VALUE ' + edge_school_id + ", " + edge_school_ip + ", " + edge_school_mac + ", " + edge_school_port + ", " + edge_school_container_id)
            return {"regist": "ok"}
        except:
            return {"regist": "fail"}

if __name__ == '__main__':
	app.run(debug = True)
	app.run(host = '0.0.0.0', port=5000)
