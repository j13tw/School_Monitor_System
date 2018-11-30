#! /usr/bin/python3

import os, sys
import subprocess
import math
import time

control_id = 0
error_id = 1

def delete_service():
    os.system('docker ps -f "name=librenms" --format "{{.Names}}" > container.txt')
    container = open("container.txt", "r")
    container_name = container.read()
    print(container_name)
    for x in range(0, len(container_name.split("\n"))-1):
        print(x, container_name.split("\n")[x])
    print("delete")

def create_mysql(docker_mysql_name, db_root_pwd, db_name, db_user_name, db_user_pwd):
    print("Create mysql")
    if (os.path.isdir("./School_Monitor") == 0): os.mkdir("./School_Monitor")
    if (os.path.isdir("./School_Monitor/mysql") == 0): os.mkdir("./School_Monitor/mysql")
    os.chdir("./School_Monitor/mysql")
    mysql_volume = str(subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
#    print(mysql_volume)
    docker_mysql_config = 'docker run --name ' + docker_mysql_name + " -d -e MYSQL_ROOT_PASSWORD=" + db_root_pwd + " -e MYSQL_USER=" + db_user_name + " -e MYSQL_PASSWORD=" + db_user_pwd + " -e MYSQL_DATABASE=" + db_name + " -p 127.0.0.1:3307:3306 -v " + mysql_volume + ':/var/lib/mysql mysql:5.6 --sql-mode=""'
    print(docker_mysql_config)
    os.system(docker_mysql_config + "2&>1")
    docker_mysql_config = 'docker exec -ti ' + docker_mysql_name + " service mysql start"
    print(docker_mysql_config)
    os.system(docker_mysql_config + "2&>1")

def create_service():
    school_name = input("請輸入學校代碼：")
    librenms_docker_name = school_name + "-librenms"
    librenms_mysql_docker_name = school_name + "-librenms-mysql"
    librenms_mysql_root_pwd = school_name + "-root"
    librenms_mysql_user_db = school_name + "-db"
    librenms_mysql_user_name = school_name + "-user"
    librenms_mysql_user_pwd = school_name + "-pwd"
    print("librenms_docker_name ", librenms_docker_name)
    print("librenms_docker_mysql_name ", librenms_mysql_docker_name)
    print("librenms_mysql_root_pwd ", librenms_mysql_root_pwd)
    print("librenms_mysql_user_db ", librenms_mysql_user_db)
    print("librenms_mysql_user_name ", librenms_mysql_user_name)
    print("librenms_mysql_user_pwd ", librenms_mysql_user_pwd)
    print("資料庫服務名稱：", librenms_mysql_docker_name)
    print("資料庫總管密碼：", librenms_mysql_root_pwd)
    create_mysql(librenms_mysql_docker_name, librenms_mysql_root_pwd, librenms_mysql_user_db, librenms_mysql_user_name, librenms_mysql_user_pwd)
    user_name = input("請輸入使用者帳號：")
    user_pwd = input("請輸入使用者密碼：")


while(error_id == 1):
    control_id = input("請輸入管理動作(1->新建服務/2->刪除服務): ")
    try:
        control_id = int(control_id)
        error_id = 0
    except:
        error_id = 1
    if (error_id == 0 and (control_id == 1 or control_id == 2)):
        error_id = 0
    else:
        print("輸入錯誤 --> 請輸入 1 或 2")
        error_id = 1

if (int(control_id) == 1):
    create_service()
else:
    delete_service()


