#! /usr/bin/python3

import os, sys
import subprocess
import math
import time

control_id = 0
error_id = 1

def delete_service():
    print("刪除服務模式")
    container_name = str(subprocess.Popen('docker ps -a -f "name=librenms" --format "{{.Names}}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8'))
    print(container_name)
    for x in range(0, len(container_name.split("\n"))-1):
        print("刪除服務 --> ", container_name.split("\n")[x])
        delete_container_command = "docker stop " + container_name.split("\n")[x]
        os.system(delete_container_command + " >/dev/null 2>&1")
        delete_container_command = "docker rm " + container_name.split("\n")[x]
        os.system(delete_container_command + " >/dev/null 2>&1")
    print("正在刪除監控系統資料")
    os.system("rm -r School_Monitor/ ")
    print("服務已解除安裝")

def create_docker_network(network_name):
    # network_config = 'docker network create --subnet 172.3.0.0/24 ' + network_name
    # print(network_config)
    # os.system(network_config)
    print("No Create Docker Network")

def create_librenms(school_serial_id, school_name, docker_mysql_name, docker_mysql_ip, db_name, db_user_name, db_user_pwd, librenms_network):
    print("建立監控系統總服務")
    print("生成系統認證金鑰碼")
    docker_librenms_config = "docker run --rm jarischaefer/docker-librenms generate_key"
    librenms_product_key = str(subprocess.Popen(docker_librenms_config, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
    # print(librenms_product_key)
    if (os.path.isdir("./School_Monitor") == 0): os.mkdir("./School_Monitor")
    if (os.path.isdir("./School_Monitor/librenms") == 0): os.mkdir("./School_Monitor/librenms")
    if (os.path.isdir("./School_Monitor/librenms/" + school_name) == 0): os.mkdir("./School_Monitor/librenms/" + school_name)
    if (os.path.isdir("./School_Monitor/librenms/" + school_name + "/logs") == 0): os.mkdir("./School_Monitor/librenms/" + school_name + "/logs")
    if (os.path.isdir("./School_Monitor/librenms/" + school_name + "/rrd") == 0): os.mkdir("./School_Monitor/librenms/" + school_name + "/rrd")
    librenms_volume = str(subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
    # print(librenms_volume)
    print("安裝系統基礎監控服務")
    docker_librenms_config = "docker run -d -h librenms -p " + str(30000 + int(school_serial_id)) + ":80 -e APP_KEY=" + librenms_product_key +  " -e DB_HOST='" + docker_mysql_ip + "' -e DB_NAME=" + db_name + " -e DB_USER=" + db_user_name + " -e DB_PASS=" + db_user_pwd + " -e BASE_URL=http://127.0.0.1" + " --link " + docker_mysql_name + ":db -v " + librenms_volume + "/School_Monitor/librenms/" + school_name + "logs:/opt/librenms/logs -v " + librenms_volume + "/School_Monitor/librenms/" + school_name + "/rrd:/opt/librenms/rrd --name " + school_name + " jarischaefer/docker-librenms"
    # print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    time.sleep(10)
    print("監控系統服務啟動測試")
    time.sleep(10)
    print("設定監控系統基礎資料")
    docker_librenms_config = "docker exec " + school_name + " setup_database"    
   # print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("創建最高權限使用者")
    docker_librenms_config = "docker exec " + school_name + " create_admin"
   # print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("重新啟動資料庫系統")
    # docker_librenms_config = "docker start " + docker_mysql_name
    # os.system(docker_librenms_config + " >/dev/null 2>&1")
    # time.sleep(30)
    print("Docker Container 環境更新")
    docker_librenms_config = "docker exec " + school_name + " sh -c " + '"apt-get update"'
   # print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("Docker Container 環境安裝")
    docker_librenms_config = "docker exec " + school_name + " sh -c " + '"apt-get install -y git python3 python3-pip"'
   # print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("下載雲端連線服務")
    docker_librenms_config = "docker exec " + school_name + " sh -c " + '"git clone https://github.com/j13tw/School_Monitor_System.git"'
   # print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("創建學校環境服務")
    docker_librenms_config = "docker exec " + school_name + " sh -c " + '"python3 /School_Monitor_System/Client/envoriment_docker.py"'
   # print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("複製服務設定檔")
    docker_librenms_config = "docker exec " + school_name + ' sh -c "' + "echo 'nohup python3 -u /School_Monitor_System/Client/selfCheck_docker.py " + school_name + " " + docker_mysql_ip + " > client.log 2>&1 &' > client.sh" + '"'
    print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("創建雲端環境服務")
    docker_librenms_config = "docker exec " + school_name + ' sh -c "sudo sh client.sh"'
    print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("自動添加設備服務-1")
    docker_librenms_config = "docker exec " + school_name + ' sh -c "python3 /opt/librenms/snmp-scan.py 10.0.0.196"'
    print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("自動添加設備服務-2")
    docker_librenms_config = "docker exec " + school_name + ' sh -c "python3 /opt/librenms/snmp-scan.py 10.0.0.197"'
    print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("自動添加設備服務-3")
    docker_librenms_config = "docker exec " + school_name + ' sh -c "python3 /opt/librenms/snmp-scan.py 10.0.0.199"'
    print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")
    print("自動添加設備服務-4")
    docker_librenms_config = "docker exec " + school_name + ' sh -c "python3 /opt/librenms/snmp-scan.py 10.0.0.254"'
    print(docker_librenms_config)
    os.system(docker_librenms_config + " >/dev/null 2>&1")

def create_mysql(school_serial_id, school_name, docker_mysql_name, db_root_pwd, db_name, db_user_name, db_user_pwd, librenms_network):
    print("建立監控系統資料庫")
    if (os.path.isdir("./School_Monitor") == 0): os.mkdir("./School_Monitor")
    if (os.path.isdir("./School_Monitor/mysql") == 0): os.mkdir("./School_Monitor/mysql")
    if (os.path.isdir("./School_Monitor/mysql/" + school_name) == 0): os.mkdir("./School_Monitor/mysql/" + school_name)
    os.chdir("./School_Monitor")
    mysql_volume = str(subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0]
    # print(mysql_volume)
    docker_mysql_config = 'docker run --name ' + docker_mysql_name + " -d -e MYSQL_ROOT_PASSWORD=" + db_root_pwd + " -e MYSQL_USER=" + db_user_name + " -e MYSQL_PASSWORD=" + db_user_pwd + " -e MYSQL_DATABASE=" + db_name + " -p 127.0.0.1:" + str(33060 + int(school_serial_id)) + ":3306 -v " + mysql_volume + '/School_Monitor/mysql/' + school_name + ':/var/lib/mysql mysql:5.6 --sql-mode=""'
    # print(docker_mysql_config)
    os.system(docker_mysql_config + " >/dev/null 2>&1")
    print("重新啟動資料庫系統")
    docker_librenms_config = "docker start " + docker_mysql_name
    os.system(docker_librenms_config)
    docker_mysql_config = 'docker exec -ti ' + docker_mysql_name + " service mysql start"
   # print(docker_mysql_config)
    os.system(docker_mysql_config + " >/dev/null 2>&1")
    docker_mysql_config = 'docker exec ' + docker_mysql_name + " sh -c " + '"hostname -I"'
    print(docker_mysql_config)
    docker_mysql_ip = str(subprocess.Popen(docker_mysql_config, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].decode('utf-8')).split("\n")[0].split("\r")[0].split(" ")[0]
    print("docker_mysql_ip", docker_mysql_ip, "-123")
    return docker_mysql_ip

def create_service(school_serial_id, school_name):
#    school_name = input("請輸入學校代碼：")
    librenms_docker_name = school_name + "-librenms"
    librenms_mysql_docker_name = school_name + "-librenms-mysql"
    librenms_mysql_root_pwd = school_name + "root"
    librenms_mysql_user_db = "lib" + school_name + "name"
    librenms_mysql_user_name = "lib" + school_name + "user"
    librenms_mysql_user_pwd = "lib" + school_name + "pass"
    librenms_network = school_name + "-net"
    print("librenms_docker_name ", librenms_docker_name)
    print("librenms_docker_mysql_name ", librenms_mysql_docker_name)
    print("librenms_mysql_root_pwd ", librenms_mysql_root_pwd)
    print("librenms_mysql_user_db ", librenms_mysql_user_db)
    print("librenms_mysql_user_name ", librenms_mysql_user_name)
    print("librenms_mysql_user_pwd ", librenms_mysql_user_pwd)
    print("資料庫服務名稱：" + librenms_mysql_docker_name)
    print("資料庫總管密碼：" + librenms_mysql_root_pwd)
    create_docker_network(librenms_network)
   # print("librenms_network" + librenms_network)
    librenms_mysql_ip = create_mysql(school_serial_id, school_name, librenms_mysql_docker_name, librenms_mysql_root_pwd, librenms_mysql_user_db, librenms_mysql_user_name, librenms_mysql_user_pwd, librenms_network)
   # print(librenms_mysql_ip)
    create_librenms(school_serial_id, school_name, librenms_mysql_docker_name, librenms_mysql_ip, librenms_mysql_user_db, librenms_mysql_user_name, librenms_mysql_user_pwd, librenms_network)
    print("監控系統安裝完成")
    print("請輸入 http://127.0.0.1/")
    print("帳號 : admin")
    print("密碼 : admin")
    print("感謝您的安裝與使用~")

#    user_name = input("請輸入使用者帳號：")
#    user_pwd = input("請輸入使用者密碼：")

# while(error_id == 1):
#     control_id = input("請輸入管理動作(1->新建服務/2->刪除服務): ")
#     try:
#         control_id = int(control_id)
#         error_id = 0
#     except:
#         error_id = 1
#     if (error_id == 0 and (control_id == 1 or control_id == 2)):
#         error_id = 0
#     else:
#         print("輸入錯誤 --> 請輸入 1 或 2")
#         error_id = 1

# if (int(control_id) == 1):
#     create_service()
# else:
#     delete_service()

create_service(str(sys.argv[1]), str(sys.argv[2]))