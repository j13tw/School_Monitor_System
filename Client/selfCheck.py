#! /usr/bin/python3
from ipgetter2 import ipgetter1 as ipgetter
import os, sys
import time, datetime
import MySQLdb
import requests
import getmac

# [Cloud Setup]
cloudServerProtocol = "http"
cloudServerIp = "127.0.0.1"
cloudServerPort = 5000
cloudState = 0 # 0 is connected / 1 is connect fail
edgeNodeRegistUrl = "/edgeNodeRegist"
edgeServiceCheckUrl = "/edgeNodeHealthCheck"
edgeDatabaseFlashUrl = "/edgeNodeSqlUpload"

registData = {"school": sys.argv[1], "mac": getmac.get_mac_address(), "ip": ipgetter.myip(),"port": sys.argv[1]}
healthData = {"school": sys.argv[1], "status":""}
searchSqlData = {"school": sys.argv[1], "devices": [], "device_perf": "", "alert_log": []}


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
pushSqlDelay = 30  # 拋送 sql 查詢資料延遲次數
pushSqlCount = checkInterval * pushSqlDelay  # 每次拋送 sql 查詢延時 (pushSqlCount*checkInterval=300s)


def mysql_connect():
    global mysql_conn
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd, \
            db=mysql_db)
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
        devices_data.append({ \
            "device_id": x[0], \
            "hostname": x[1], \
            "sysName": x[2], \
            "ip": x[3], \
            "community": x[4], \
            "authlevel": x[5], \
            "authname": x[6], \
            "authpass": x[7], \
            "authalgo": x[8], \
            "cryptopass": x[9], \
            "cryptoalgo": x[10], \
            "snmpver": x[11], \
            "port": x[12], \
            "transport": x[13], \
            "timeout": x[14], \
            "retries": x[15], \
            "snmp_disable": x[16], \
            "bgpLocalAs": x[17], \
            "sysObjectID": x[18], \
            "sysDescr": x[19], \
            "sysContact": x[20], \
            "version": x[21], \
            "hardware": x[22], \
            "features": x[23], \
            "location_id": x[24], \
            "os": x[25], \
            "status": x[26], \
            "status_reason": x[27], \
            "ignores": x[28], \
            "disabled": x[29], \
            "uptime": x[30], \
            "agent_uptime": x[31], \
            "last_polled": str(x[32]), \
            "last_poll_attempted": x[33], \
            "last_polled_timetaken": x[34], \
            "last_discovered_timetaken": x[35], \
            "last_discovered": str(x[36]), \
            "last_ping": str(x[37]), \
            "last_ping_timetaken": x[38], \
            "purpose": x[39], \
            "type": x[40], \
            "serial": x[41], \
            "icon": x[42], \
            "poller_group": x[43], \
            "override_sysLocation": x[44], \
            "notes": x[45], \
            "port_association_mode": x[46], \
            "max_depth": x[47]})
    if (len(devices_data) == deviceCount)
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
        mysql_connection.execute("select * from device_perf where device_id = " + devices_list[x] + " group by timestamp limit 1")
        for y in mysql_connection:
            device_perf_data.append({ \
                "id": y[0], \
                "device_id": y[1], \
                "timestamp": y[2], \
                "xmt": y[3], \
                "rcv": y[4], \
                "loss": y[5], \
                "min": y[6], \
                "max": y[7], \
                "avg": y[8], \
                "debug": y[9]})
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
        mysql_connection.execute("select * from alert_log where device_id = " + devices_list[x] + " group by timestamp limit 3")
        for y in mysql_connection:
            device_alert_log.append({ \
                "id": y[0], \
                "rule_id": y[1], \
                "device_id": y[2], \
                "state": y[3], \
                "details": y[4], \
                "time_logged": y[5]})
    if (deviceCount == len(device_alert_log)): 
        return device_alert_log
    else:
        return []

# [Edge Init]
while edgeInitState != 1:
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd, \
            db=mysql_db)
        mysql_check_table(mysql_db, "devices")
        mysql_check_table(mysql_db, "device_perf")
        mysql_check_table(mysql_db, "alert_log")
    except:
        print(str(datetime.datetime.now()) + " Connect MySQL Error !")
        edgeStatusCode = edgeStatusCodeArray[2]
    if (edgeStatusCode == ""):
        try:
            if (requests.get("http://127.0.0.1/login").status_code == requests.codes.ok): edgeStatusCode = edgeStatusCodeArray[0]
        except:
            edgeStatusCode = edgeStatusCodeArray[1]
        if (edgeStatusCode == edgeStatusCodeArray[0])
            try:
                requests.post(cloudServerProtocol + "://" + cloudServerIp + cloudServerPort + edgeNodeRegistUrl, data=registData)
                print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : OK !")
                edgeInitState = 1
            except:
                print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : Error !")
    else:
        os.system("service mysql start")
    time.sleep(checkInterval)

# [Edge selfCheck]
while edgeInitState:
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
    if (edgeStatusCode != ""):
        try:
            healthData.status = edgeStatusCode
            # requests.post(cloudServerProtocol + "://" + cloudServerIp + cloudServerPort + edgeServiceCheckUrl, data=healthData)
            print(str(datetime.datetime.now()) + " Response to Cloud !")
        except:
            print(str(datetime.datetime.now()) + " Network to Cloud Error !")
            cloudState = 0
        if (cloudState == 0 and pushSqlCount = 0):
            searchSqlData["devices"] = mysql_search_devices_tables()
            searchSqlData["device_perf"] = mysql_search_device_perf_tables()
            searchSqlData["alert_log"] = mysql_search_alert_log_tables()
            print(searchSqlData)
            try:
                requests.post(cloudServerProtocol + "://" + cloudServerIp + cloudServerPort + edgeDatabaseFlashUrl, data=searchSqlData)
                print(str(datetime.datetime.now()) + " Upload Sql to Cloud ok !")
            except:
                print(str(datetime.datetime.now()) + " Upload Sql to Cloud fail !")
            pushSqlCount = pushSqlDelay * checkInterval
        else:
            pushSqlCount = pushSqlCount - 1

    edgePreState = edgeNowState
    time.sleep(checkInterval)