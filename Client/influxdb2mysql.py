import MySQLdb
from influxdb import InfluxDBClient
import json

mysql_host = '10.0.0.186'
mysql_port = 3306
mysql_user = 'lib313302user'
mysql_passwd = 'lib313302pass'
mysql_db = 'lib313302name'

influxdb_host = '10.0.0.186'
influxdb_port = 8086
influxdb_user = 'lib313302user'
influxdb_passwd = 'lib313302pass'
influxdb_db = 'lib313302name'


mysql_conn = MySQLdb.connect(host = mysql_host, \
            port=mysql_port, \
            user=mysql_user, \
            db=mysql_db,\
            passwd=mysql_passwd)

influx_conn = InfluxDBClient(influxdb_host, 8086, influxdb_user, influxdb_passwd, influxdb_db)

   mysql_connection = mysql_conn.cursor()
    influx_conn = InfluxDBClient(influxdb_host, 8086, influxdb_user, influxdb_passwd, influxdb_db)

    mysql_connection = mysql_conn.cursor()
    mysql_connection.execute("select b.hostname, a.ifName, b.device_id, a.ifSpeed/1000, a.ifOperStatus from ports as a natural join devices as b group by port_id;")
    portList = mysql_connection.fetchall()
    portDataList = []

    for x in portList:
        data = influx_conn.query('select ifName as port_name, ifInBits_rate/1000 as input, ifOutBits_rate/1000 as output, hostname from ports where hostname = \'' + x[0] + '\' and ifName = \'' + x[1] + '\' order by time desc limit 1;')
        portData = list(data.get_points())[0]
        portData["device_id"] = x[2]
        if (x[3] == None): portData["port_speed"] = "NULL"
        else: portData["port_speed"] = int(x[3])
        portData["port_status"] = x[4]
        portDataList.append(portData)

print(json.dumps(portDataList))