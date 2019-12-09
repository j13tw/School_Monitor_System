#! /usr/bin/python3

from flask import Flask, request
import MySQLdb
import os, sys
import docker
import datetime
import json


# define Mysql status
mysql_conn = ""
mysql_host = "127.0.0.1"
mysql_port = 3306
mysql_db = ""
mysql_user = "root"
mysql_passwd = "root"
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
# cloud system
mysql_service_db = "school_monitor_system"
mysql_create_service_db = "create database " + mysql_service_db
mysql_service_table = "edge_regist"

mysql_create_regist_table = "CREATE TABLE " + mysql_service_table + " (\
    School_Id           int AUTO_INCREMENT, \
    School_Ip           varchar(17) NOT NULL, \
    School_MAC          varchar(17) NOT NULL, \
    School_Port         int NOT NULL, \
    School_ContainerId  varchar(64) NOT NULL, \
    School_LastCheck    datetime NOT NULL, \
    PRIMARY KEY(School_Id));')"

# edge system
mysql_edge_db = ""
mysql_create_edge_db = "create database " + mysql_edge_db
mysql_edge_table = "librenms"

mysql_create_status_table = "CREATE TABLE " + mysql_edge_table + " (\
    School_Id           int AUTO_INCREMENT, \
    School_Ip           varchar(17) NOT NULL, \
    School_MAC          varchar(17) NOT NULL, \
    School_Port         int NOT NULL, \
    School_ContainerId  varchar(64) NOT NULL, \
    School_LastCheck    datatime NOT NULL, \
    PRIMARY KEY(school_Id));')"

mysql_push_edge_data = ""

def mysql_connect():
    global mysql_conn
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd)
        return True
    except:
        return False

def mysql_creat_edge_db(edge_school_id):
    mysql_connect()
    dbName = "school_" + str(edge_school_id)
    try:
        mysql_connection = mysql_conn.cursor()
        print("1")
        mysql_connection.execute("create database " + dbName)
        print("2")
        mysql_conn.select_db(dbName)
        print("3")
        mysql_connection = mysql_conn.cursor()
        print("4")
        mysql_connection.execute(mysql_create_status_table)
        print("5")
        mysql_conn.commit()
        return True
    except:
        return False

# mysql 檢查指定 db 是否存
def mysql_check_db(dbName):
    mysql_connect()
    try:
        mysql_conn.select_db(dbName)
        return True
    except:
        return False

# mysql 檢查指定 db 中 table 是否存
def mysql_check_table(dbName, tableName):
    global mysql_conn
    if mysql_check_db(dbName) == True:
        mysql_connection = mysql_conn.cursor()
        mysql_connection.execute("show tables;")
        for x in mysql_connection:
            if x[0] == tableName:
                return True
        else: 
            return False
    else:
        return False

# 上傳檔案檢查
def is_allowed_file(file):
    if '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
    else:
        return False
    mime_type = magic.from_buffer(file.stream.read(), mime=True)
    if (
        mime_type in ALLOWED_MIME_TYPES and
        ext in ALLOWED_EXTENSIONS
    ):
        return True    
    return False 

# 切換資料庫
# conn.select_db('edge-regist')
# 新增資料庫
# mysql_school_dbName = "school_" + str(edge_school_id)
# mysql_connection.execute("create database " + str(mysql_school_dbName))

# docker container 啟動
docker_client = docker.from_env()
# docker_create = docker_client.containers.run(image='grafana/grafana', name=1234, ports={'3000/tcp': 1234}, detach=True).id
# docker_delete = client.containers.get(edge_school_container_id).remove(force=True)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024  # 128MB

# mysql server db 準備
os.system("service mysql start")
try:
    mysql_conn = MySQLdb.connect(host = mysql_host, \
        port=mysql_port, \
        user=mysql_user, \
        passwd=mysql_passwd)
except:
    print("Connect MySQL Error !")
    exit()
mysql_connection = mysql_conn.cursor()
if (not mysql_check_db(mysql_service_db)):
    print("create regist database")
    mysql_connection.execute(mysql_create_service_db)
    mysql_conn.commit()
mysql_conn.select_db(mysql_service_db)
mysql_connection = mysql_conn.cursor()
if (not mysql_check_table(mysql_service_db, mysql_service_table)):
    print("create regist table")
    mysql_connection.execute(mysql_create_regist_table)
    mysql_conn.commit()

@app.route('/listContainer', methods=['GET'])
def listContainer():
    x = 0
    container_list = [0]*len(docker_client.containers.list())
    for y in docker_client.containers.list():
        print(y.id, y.name, y.status, y.image.tags[0])
        container_list[x] = {"id": y.short_id, "name": y.name, "status": y.status, "image": y.image.tags[0]}
        x += 1
    # print(container_list)
    return str(container_list)

@app.route('/edgeNodeHealthCheck', methods=['POST'])
def edgeNodeHealthCheck():
    if request.method == 'POST':
        try:
            edgedata = json.loads(str(request.json).replace("'", '"'))
            edge_school_id = int(edgedata["school"])
            edge_school_ip = str(edgedata["ip"])
            edge_school_mac = str(edgedata["mac"])
            edge_school_status = str(edgedata["status"])
            print("healthCheck = ", edge_school_id, edge_school_ip, edge_school_mac, edge_school_status)   
        except:
            return {"check": "fail"}
        if (edge_school_status == "running"):
            print("running")
        else:
            print("stop")
        return {"check": "ok"}


@app.route('/edgeNodeRegist', methods=['POST'])
def edgeNodeRegist():
    if request.method == 'POST':
        try:
            edgedata = json.loads(str(request.json).replace("'", '"'))
            edge_school_id = int(edgedata["school"])
            edge_school_ip = str(edgedata["ip"])
            edge_school_mac = str(edgedata["mac"])
            edge_school_port = 30000 + int(edgedata["school"])
            print("School_Id = "+ str(edge_school_id))
            print("School_Ip = "+ edge_school_ip)
            print("School_Port = "+ str(edge_school_port))
            print("School_MAC = "+ edge_school_mac)
        except:
            return {"regist": "fail", "info": "post_Error"}
        try:
            edge_school_container_id = docker_client.containers.run(image='grafana/grafana', name=str(edge_school_id), ports={'3000/tcp': edge_school_port}, detach=True).short_id    
        except:
            edge_school_container_id = docker_client.containers.get(str(dge_school_id)).short_id
        print("School_ContainerId = "+ edge_school_container_id)
        if mysql_connect() == True:
            mysql_conn.select_db(mysql_service_db)
            mysql_connection = mysql_conn.cursor()
            mysql_find_school = mysql_connection.execute("Select school_Id from " + mysql_service_table + " where school_Id = " + str(edge_school_id))
            if (mysql_find_school == 0):
                try:
                    mysql_connection.execute("Insert INTO " + mysql_service_table + " (School_Id, School_Ip, School_MAC, School_Port, School_ContainerId, School_LastCheck) VALUE (" + str(edge_school_id) + ", '" + edge_school_ip + "', '" + edge_school_mac + "', " + str(edge_school_port) + ", '" + edge_school_container_id + "', '" + str(datetime.datetime.now()) + "')")
                    print("db_Insert :" + str(School_Id))
                except: 
                    return {"regist": "fail", "info": "db_Insert_Error"}
            else:
                try:
                    mysql_connection.execute("UPDATE " + mysql_service_table + " SET School_Ip='" + edge_school_ip + "', School_MAC = '" + edge_school_mac + "', School_Port = " + str(edge_school_port) + ", School_LastCheck = '" + str(datetime.datetime.now()) + "' WHERE School_Id = " + str(edge_school_id))
                    print("db_Update :" + str(School_Id))
                except: 
                    return {"regist": "fail", "info": "db_Update_Error"}
            mysql_conn.commit()
            if (mysql_check_db("school_" + str(edge_school_id)) == False):
                if (mysql_creat_edge_db("school_" + str(edge_school_id)) == False):
                    return {"regist": "fail", "info": "db_Use_Error"}
            return {"regist": "ok"}
        else:
            return {"regist": "fail", "info": "db_Connect_Error"}
        

@app.route('/edgeNodeSqlUpload', methods=['POST'])
def edgeNodeSqlUpload():
    if request.method == 'POST':
        file = request.files['file']
    if file and is_allowed_file(file):
        filename = secure_filename(file.filename)
        file.save(os.path.join('/tmp', filename))
        return {"upload": "ok"}
    return {"upload": "fail"}

if __name__ == '__main__':
	app.run(debug = True)
	app.run(host = '0.0.0.0', port=5000)
