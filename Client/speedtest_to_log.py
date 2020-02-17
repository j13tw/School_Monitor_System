import json
import speedtest
import time
import datetime

while(True):
    f = open("speedtest.log", 'a')
    speedtestData = {}
    try:
        spd = speedtest.Speedtest()
        spd.get_best_server()
        start_time = str(datetime.datetime.now())
        spd.download()
        spd.upload()
        end_time = str(datetime.datetime.now())
    except:
        print("speedtest error !")
        exit()

    speedtestData['ping'] = "{:.3f}".format(float(spd.results.ping))
    speedtestData['download'] = "{:.3f}".format(float(spd.results.download)/1024/1024)
    speedtestData['upload'] = "{:.3f}".format(float(spd.results.upload)/1024/1024)
    speedtestData['server_name'] = spd.results.server["name"]
    speedtestData['server_sponsor'] = spd.results.server["sponsor"]
    speedtestData['server_distance'] = "{:.5f}".format(float(spd.results.server["d"]))
    speedtestData['timestamp'] = str(datetime.datetime.strptime(spd.results.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8))
    speedtestData['start_time'] = start_time
    speedtestData['end_time'] = end_time
    print(speedtestData)
    f.write(str(speedtestData) + "\n")
    f.close()
    time.sleep(10)
