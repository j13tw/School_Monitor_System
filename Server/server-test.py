#! /usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask, request
import MySQLdb
import os, sys
import datetime
import json
import xlrd


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
edge_school_status = ""

# define mysql command
# cloud system
mysql_service_db = "school_monitor_system"
mysql_create_service_db = "CREATE DATABASE " + mysql_service_db + " CHARACTER SET utf8 COLLATE utf8_general_ci;" 
mysql_service_table = "edge_regist"
mysql_school_table = "edge_list"


mysql_create_regist_table = "CREATE TABLE " + mysql_service_table + " (\
    School_Id           varchar(10) NOT NULL, \
    School_Ip           varchar(15) NOT NULL, \
    School_MAC          varchar(60) NOT NULL, \
    School_Status       varchar(10) NOT NULL, \
    School_LastCheck    datetime NOT NULL, \
    PRIMARY KEY(School_Id));"

mysql_create_school_table = "CREATE TABLE " + mysql_school_table + " (\
    School_Serial_Id    int AUTO_INCREMENT, \
    School_Location     varchar(10) NOT NULL, \
    School_Name         varchar(25) NOT NULL, \
    School_Id           varchar(10) NOT NULL, \
    PRIMARY KEY(School_Serial_Id)) CHARACTER SET = utf8;"

# edge system
mysql_edge_db = ""
mysql_create_edge_db = "create database " + mysql_edge_db
mysql_edge_table = "librenms"

mysql_create_edge_devices_table = "CREATE TABLE devices (\
    device_id                   int(10) unsigned                             NOT NULL, \
    hostname                    varchar(128)                                 NOT NULL, \
    sysName                     varchar(128)                                 NULL, \
    ip                          varbinary(16)                                NULL, \
    community                   varchar(255)                                 NULL, \
    authlevel                   enum('noAuthNoPriv','authNoPriv','authPriv') NULL, \
    authname                    varchar(64)                                  NULL, \
    authpass                    varchar(64)                                  NULL, \
    authalgo                    enum('MD5','SHA')                            NULL, \
    cryptopass                  varchar(64)                                  NULL, \
    cryptoalgo                  enum('AES','DES','')                         NULL, \
    snmpver                     varchar(4)                                   NOT NULL   default 'v2c', \
    port                        smallint(5) unsigned                         NOT NULL   default '161', \
    transport                   varchar(16)                                  NOT NULL   default 'udp',\
    timeout                     int(11)                                      NULL, \
    retries                     int(11)                                      NULL, \
    snmp_disable                tinyint(1)                                   NOT NULL   default '0', \
    bgpLocalAs                  int(10) unsigned                             NULL, \
    sysObjectID                 varchar(128)                                 NULL, \
    sysDescr                    text                                         NULL, \
    sysContact                  text                                         NULL, \
    version                     text                                         NULL, \
    hardware                    text                                         NULL, \
    features                    text                                         NULL, \
    location_id                 int(10) unsigned                             NULL, \
    os                          varchar(32)                                  NULL, \
    status                      tinyint(1)                                   NOT NULL   default '0', \
    status_reason               varchar(50)                                  NOT NULL, \
    ignores                     tinyint(1)                                   NOT NULL   default '0', \
    disabled                    tinyint(1)                                   NOT NULL   default '0', \
    uptime                      bigint(20)                                   NULL, \
    agent_uptime                int(10) unsigned                             NOT NULL   default '0', \
    last_polled                 timestamp                                    NULL, \
    last_poll_attempted         timestamp                                    NULL, \
    last_polled_timetaken       double(5,2)                                  NULL, \
    last_discovered_timetaken   double(5,2)                                  NULL, \
    last_discovered             timestamp                                    NULL, \
    last_ping                   timestamp                                    NULL, \
    last_ping_timetaken         double(8,2)                                  NULL, \
    purpose                     text                                         NULL, \
    type                        varchar(20)                                  NOT NULL   default '', \
    serial                      text                                         NULL, \
    icon                        varchar(255)                                 NULL, \
    poller_group                int(11)                                      NOT NULL   default '0', \
    override_sysLocation        tinyint(1)                                   NULL       default '0', \
    notes                       text                                         NULL, \
    port_association_mode       int(11)                                      NOT NULL   default '1', \
    max_depth                   int(11)                                      NOT NULL   default '0', \
    PRIMARY KEY(device_id));"

mysql_create_edge_device_perf_table = "CREATE TABLE device_perf (\
    id          int(10) unsigned  NOT NULL, \
    device_id   int(10) unsigned  NOT NULL, \
    timestamp   datetime          NOT NULL, \
    xmt         int(11)           NOT NULL, \
    rcv         int(11)           NOT NULL, \
    loss        int(11)           NOT NULL, \
    min         double(8,2)       NOT NULL, \
    max         double(8,2)       NOT NULL, \
    avg         double(8,2)       NOT NULL, \
    debug       text              NULL,\
    PRIMARY KEY(id));"

mysql_create_edge_alert_log_table = "CREATE TABLE alert_log (\
    id          int(10) unsigned    NOT NULL, \
    rule_id     int(10) unsigned    NOT NULL, \
    device_id   int(10) unsigned    NOT NULL, \
    state       int(11)             NOT NULL, \
    details     longblob            NULL, \
    time_logged timestamp           NOT NULL, \
    PRIMARY KEY(id));"

mysql_create_edge_device_state_history_table = "CREATE TABLE device_state_history (\
    id          int(10) unsigned    NOT NULL, \
    device_id   int(10) unsigned    NOT NULL, \
    status       int(11)             NOT NULL, \
    time_logged timestamp           NOT NULL, \
    PRIMARY KEY(id));"

mysql_push_edge_data = ""

def mysql_reconnect():
    global mysql_conn
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd, \
            charset='utf8')
        return True
    except:
        return False

def mysql_connect():
    try:
        mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            passwd=mysql_passwd)
        mysql_conn.close()
        return True
    except:
        return False

# 建立 edge 所使用的 DB 的 Table
def mysql_creat_edge_table(dbName, tableName):
    if tableName == "devices": tableInfo = mysql_create_edge_devices_table
    elif tableName == "device_perf": tableInfo = mysql_create_edge_device_perf_table
    elif tableName == "alert_log": tableInfo = mysql_create_edge_alert_log_table
    elif tableName == "device_state_history": tableInfo = mysql_create_edge_device_state_history_table
    # print(tableName, tableInfo)
    try:
        mysql_conn.select_db(dbName)
        mysql_connection = mysql_conn.cursor()
        mysql_connection.execute(tableInfo)
        return True
    except:
        return False

# 建立 edge 所使用的 DB
def mysql_creat_edge_db(dbName):
    try:
        mysql_connection = mysql_conn.cursor()
        mysql_connection.execute("create database " + dbName)
        return True
    except:
        return False

# mysql 檢查指定 db 是否存
def mysql_check_db(dbName):
    try:
        mysql_conn.select_db(dbName)
        return True
    except:
        return False

# mysql 檢查指定 db 中 table 是否存
def mysql_check_table(dbName, tableName):
    if mysql_check_db(dbName) == True:
        mysql_conn.select_db(dbName)
        mysql_connection = mysql_conn.cursor()
        mysql_connection.execute("show tables;")
        for x in mysql_connection:
            if x[0] == tableName:
                return True
        else: 
            return False
    else:
        return False

# 切換資料庫
# conn.select_db('edge-regist')
# 新增資料庫
# mysql_school_dbName = "school_" + edge_school_id
# mysql_connection.execute("create database " + str(mysql_school_dbName))

app = Flask(__name__)

# mysql server db 準備
# os.system("service mysql start")
try:
    mysql_conn = MySQLdb.connect(host = mysql_host, \
        port=mysql_port, \
        user=mysql_user, \
        passwd=mysql_passwd, \
        charset='utf8')
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
    print("create school_regist table")
    mysql_connection.execute(mysql_create_regist_table)
    mysql_conn.commit()
if (not mysql_check_table(mysql_service_db, mysql_school_table)):
    print("create school_list table")
    try:
        school_list = xlrd.open_workbook("./315校名單.xlsx")
    except:
        print("lose school list file (315校名單.xlsx)")
        exit()
    school_sheet = school_list.sheets()[0]
    mysql_connection.execute(mysql_create_school_table)
    mysql_conn.commit()
    for x in range(1, school_sheet.nrows):
        mysql_connection.execute("set names utf8;")
        mysql_connection.execute("INSERT INTO " + mysql_school_table + "(School_Serial_Id, School_Location, School_Name, School_Id) \
            VALUES (" + str(int(school_sheet.row_values(x)[0])) + ", '" + str(school_sheet.row_values(x)[1]) + "', '" + str(school_sheet.row_values(x)[2]) + "', '" + str(school_sheet.row_values(x)[3]) + "')")
        mysql_conn.commit()
mysql_conn.close()

@app.route('/edgeNodeHealthCheck', methods=['POST'])
def edgeNodeHealthCheck():
    if request.method == 'POST':
        try:
            edgeData = json.loads(str(request.json).replace("'", '"'))
            edge_school_id = int(edgeData["school"])
            edge_school_status = str(edgeData["status"])
            edge_school_devices_table = str(edgeData["devices"])
            edge_school_device_perf_table = str(edgeData["devices_perf"])
            edge_school_alert_log_table = str(edgeData["alert_log"])
            print("healthCheck = ", edge_school_id, edge_school_status)  
            print("devices", edge_school_devices_table)
            print("device_perf", edge_school_device_perf_table)
            print("alert_log", edge_school_alert_log_table) 
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
            edgeData = json.loads(str(request.json).replace("'", '"'))
            edge_school_id = str(edgeData["school"])
            edge_school_ip = str(edgeData["ip"])
            edge_school_mac = str(edgeData["mac"])
            edge_school_status = str(edgeData["status"])
            print("School_Id = "+ edge_school_id)
            print("School_Ip = "+ edge_school_ip)
            print("School_Status = "+ str(edge_school_status))
            print("School_MAC = "+ edge_school_mac)
        except:
            return {"regist": "fail", "info": "post_Error"}
        
        if (mysql_connect() == True):
            mysql_reconnect()
            mysql_conn.select_db(mysql_service_db)
            mysql_connection = mysql_conn.cursor()
            mysql_check_school = mysql_connection.execute("Select school_Id from " + mysql_school_table + " where school_Id = '" + edge_school_id + "'")
            if (mysql_check_school == 0):
                print("school.id - Error")
                return {"regist": "fail", "info": "school_Error"}
            mysql_find_school = mysql_connection.execute("Select school_Id from " + mysql_service_table + " where school_Id = '" + edge_school_id + "'")
            if (mysql_find_school == 0):
                try:
                    mysql_connection.execute("Insert INTO " + mysql_service_table + " (School_Id, School_Ip, School_MAC, School_Status, School_LastCheck) VALUE ('" + edge_school_id + "', '" + edge_school_ip + "', '" + edge_school_mac + "', '" +  edge_school_status + "', '" + str(datetime.datetime.now()) + "')")
                    print("db_Insert : " + "school_" + edge_school_id)
                except: 
                    return {"regist": "fail", "info": "db_Insert_Error"}
            else:
                try:
                    mysql_connection.execute("UPDATE " + mysql_service_table + " SET School_Ip='" + edge_school_ip + "', School_MAC = '" + edge_school_mac + "', School_Status = '" + edge_school_status + "', School_LastCheck = '" + str(datetime.datetime.now()) + "' WHERE School_Id = '" + edge_school_id + "'")
                    print("db_Update : " + "school_" + edge_school_id)
                except: 
                    return {"regist": "fail", "info": "db_Update_Error"}
            mysql_conn.commit()
            if (mysql_check_db("school_" + edge_school_id) == False):
                if (mysql_creat_edge_db("school_" + edge_school_id) == False):
                    return {"regist": "fail", "info": "db_edgeDb_Error"}
            if (mysql_check_table("school_" + edge_school_id, "devices") == False):
                if (mysql_creat_edge_table("school_" + edge_school_id, "devices") == False):
                    return {"regist": "fail", "info": "db_edgeTable_devices_Error"}
            if (mysql_check_table("school_" + edge_school_id, "device_perf") == False):
                if (mysql_creat_edge_table("school_" + edge_school_id, "device_perf") == False):
                    return {"regist": "fail", "info": "db_edgeTable_device_perf_Error"}
            if (mysql_check_table("school_" + edge_school_id, "alert_log") == False):
                if (mysql_creat_edge_table("school_" + edge_school_id, "alert_log") == False):
                    return {"regist": "fail", "info": "db_edgeTable_alert_log_Error"}
            if (mysql_check_table("school_" + edge_school_id, "device_state_history") == False):
                if (mysql_creat_edge_table("school_" + edge_school_id, "device_state_history") == False):
                    return {"regist": "fail", "info": "db_edgeTable_device_state_history_Error"}
            mysql_conn.close()
            return {"regist": "ok"}
        else:
            return {"regist": "fail"}
        

@app.route('/edgeNodeSqlUpload', methods=['POST'])
def edgeNodeSqlUpload():
    if request.method == 'POST':
        print(str(datetime.datetime.now()) + "start")
        edgeData = json.loads(str(request.json).replace("'", '"'))
        edge_school_id = str(edgeData["school"])
        edge_school_devices = edgeData["devices"]
        edge_school_device_perf = edgeData["device_perf"]
        edge_school_alert_log = edgeData["alert_log"]
        # print("school_id", "\n", edge_school_id)
        # print("edge_school_devices", "\n", edge_school_devices)
        # print("edge_school_device_perf", "\n", edge_school_device_perf)
        # print("edge_school_alert_log", "\n", edge_school_alert_log)
        edge_device_list = []

        if (mysql_connect() == True):
            mysql_reconnect()
            mysql_conn.select_db("school_" + edge_school_id)
            mysql_connection = mysql_conn.cursor()
            mysql_connection.execute("select id from device_state_history group by id desc limit 1")
            if (len(list(mysql_connection)) == 0): device_state_count = 0
            else: 
                device_state_count = int(list(mysql_connection)[0][0])

            # edge devices table update
            print("Refresh devices tables")
            for x in range(0, len(edge_school_devices)):
                y = json.loads(str(edge_school_devices[x]).replace("'", '"'))
                if (y["device_id"] != "NULL"): device_id = str(y["device_id"])
                if (y["hostname"] != "NULL"): hostname = "'" + y["hostname"] + "'"
                if (y["sysName"] != "NULL"): sysName = "'" + y["sysName"] + "'"
                if (y["ip"] != "NULL"): ip = "'" + y["ip"] + "'"
                if (y["community"] != "NULL"): community = "'" + y["community"] + "'"
                if (y["authlevel"] != "NULL"): authlevel = str(y["authlevel"])
                if (y["authname"] != "NULL"): authname = "'" + y["authname"] + "'"
                if (y["authpass"] != "NULL"): authpass = "'" + y["authpass"] + "'"
                if (y["authalgo"] != "NULL"): authalgo = "'" + y["authalgo"] + "'"
                if (y["cryptopass"] != "NULL"): cryptopass = "'" + y["cryptopass"] + "'"
                if (y["cryptoalgo"] != "NULL"): cryptoalgo = "'" + y["cryptoalgo"] + "'"
                if (y["snmpver"] != "NULL"): snmpver = "'" + y["snmpver"] + "'"
                if (y["port"] != "NULL"): port = str(y["port"])
                if (y["transport"] != "NULL"): transport = "'" + y["transport"] + "'"
                if (y["timeout"] != "NULL"): timeout = str(y["timeout"])
                if (y["retries"] != "NULL"): retries = str(y["retries"])
                if (y["snmp_disable"] != "NULL"): snmp_disable = str(y["snmp_disable"])
                if (y["bgpLocalAs"] != "NULL"): bgpLocalAs = str(y["bgpLocalAs"])
                if (y["sysObjectID"] != "NULL"): sysObjectID = "'" + y["sysObjectID"] + "'"
                if (y["sysDescr"] != "NULL"): sysDescr = "'" + y["sysDescr"] + "'"
                if (y["sysContact"] != "NULL"): sysContact = "'" + y["sysContact"] + "'"
                if (y["version"] != "NULL"): version = "'" + y["version"] + "'"
                if (y["hardware"] != "NULL"): hardware = "'" + y["hardware"] + "'"
                if (y["features"] != "NULL"): features = "'" + y["features"] + "'"
                if (y["location_id"] != "NULL"): location_id = str(y["location_id"])
                if (y["os"] != "NULL"): os = "'" + y["os"] + "'"
                if (y["status"] != "NULL"): status = str(y["status"])
                if (y["status_reason"] != "NULL"): status_reason = "'" + str(y["status_reason"]) + "'" 
                if (y["ignores"] != "NULL"): ignores = str(y["ignores"])
                if (y["disabled"] != "NULL"): disabled = str(y["disabled"])
                if (y["uptime"] != "NULL"): uptime = str(y["uptime"])
                if (y["agent_uptime"] != "NULL"): agent_uptime = str(y["agent_uptime"])
                if (y["last_polled"] != "NULL"): last_polled = "'" + str(y["last_polled"]) + "'"
                if (y["last_poll_attempted"] != "NULL"): last_poll_attempted = "'" + str(y["last_poll_attempted"]) + "'"
                if (y["last_polled_timetaken"] != "NULL"): last_polled_timetaken = str(y["last_polled_timetaken"])
                if (y["last_discovered_timetaken"] != "NULL"): last_discovered_timetaken = str(y["last_discovered_timetaken"])
                if (y["last_discovered"] != "NULL"): last_discovered = "'" + str(y["last_discovered"]) + "'"
                if (y["last_ping"] != "NULL"): last_ping = "'" + str(y["last_ping"]) + "'"
                if (y["last_ping_timetaken"] != "NULL"): last_ping_timetaken = str(y["last_ping_timetaken"])
                if (y["purpose"] != "NULL"): purpose = "'" + y["purpose"] + "'"
                if (y["type"] != "NULL"): type = "'" + y["type"] + "'"
                if (y["serial"] != "NULL"): serial = "'" + y["serial"] + "'"
                if (y["icon"] != "NULL"): icon = "'" + y["icon"] + "'"
                if (y["poller_group"] != "NULL"): poller_group = str(y["poller_group"])
                if (y["override_sysLocation"] != "NULL"): override_sysLocation = str(y["override_sysLocation"])
                if (y["notes"] != "NULL"): notes = "'" + y["notes"] + "'"
                if (y["port_association_mode"] != "NULL"): port_association_mode = str(y["port_association_mode"])
                if (y["max_depth"] != "NULL"): max_depth = str(y["max_depth"])
                edge_device_list.append(device_id)
                if (mysql_connection.execute("select * from devices where device_id = " + device_id) == 1):
                    try:
                        mysql_connection.execute("UPDATE devices SET \
                            device_id = " + device_id + ", hostname = " + hostname + ", sysName = " + sysName + ", ip = " + ip + ", community = " + community + ", \
                            authlevel = " + authlevel + ", authname = " + authname + ", authpass = " + authpass + ", authalgo = " + authalgo + ", cryptopass = " + cryptopass + ", \
                            cryptoalgo = " + cryptoalgo + ", snmpver = " + snmpver + ", port = " + port + ", transport = " + transport + ", timeout = " + timeout + ", \
                            retries = " + retries + ", snmp_disable = " + snmp_disable + ", bgpLocalAs = " + bgpLocalAs + ", sysObjectID = " + sysObjectID + ", sysDescr = " + sysDescr + ", \
                            sysContact = " + sysContact + ", version = " + version + ", hardware = " + hardware + ", features = " + features + ", location_id = " + location_id + ", \
                            os = " + os + ", status = " + status + ", status_reason = " + status_reason + ", ignores = " + ignores + ", disabled = " + disabled + ", \
                            uptime = " + uptime + ", agent_uptime = " + agent_uptime + ", last_polled = " + last_polled + ", last_polled_timetaken = " + last_polled_timetaken + ", \
                            last_discovered_timetaken = " + last_discovered_timetaken + ", last_ping_timetaken = " + last_ping_timetaken + ", purpose = " + purpose + ", type = " + type + ", \
                            serial = " + serial + ", icon = " + icon + ", poller_group = " + poller_group + ", override_sysLocation = " + override_sysLocation + ", notes = " + notes + ", \
                            port_association_mode = " + port_association_mode + ", max_depth = " + max_depth + ", last_poll_attempted = " + last_poll_attempted + ", \
                            last_discovered = " + last_discovered + ", last_ping = " + last_ping + " WHERE device_id = " + device_id)
                        mysql_conn.commit()
                    except:
                        return {"uploadSql": "devices_table_update_Error"} 
                else:
                    try:
                        mysql_connection.execute("INSERT INTO devices (device_id, hostname, sysName, ip, community, authlevel, authname, authpass, authalgo, cryptopass, cryptoalgo, \
                            snmpver, port, transport, timeout, retries, snmp_disable, bgpLocalAs, sysObjectID, sysDescr, sysContact, version, hardware, features, location_id, os, \
                            status, status_reason, ignores, disabled, uptime, agent_uptime, last_polled_timetaken, last_discovered_timetaken, last_ping_timetaken, purpose, type, serial, icon, \
                            poller_group, override_sysLocation, notes, port_association_mode, max_depth, last_polled, last_poll_attempted, last_discovered, last_ping) \
                            VALUES (\
                            " + device_id + ", " + hostname + ", " + sysName + ", " + ip + ", " + community + ", " + authlevel + ", " + authname + ", " + authpass + ", \
                            " + authalgo + ", " + cryptopass + ", " + cryptoalgo + ", " + snmpver + ", " + port + ", " + transport + ", " + timeout + ", " + retries + ", \
                            " + snmp_disable + ", " + bgpLocalAs + ", " + sysObjectID + ", " + sysDescr + ", " + sysContact + ", " + version + ", " + hardware + ", \
                            " + features + ", " + location_id + ", " + os + ", " + status + ", " + status_reason + ", " + ignores + ", " + disabled + ", " + uptime + ", \
                            " + agent_uptime + ", " + last_polled_timetaken + ", " + last_discovered_timetaken + ", " + last_ping_timetaken + ", " + purpose + ", " + type + ", \
                            " + serial + ", " + icon + ", " + poller_group + ", " + override_sysLocation + ", " + notes + ", " + port_association_mode + ", " + max_depth + ", \
                            " + last_polled + ", " + last_poll_attempted + ", " + last_discovered + ", " + last_ping + ")")
                        mysql_conn.commit()
                    except:
                        return {"uploadSql": "devices_table_insert_Error"}
                print("recive school_" + edge_school_id + " devices " + device_id + "=" + hostname) 

                device_state_count = device_state_count + 1
                try:
                    mysql_connection.execute("INSERT INTO device_state_history (id, device_id, status ,time_logged) \
                    VALUES (\
                    " + str(device_state_count) + ", " + device_id + ", " + status + ", '" + str(datetime.datetime.now()) + "')")
                    mysql_conn.commit()
                except:
                    return {"uploadSql": "device_state_history_table_insert_Error"}
                print("add device " + device_id + " status: " + status + " time: " + str(datetime.datetime.now()))

            # edge device_perf table update
            print("Refresh device_perf tables")
            for x in range(0, len(edge_school_device_perf)):
                y = json.loads(str(edge_school_device_perf[x]).replace("'", '"'))
                if (y["id"] != "NULL"): id = str(y["id"])
                if (y["device_id"] != "NULL"): device_id = str(y["device_id"])
                if (y["timestamp"] != "NULL"): timestamp = "'" + str(y["timestamp"]) + "'"
                if (y["xmt"] != "NULL"): xmt = str(y["xmt"])
                if (y["rcv"] != "NULL"): rcv = str(y["rcv"])
                if (y["loss"] != "NULL"): loss = str(y["loss"])
                if (y["min"] != "NULL"): min = str(y["min"]) 
                if (y["max"] != "NULL"): max = str(y["max"])
                if (y["avg"] != "NULL"): avg = str(y["avg"] ) 
                if (y["debug"] != "NULL"): debug = "'" + str(y["debug"]) + "'"
                if (mysql_connection.execute("select * from device_perf where id = " + id) == 0):
                    try:
                        mysql_connection.execute("INSERT INTO device_perf (id, device_id, timestamp, xmt, rcv, loss, min, max, avg, debug) \
                            VALUE \
                            (" + id + ", " + device_id + ", " + timestamp + ", " + xmt + ", " + rcv + ", " + loss + ", " + min + ", " + max + ", " + avg + ", " + debug + ")")
                        print("device_perf insert new data !")
                        mysql_conn.commit()
                    except:
                        return {"uploadSql": "device_perf_table_insert_Error"}
                print("recive school_" + edge_school_id + " device_perf " + y["device_id"] + "=> device_perf_id = " + y["id"]) 

            # edge alert_log table update
            print("Refresh alert_log tables")
            for x in range(0, len(edge_school_alert_log)):
                y = json.loads(str(edge_school_alert_log[x]).replace("'", '"'))
                if (y["id"] != "NULL"): id = str(y["id"])
                if (y["rule_id"] != "NULL"): rule_id = str(y["rule_id"])
                if (y["device_id"] != "NULL"): device_id = str(y["device_id"])
                if (y["state"] != "NULL"): state = str(y["state"])
                if (y["details"] != "NULL"): details = "'" + str(y["details"]) + "'"
                if (y["time_logged"] != "NULL"): time_logged = "'" + str(y["time_logged"]) + "'"
                if (mysql_connection.execute("select * from alert_log where id = " + y["id"]) == 0):
                    try:
                        mysql_connection.execute("INSERT INTO alert_log (id, rule_id, device_id, state, details, time_logged) \
                            VALUE \
                            (" + id + ", " + rule_id + ", " + device_id + ", " + state + ", " + details + ", " + time_logged + ")")
                        print("alert_log insert new data !")
                        mysql_conn.commit() 
                    except:
                        return {"uploadSql": "device_perf_table_insert_Error"}
                print("recive school_" + edge_school_id + " alert_log " + device_id + "=> alert_log_id = " + id) 
            
            # print(edge_device_list)
            edge_device_list_set = set(edge_device_list)
            edge_device_list = []
            mysql_connection.execute("select device_id from devices")
            for x in mysql_connection:
                edge_device_list.append(str(x[0]))
            # print(edge_device_list)
            cloud_device_list_set = set(edge_device_list)
            device_difference_list = cloud_device_list_set.difference(edge_device_list_set)
            # print(device_difference_list)
            for x in device_difference_list:
            #    print(x)
                mysql_connection.execute("DELETE from devices where device_id = " + str(x))
                mysql_conn.commit()
                mysql_connection.execute("DELETE from device_perf where device_id = " + str(x))
                mysql_conn.commit()
                mysql_connection.execute("DELETE from alert_log where device_id = " + str(x))
                mysql_conn.commit()
                mysql_connection.execute("DELETE from device_state_history where device_id = " + str(x))
                mysql_conn.commit()
            print(str(datetime.datetime.now()) + "over")
            mysql_conn.close()
            return {"uploadSql": "ok"}
        else:
            print(str(datetime.datetime.now()) + "Server Mysql Fail")
            return {"uploadSql": "fail"}

if __name__ == '__main__':
#	app.run(debug = True)
	app.run(host = '10.0.0.194', port=5000)
