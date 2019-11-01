#! /usr/bin/python3
import os, sys
import time, datetime
import requests

# [Cloud Setup]
cloudServerProtocol = "http"
cloudServerIp = "127.0.0.1"
cloudServerPort = 80
cloudServerParmeter = "/" + sys.argv[1] + "/status"
metaData = {"school": sys.argv[1], "status":""}

# [Edge Setup]
edgeInitState = 0
edgePreState = 200
edgeNowState = 404
edgeStatusCodeArray = ["Run", "Fail"]
edgeStatusCode = ""
checkInterval = 1 # 秒數

# [Edge Init]
print("argv = "+sys.argv[1])
while edgeInitState != 1:
    try:
        if (requests.get("http://127.0.0.1/login").status_code == requests.codes.ok): edgeStatusCode = edgeStatusCodeArray[0]
        else: edgeStatusCodeArray[1]
    except:
        edgeStatusCodeArray[1]
    try:
        requests.post(cloudServerProtocol + "://" + cloudServerIp + cloudServerParmeter)
        print(str(datetime.datetime.now()) + " Edge Init Network to Cloud : OK !")
        edgeInitState = 1
    except:
        print(str(datetime.datetime.now()) + "Edge Init Network to Cloud : Error !")
    time.sleep(checkInterval)

# [Edge selfCheck]
while edgeInitState:
    edgeStatusCode = ""
    try:
        edgeNowState = requests.get("http://127.0.0.1/login").status_code
    except:
        edgeNowState = 404
    if (edgeNowState == 200 and edgePreState == 200): print("LibreNMS is Running")
    elif (edgeNowState == 404 and edgePreState == 200):
        os.system("service mysql restart")
        os.system("service apach2 restart")
        try:
            edgeNowState = requests.get("http://127.0.0.1/login").status_code
            print("LibreNMS is Running")
        except:
            edgeNowState = 404
            print("LibreNMS is Down")
            edgeStatusCode = edgeStatusCodeArray[1]
    elif (edgeNowState == 404 and edgePreState == 200):
        print("LibreNMS is Up")
        edgeStatusCode = edgeStatusCodeArray[0]
    else:
        print("LibreNMS is Fail !")
    if (edgeStatusCode != ""):
        try:
            requests.post(cloudServerProtocol + "://" + cloudServerIp + cloudServerParmeter)
            print("Response to Cloud  !")
        except:
            print("Network to Cloud Error !")
    edgePreState = edgeNowState
    time.sleep(checkInterval)