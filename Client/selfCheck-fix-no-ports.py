#! /usr/bin/python3
from ipgetter2 import ipgetter1 as ipgetter
from influxdb import InfluxDBClient
import os, sys
import time, datetime
import MySQLdb
import requests
import getmac
import json
import speedtest

# [School Setup]
school_id = str(sys.argv[1])
school_core_switch_ip = str(sys.argv[2])
school_mac = getmac.get_mac_address()
school_ip = ipgetter.myip()

# [Cloud Setup]
cloudServerProtocol = "http"
# cloudServerIp = "10.0.0.203"
cloudServerIp = str(sys.argv[3])
cloudServerPort = 5000
cloudState = 0 # 0 is connected / 1 is connect fail
edgeNodeRegistUrl = "/edgeNodeRegist"
edgeServiceCheckUrl = "/edgeNodeHealthCheck"
edgeDatabaseFlashUrl = "/edgeNodeSqlUpload"
edgeSpeedtestUploadUrl = "/edgeNodeSpeedtestUpload"

registData = {"school": school_id, "mac": school_mac, "ip": school_ip, "status": ""}
healthData = {"school": school_id, "mac": school_mac, "ip": school_ip, "status":""}
searchSqlData = {"school": school_id, "mac": school_mac, "ip": school_ip, "devices": [], "device_perf": [], "alert_log": [], "ports": []}
speedtestData = {"school": school_id, "mac": school_mac, "ip": school_ip, "speedtest": {"timestamp": "2020-01-01 00:00:00"}}

#print("argv = "+school_id)
#print(registData)
#print(healthData)

# [Mysql Setup]
mysql_host = "127.0.0.1"
mysql_port = 3306
mysql_user = "lib" + school_id + "user"
mysql_passwd = "lib" + school_id + "pass"
mysql_db = "lib" + school_id + "name"

# mysql_user = "librenms"
# mysql_passwd = "librenms"
# mysql_db = "librenms"

# [InfluxDB Setup]
influxdb_host = '127.0.0.1'
influxdb_port = 8086
influxdb_user = "lib" + school_id + "user"
influxdb_passwd = "lib" + school_id + "pass"
influxdb_db = "lib" + school_id + "name"

# influxdb_user = 'lib313302user'
# influxdb_passwd = 'lib313302pass'
# influxdb_db = 'lib313302name'

# [Edge Setup]
edgeInitState = 0
edgePreState = 200
edgeNowState = 404
edgeMysqlState = True
edgeStatusCodeArray = ["running", "stop", "fail"]
checkInterval = 60 # 鑑測輪詢秒數
pushSqlDelay = 5  # 拋送 sql 查詢資料延遲次數
pushSqlCount = checkInterval * pushSqlDelay  # 每次拋送 sql 查詢延時 (pushSqlCount*checkInterval=300s)

def influxdb_search_ports_tables():
    global mysql_conn
    influxdbStatus = 0
    for x in range(0, 3):
        try:
            influx_conn = InfluxDBClient(influxdb_host, 8086, influxdb_user, influxdb_passwd, influxdb_db)
            break
        except:
            os.system("sudo service influxdb start")
            time.sleep(10)
        if (x == 2): influxdbStatus = 1

    if (mysql_connect() == True and influxdbStatus == 0):
        mysql_connection = mysql_conn.cursor()
        # print("select b.hostname, a.ifName, b.device_id, a.ifSpeed/1000, a.ifOperStatus from (select * from ports where device_id in (select device_id from devices where hostname=\"" + school_core_switch_ip + "\")) as a natural join devices as b group by port_id;")
        mysql_connection.execute("select b.hostname, a.ifName, b.device_id, a.ifSpeed/1000, a.ifOperStatus from (select * from ports where device_id in (select device_id from devices where hostname=\"" + school_core_switch_ip + "\")) as a natural join devices as b group by port_id;")
        portList = mysql_connection.fetchall()
        portDataList = []

        if (len(portList) != 0):
            for x in portList:
                y = x[1].split(" ")
                if (len(y) > 1): z = y[0] + "\\\\ " + y[1]
                else: z = x[1]
                data = influx_conn.query('select ifName as port_name, ifInBits_rate/1000 as input, ifOutBits_rate/1000 as output, hostname from ports where hostname = \'' + x[0] + '\' and ifName = \'' + z + '\' order by time desc limit 1;')
                if (len(list(data.get_points())) > 0):
                    portData = list(data.get_points())[0]
                    portData["device_id"] = x[2]
                    if (x[3] == None): portData["port_speed"] = "NULL"
                    else: portData["port_speed"] = int(x[3])
                    if (x[4] == None): portData["port_status"] = "NULL"
                    else: portData["port_status"] = x[4]
                    portDataList.append(portData)
            return portDataList
        else:
          return portDataList
    else:
      return portDataList

def make_speedtest():
    if (str(datetime.datetime.now()).split(" ")[0] != str(speedtestData["speedtest"]['timestamp']).split(" ")[0]):
        try:
            spd = speedtest.Speedtest()
            spd.get_best_server()
            start_time = str(datetime.datetime.now())
            spd.download()
            spd.upload()
            end_time = str(datetime.datetime.now())
        except:
            return False
        
        speedtestData["speedtest"]['ping'] = "{:.3f}".format(float(spd.results.ping))
        speedtestData["speedtest"]['download'] = "{:.3f}".format(float(spd.results.download)/1024/1024)
        speedtestData["speedtest"]['upload'] = "{:.3f}".format(float(spd.results.upload)/1024/1024)
        speedtestData["speedtest"]['server_name'] = spd.results.server["name"]
        speedtestData["speedtest"]['server_sponsor'] = spd.results.server["sponsor"]
        speedtestData["speedtest"]['server_distance'] = "{:.5f}".format(float(spd.results.server["d"]))
        speedtestData["speedtest"]['timestamp'] = str(datetime.datetime.strptime(spd.results.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8))
        speedtestData["speedtest"]['start_time'] = start_time
        speedtestData["speedtest"]['end_time'] = end_time
        speedtestData["speedtest"]['submit'] = 0
        print(speedtestData)
        try:
            r = requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeSpeedtestUploadUrl, json=speedtestData)
            if (json.loads(r.text)["uploadSpeedtest"] == "ok"): 
                speedtestData["speedtest"]['submit'] = 1
                return True
            else: False  
        except:
            return False

    elif (str(datetime.datetime.now()).split(" ")[0] == speedtestData["speedtest"]['timestamp'] and speedtestData["speedtest"]["submit"] == 0):
        try:
            r = requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeSpeedtestUploadUrl, json=speedtestData)
            if (json.loads(r.text)["uploadSpeedtest"] == "ok"): 
                speedtestData["speedtest"]['submit'] = 1
                # spd_log_w = open("./speedtest.log", "w")
                # spd_log_w.write(str(speedtestData))
                # spd_log_w.close()
                return True
            else: False  
        except:
            return False
    else:
        return False
        
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
    global mysql_conn
    if mysql_connect() == True:
        mysql_connection = mysql_conn.cursor()
        mysql_connection.execute("show tables;")
        mysql_conn.close()
        for x in mysql_connection:
            if x[0] == tableName:
                return True
        else: 
            return False
    else:
        return False

# search edge Node ==> librenms devices data
def mysql_search_devices_tables():
    global mysql_conn
    devices_data = []
    deviceCount = 0
    mysql_connect()
    mysql_connection = mysql_conn.cursor()
    deviceCount = mysql_connection.execute("select device_id, hostname, sysName, ip, community, authlevel, authname, authpass, authalgo, \
        cryptopass, cryptoalgo, snmpver, port, transport, timeout, retries, snmp_disable, bgpLocalAs, sysObjectID, sysDescr, sysContact, \
        version, hardware, features, location_id, os, status, status_reason, disabled, uptime, agent_uptime, last_polled, \
        last_poll_attempted, last_polled_timetaken, last_discovered_timetaken, last_discovered, last_ping, last_ping_timetaken, purpose, \
        type, serial, icon, poller_group, override_sysLocation, notes, port_association_mode, max_depth from devices")
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
            "status_reason": z[27], \
            "disabled": z[28], \
            "uptime": z[29], \
            "agent_uptime": z[30], \
            "last_polled": str(z[31]), \
            "last_poll_attempted": str(z[32]), \
            "last_polled_timetaken": z[33], \
            "last_discovered_timetaken": z[34], \
            "last_discovered": str(z[35]), \
            "last_ping": str(z[36]), \
            "last_ping_timetaken": str(z[37]), \
            "purpose": z[38], \
            "type": z[39], \
            "serial": z[40], \
            "icon": z[41], \
            "poller_group": z[42], \
            "override_sysLocation": z[43], \
            "notes": z[44], \
            "port_association_mode": z[45], \
            "max_depth": z[46]})
    #print(devices_data)
    mysql_conn.close()
    if (len(devices_data) == deviceCount):
        return devices_data
    else:
        return []

# search edge Node ==> librenms device_perf data
def mysql_search_device_perf_tables():
    global mysql_conn
    deviceCount = 0
    devices_list = []
    device_perf_data = []
    mysql_connect()
    mysql_connection = mysql_conn.cursor()
    deviceCount = mysql_connection.execute("select * from devices")
    for x in mysql_connection:
        devices_list.append(x[0])
    for x in range(0, len(devices_list)):
        mysql_connection.execute("select * from device_perf where device_id = " + str(devices_list[x]) + " order by timestamp desc limit 1")
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
    #print(device_perf_data)
    mysql_conn.close()
    if (deviceCount == len(device_perf_data)): 
        return device_perf_data
    else:
        return []

# search edge Node ==> librenms alert_log data
def mysql_search_alert_log_tables():
    deviceCount = 0
    devices_list = []
    alert_log_data = []
    mysql_connect()
    mysql_connection = mysql_conn.cursor()
    deviceCount = mysql_connection.execute("select * from devices")
    for x in mysql_connection:
        devices_list.append(x[0])
    for x in range(0, len(devices_list)):
        mysql_connection.execute("select alert_log.id, alert_log.rule_id, alert_log.device_id, alert_log.state, alert_rules.name as details, alert_log.time_logged from alert_log, alert_rules where alert_log.rule_id = alert_rules.id and alert_log.device_id = " + str(devices_list[x]) + " order by time_logged desc limit 3;")
        for y in mysql_connection:
            alert_log_data.append({ \
                "id": y[0], \
                "rule_id": y[1], \
                "device_id": y[2], \
                "state": y[3], \
                "details": y[4], \
                "time_logged": str(y[5])})
    #print(alert_log_data)
    mysql_conn.close()
    return alert_log_data

# [Edge Init]
for x in range(0, 3):
    edgeStatusCode = ""
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd, \
            db=mysql_db)
        mysql_conn.close()
        mysql_check_table("devices")
        mysql_check_table("device_perf")
        mysql_check_table("alert_log")
        break
    except:
        print(str(datetime.datetime.now()) + " Connect MySQL Error !")
        edgeStatusCode = edgeStatusCodeArray[2]
        os.system("service mysql restart")
        time.sleep(10)

if (edgeStatusCode == ""):
    for x in range(0, 3):
        try:
            if (requests.get("http://127.0.0.1/login").status_code == requests.codes.ok): 
                if (edgeStatusCode == ""): edgeStatusCode = edgeStatusCodeArray[0]
                break
        except:
            if (edgeStatusCode == ""): edgeStatusCode = edgeStatusCodeArray[1]
            os.system("service apache2 start")
            time.sleep(10)
   
registData["status"] = edgeStatusCode

while edgeInitState != 1:
    try:
        print(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeNodeRegistUrl)
        print(registData)
        r = requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeNodeRegistUrl, json=registData)
        if (json.loads(r.text)["regist"] == "ok"):
            edgeInitState = 1
            print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : Regist OK !")
        else: 
            print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : Regist Fail ! (" + json.loads(r.text)["info"] + ")")
    except:
        print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : Error !")
    time.sleep(checkInterval)

# [Edge selfCheck]
while edgeInitState:
    make_speedtest()
    edgeStatusCode = ""
    try:
        edgeNowState = requests.get("http://127.0.0.1/login").status_code
    except:
        edgeNowState = 404
    if (edgeNowState == 200 and edgePreState == 200): print(str(datetime.datetime.now()) + " LibreNMS is Running")
    elif (edgeNowState == 404 and edgePreState == 200):
        print(str(datetime.datetime.now()) + " LibreNMS Service Fail, Retry Secure Service")
        os.system("service apache2 restart")
        try:
            edgeNowState = requests.get("http://127.0.0.1/login").status_code
            print(str(datetime.datetime.now()) + " LibreNMS is Running")
        except:
            edgeNowState = 404
            print(str(datetime.datetime.now()) + " LibreNMS is Down")
            edgeStatusCode = edgeStatusCodeArray[1]
    elif (edgeNowState == 200 and edgePreState == 404):
        print(str(datetime.datetime.now()) + " LibreNMS is Up")
        edgeStatusCode = edgeStatusCodeArray[0]
    else:
        print(str(datetime.datetime.now()) + " LibreNMS is Fail !")
        os.system("service apache2 restart")

    if (mysql_connect() == False): 
        print(str(datetime.datetime.now()) + " Mysql Service Fail, Retry Secure Service")
        os.system("service mysql restart")
        time.sleep(10)
        if (mysql_connect() == False and edgeMysqlState == True): 
            print(str(datetime.datetime.now()) + " Mysql is Fail !")
            edgeStatusCode = edgeStatusCodeArray[1]
        else:
            print(str(datetime.datetime.now()) + " Mysql is Down")
            os.system("service apache2 restart")
    else:
        if (edgeMysqlState == False): 
            edgeStatusCode = edgeStatusCodeArray[0]
            print(str(datetime.datetime.now()) + " Mysql is Up")
        else:
            print(str(datetime.datetime.now()) + " Mysql is Running")

    edgeMysqlState = mysql_connect()
    # HealthCheck Flash API     
    if (edgeStatusCode != ""):
        cloudState = 1
        while(cloudState):
            try:
                healthData["status"] = edgeStatusCode
                requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeServiceCheckUrl, json=healthData)
                print(str(datetime.datetime.now()) + " Health Status Refresh to Cloud ok !")
                cloudState = 0
            except:
                print(str(datetime.datetime.now()) + " Health Response to Cloud Error !")
            if (cloudState == 1): time.sleep(checkInterval)
    else:
        if (pushSqlCount != 0): pushSqlCount = pushSqlCount - checkInterval
    # Mysql Data Flash API
    if (pushSqlCount == 0 and edgeStatusCode == ""):
        try:
            searchSqlData["devices"] = mysql_search_devices_tables()
            searchSqlData["device_perf"] = mysql_search_device_perf_tables()
            searchSqlData["alert_log"] = mysql_search_alert_log_tables()
            searchSqlData["ports"] = influxdb_search_ports_tables()
            print(searchSqlData)
            try:
                requests.post(cloudServerProtocol + "://" + cloudServerIp + ":" + str(cloudServerPort) + edgeDatabaseFlashUrl, json=searchSqlData)
                print(str(datetime.datetime.now()) + " Upload Sql to Cloud ok !")
            except:
                print(str(datetime.datetime.now()) + " Upload Sql to Cloud fail !")
            pushSqlCount = pushSqlDelay * checkInterval
        except:
            os.system("service mysql restart")
            print(str(datetime.datetime.now()) + " Fetch Sql to Cloud fail !")

    edgePreState = edgeNowState
    time.sleep(checkInterval)
