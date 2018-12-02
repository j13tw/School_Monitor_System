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

def create_librenms(docker_librenms_name, docker_mysql_name, docker_mysql_ip, db_name, db_user_name, db_user_pwd):
    print("建立監控系統總服務")
    print("生成系統認證金鑰")
    docker_librenms_config = "docker run --rm jarischaefer/docker-librenms generate_key"
    librenms_product_key = str(subprocess.Popen(docker_librenms_config, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
#    print(librenms_product_key)
    if (os.path.isdir("./librenms") == 0): os.mkdir("./librenms")
    if (os.path.isdir("./librenms/logs") == 0): os.mkdir("./librenms/logs")
    if (os.path.isdir("./librenms/rrd") == 0): os.mkdir("./librenms/rrd")
    librenms_volume = str(subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
#    print(librenms_volume)
    print("安裝系統基礎監控服務")
    docker_librenms_config = "docker run -d -h " + docker_librenms_name + " -p 80:80 -e APP_KEY=" + librenms_product_key +  " -e DB_HOST='" + docker_mysql_ip + "' -e DB_NAME=" + db_name + " -e DB_USER=" + db_user_name + " -e DB_PASS=" + db_user_pwd + " -e BASE_URL=http://127.0.0.1" + " --link " + docker_mysql_name + ":db -v " + librenms_volume + "/librenms/logs:/opt/librenms/logs -v " + librenms_volume + "/librenms/rrd:/opt/librenms/rrd --name " + docker_librenms_name + " jarischaefer/docker-librenms"
#    print(docker_librenms_config)
    os.system(docker_librenms_config + "2&>1")
    time.sleep(40)
    print("設定監控系統基礎資料")
    docker_librenms_config = "docker exec " + docker_librenms_name + " setup_database"
#    print(docker_librenms_config)
    os.system(docker_librenms_config + "2&>1")
    print("創建最高權限使用者")
    docker_librenms_config = "docker exec " + docker_librenms_name + " create_admin"
#    print(docker_librenms_config)
    os.system(docker_librenms_config + "2&>1")

def create_mysql(docker_mysql_name, db_root_pwd, db_name, db_user_name, db_user_pwd):
    print("建立監控系統資料庫")
    if (os.path.isdir("./School_Monitor") == 0): os.mkdir("./School_Monitor")
    if (os.path.isdir("./School_Monitor/mysql") == 0): os.mkdir("./School_Monitor/mysql")
    os.chdir("./School_Monitor")
    mysql_volume = str(subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
#    print(mysql_volume)
    docker_mysql_config = 'docker run --name ' + docker_mysql_name + " -d -e MYSQL_ROOT_PASSWORD=" + db_root_pwd + " -e MYSQL_USER=" + db_user_name + " -e MYSQL_PASSWORD=" + db_user_pwd + " -e MYSQL_DATABASE=" + db_name + " -p 127.0.0.1:3306:3306 -v " + mysql_volume + '/mysql:/var/lib/mysql mysql:5.6 --sql-mode=""'
#    print(docker_mysql_config)
    os.system(docker_mysql_config + "2&>1")
    docker_mysql_config = 'docker exec -ti ' + docker_mysql_name + " service mysql start"
#    print(docker_mysql_config)
    os.system(docker_mysql_config + "2&>1")
    docker_mysql_config = 'docker exec -ti ' + docker_mysql_name + " sh -c " + '"hostname -I"'
#    print(docker_mysql_config)
    docker_mysql_ip = str(subprocess.Popen(docker_mysql_config, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
#    print("docker_mysql_ip", docker_mysql_ip)
    return docker_mysql_ip

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
    librenms_mysql_ip = create_mysql(librenms_mysql_docker_name, librenms_mysql_root_pwd, librenms_mysql_user_db, librenms_mysql_user_name, librenms_mysql_user_pwd)
    print(librenms_mysql_ip)
    create_librenms(librenms_docker_name, librenms_mysql_docker_name, librenms_mysql_ip, librenms_mysql_user_db, librenms_mysql_user_name, librenms_mysql_user_pwd)

#    user_name = input("請輸入使用者帳號：")
#    user_pwd = input("請輸入使用者密碼：")


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


