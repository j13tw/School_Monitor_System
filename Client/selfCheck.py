#! /usr/bin/python3
from ipgetter2 import ipgetter1 as ipgetter
import os, sys
import time, datetime
import requests
import getmac

# [Cloud Setup]
cloudServerProtocol = "http"
cloudServerIp = "127.0.0.1"
cloudServerPort = 5000
edgeNodeRegistUrl = "/edgeNodeRegist"
edgeServiceCheckUrl = "/" + sys.argv[1] + "/status"
edgeDatabaseFlashUrl = "/" + sys.argv[1] + "/dbFlash"

registData = {"school": sys.argv[1], "mac": getmac.get_mac_address(), "ip": ipgetter.myip(),"port": sys.argv[1]}
healthData = {"school": sys.argv[1], "status":""}

print(registData)
print(healthData)

# [Edge Setup]
edgeInitState = 0
edgePreState = 200
edgeNowState = 404
edgeStatusCodeArray = ["running", "stop"]
edgeStatusCode = ""
checkInterval = 10 # 鑑測輪詢秒數

# [Edge Init]
print("argv = "+sys.argv[1])

while edgeInitState != 1:
    try:
        if (requests.get("http://127.0.0.1/login").status_code == requests.codes.ok): edgeStatusCode = edgeStatusCodeArray[0]
        else: edgeStatusCodeArray[1]
    except:
        edgeStatusCodeArray[1]
    try:
        #r = requests.post(cloudServerProtocol + "://" + cloudServerIp + cloudServerPort + edgeNodeRegistUrl, data=registData)
        print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : OK !")
        edgeInitState = 1
    except:
        print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : Error !")
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
    if (edgeStatusCode != ""):
        try:
            healthData.status = edgeStatusCode
            #requests.post(cloudServerProtocol + "://" + cloudServerIp + cloudServerPort + edgeServiceCheckUrl, data=healthData)
            print(str(datetime.datetime.now()) + " Response to Cloud  !")
        except:
            print(str(datetime.datetime.now()) + " Network to Cloud Error !")
    edgePreState = edgeNowState
    time.sleep(checkInterval)
