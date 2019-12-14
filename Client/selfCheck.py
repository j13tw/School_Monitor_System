#! /usr/bin/python3
from ipgetter2 import ipgetter1 as ipgetter
import os, sys
import time, datetime
import MySQLdb
import requests
import getmac

# [Cloud Setup]
cloudServerProtocol = "http"
cloudServerIp = "10.0.0.194"
cloudServerPort = 5000
cloudState = 0 # 0 is connected / 1 is connect fail
edgeNodeRegistUrl = "/edgeNodeRegist"
edgeServiceCheckUrl = "/edgeNodeHealthCheck"
edgeDatabaseFlashUrl = "/edgeNodeSqlUpload"

registData = {"school": sys.argv[1], "mac": getmac.get_mac_address(), "ip": ipgetter.myip(), "status": ""}
healthData = {"school": sys.argv[1], "status":""}
searchSqlData = {"school": sys.argv[1], "devices": [], "device_perf": [], "alert_log": []}


print("argv = "+sys.argv[1])
print(registData)
print(healthData)

# [Mysql Setup]
mysql_user = "libeenms"
mysql_passwd = "librenms"
mysql_db = "librenms"
mysql_host = "127.0.0.1"
mysql_port = 3306

# [Edge Setup]
edgeInitState = 0
edgePreState = 200
edgeNowState = 404
edgeStatusCodeArray = ["running", "stop", "fail"]
checkInterval = 10 # 鑑測輪詢秒數
pushSqlDelay = 3  # 拋送 sql 查詢資料延遲次數
pushSqlCount = checkInterval * pushSqlDelay  # 每次拋送 sql 查詢延時 (pushSqlCount*checkInterval=300s)


def mysql_connect():
    global mysql_conn
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd, \
            db=mysql_db, \
            set_character_set = 'utf-8')
        return True
    except:
        return False

# mysql 檢查指定 db 中 table 是否存
def mysql_check_table(tableName):
    if mysql_connect == True:
        mysql_connection = mysql_conn.cursor()
        mysql_connection.execute("show tables;")
        for x in mysql_connection:
            if x[0] == tableName:
                return True
        else: 
            return False
    else:
        return False

# search edge Node ==> librenms devices data
def mysql_search_devices_tables():
    devices_data = []
    deviceCount = 0
    mysql_connection = mysql_conn.cursor()
    deviceCount = mysql_connection.execute("select * from devices")
    for x in mysql_connection:
        z = []
        for y in range(0, len(x)):
            if x[y] == None or x[y] == '[]': z.append("NULL")
            else: z.append(x[y])
        devices_data.append({ \
            "device_id": z[0], \
            "hostname": z[1], \
            "sysName": z[2], \
            "ip": z[3], \
            "community": z[4], \
            "authlevel": z[5], \
            "authname": z[6], \
            "authpass": z[7], \
            "authalgo": z[8], \
            "cryptopass": z[9], \
            "cryptoalgo": z[10], \
            "snmpver": z[11], \
            "port": z[12], \
            "transport": z[13], \
            "timeout": z[14], \
            "retries": z[15], \
            "snmp_disable": z[16], \
            "bgpLocalAs": z[17], \
            "sysObjectID": z[18], \
            "sysDescr": z[19], \
            "sysContact": z[20], \
            "version": z[21], \
            "hardware": z[22], \
            "features": z[23], \
            "location_id": z[24], \
            "os": z[25], \
            "status": z[26], \
            "ignores": z[28], \
            "disabled": z[29], \
            "uptime": z[30], \
            "agent_uptime": z[31], \
            "last_polled": str(z[32]), \
            "last_poll_attempted": str(z[33]), \
            "last_polled_timetaken": z[34], \
            "last_discovered_timetaken": z[35], \
            "last_discovered": str(z[36]), \
            "last_ping": str(z[37]), \
            "last_ping_timetaken": z[38], \
            "purpose": z[39], \
            "type": z[40], \
            "serial": z[41], \
            "icon": z[42], \
            "poller_group": z[43], \
            "override_sysLocation": z[44], \
            "notes": z[45], \
            "port_association_mode": z[46], \
            "max_depth": z[47]})
    print(devices_data)
    if (len(devices_data) == deviceCount):
        return devices_data
    else:
        return []

# search edge Node ==> librenms device_perf data
def mysql_search_device_perf_tables():
    deviceCount = 0
    devices_list = []
    device_perf_data = []
    mysql_connection = mysql_conn.cursor()
    deviceCount = mysql_connection.execute("select * from devices")
    for x in mysql_connection:
        devices_list.append(x[0])
    for x in range(0, len(devices_list)):
        mysql_connection.execute("select * from device_perf where device_id = " + str(devices_list[x]) + " group by timestamp desc limit 1")
        for y in mysql_connection:
            device_perf_data.append({ \
                "id": y[0], \
                "device_id": y[1], \
                "timestamp": str(y[2]), \
                "xmt": y[3], \
                "rcv": y[4], \
                "loss": y[5], \
                "min": y[6], \
                "max": y[7], \
                "avg": y[8], \
                "debug": y[9]})
    print(device_perf_data)
    if (deviceCount == len(device_perf_data)): 
        return device_perf_data
    else:
        return []

# search edge Node ==> librenms alert_log data
def mysql_search_alert_log_tables():
    deviceCount = 0
    devices_list = []
    alert_log_data = []
    mysql_connection = mysql_conn.cursor()
    deviceCount = mysql_connection.execute("select * from devices")
    for x in mysql_connection:
        devices_list.append(x[0])
    for x in range(0, len(devices_list)):
        mysql_connection.execute("select * from alert_log where device_id = " + str(devices_list[x]) + " group by time_logged desc limit 3")
        for y in mysql_connection:
            alert_log_data.append({ \
                "id": y[0], \
                "rule_id": y[1], \
                "id": y[2], \
                "state": y[3], \
                "details": y[4], \
                "time_logged": str(y[5])})
    print(alert_log_data)
    if (deviceCount == len(alert_log_data)): 
        return alert_log_data
    else:
        return []

# [Edge Init]
while edgeInitState != 1:
    edgeStatusCode = ""
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd, \
            db=mysql_db, \
            set_character_set = 'utf-8')
        mysql_check_table("devices")
        mysql_check_table("device_perf")
        mysql_check_table("alert_log")
    except:
        print(str(datetime.datetime.now()) + " Connect MySQL Error !")
        edgeStatusCode = edgeStatusCodeArray[2]
    if (edgeStatusCode == ""):
        try:
            if (requests.get("http://127.0.0.1/login").status_code == requests.codes.ok): edgeStatusCode = edgeStatusCodeArray[0]
        except:
            edgeStatusCode = edgeStatusCodeArray[1]
        if (edgeStatusCode == edgeStatusCodeArray[0]):
            registData["status"] = edgeStatusCode
            try:
                print(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeNodeRegistUrl)
                print(registData)
                requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeNodeRegistUrl, json=registData)
                print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : OK !")
                edgeInitState = 1
            except:
                print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : Error !")
    else:
        os.system("service mysql start")
    time.sleep(checkInterval)

# [Edge selfCheck]
while edgeInitState:
    edgeStatusCode = ""
    try:
        edgeNowState = requests.get("http://127.0.0.1/login").status_code
    except:
        edgeNowState = 404
    if (edgeNowState == 200 and edgePreState == 200): print(str(datetime.datetime.now()) + " LibreNMS is Running")
    elif (edgeNowState == 404 and edgePreState == 200):
        print(str(datetime.datetime.now()) + " Service Fail, Retry Secure Service")
        os.system("service mysql restart")
        os.system("service apach2 restart")
        try:
            edgeNowState = requests.get("http://127.0.0.1/login").status_code
            print(str(datetime.datetime.now()) + " LibreNMS is Running")
        except:
            edgeNowState = 404
            print(str(datetime.datetime.now()) + " LibreNMS is Down")
            edgeStatusCode = edgeStatusCodeArray[1]
    elif (edgeNowState == 404 and edgePreState == 200):
        print(str(datetime.datetime.now()) + " LibreNMS is Up")
        edgeStatusCode = edgeStatusCodeArray[0]
    else:
        print(str(datetime.datetime.now()) + " LibreNMS is Fail !")
    # HealthCheck Flash API     
    if (edgeStatusCode != ""):
        try:
            healthData["status"] = edgeStatusCode
            requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeServiceCheckUrl, json=healthData)
            print(str(datetime.datetime.now()) + " Health Response to Cloud ok !")
        except:
            print(str(datetime.datetime.now()) + " Health Response to Cloud Error !")
            cloudState = 0
    else:
        pushSqlCount = pushSqlCount - checkInterval
    # Mysql Data Flash API
    if (pushSqlCount == 0):
        searchSqlData["devices"] = mysql_search_devices_tables()
        searchSqlData["device_perf"] = mysql_search_device_perf_tables()
        searchSqlData["alert_log"] = mysql_search_alert_log_tables()
        print(searchSqlData)
        try:
            requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeDatabaseFlashUrl, json=searchSqlData)
            print(str(datetime.datetime.now()) + " Upload Sql to Cloud ok !")
        except:
            print(str(datetime.datetime.now()) + " Upload Sql to Cloud fail !")
        pushSqlCount = pushSqlDelay * checkInterval
            
    edgePreState = edgeNowState
    time.sleep(checkInterval)