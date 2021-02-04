import MySQLdb
import os
import xlrd
import datetime
import subprocess
from openpyxl import Workbook

#### DB ####
f = open('/etc/mysql/debian.cnf', 'r')
fr = f.read()
mysql_user = fr.split(" = ")[2].split("\n")[0]
mysql_passwd = fr.split(" = ")[3].split("\n")[0]

#define DB connection
db = MySQLdb.connect(host="localhost", user=mysql_user, passwd=mysql_passwd, charset="utf8")
cursor = db.cursor()
#exe
cursor.execute("SELECT concat(\'school_\', school_Id), school_Name, School_Location FROM information_schema.schemata, school_monitor_system.edge_list  where schema_name like \'school_______\' and schema_name = concat(\'school_\', school_Id);")
#store results
result = cursor.fetchall()

#close connection
db.close()

#### EXCEL ####
wb = Workbook()
ws = wb.active
ws.append([ '學校名稱', '位置', '學校代碼', 'speedtestid', 'ping', 'download', 'upload', 'server_name', 'server_sponsor', 'server_distance', 'time_logged', 'start_time', 'end_time'])

for x in result:
# print(x)
# print(x[0])
 code = str(x[0]).split("school_")[1].replace("f","F")
 print("學校名稱:"+x[1])
 print("學校位置:"+x[2])
 print("學校代碼:"+code)
 db = MySQLdb.connect(host="localhost",user="root",passwd="kiss5891",charset="utf8")
 cursor = db.cursor()
 cursor.execute("select * from school_" + code + ".speedtest order by time_logged desc limit 1;")
 speedresult = cursor.fetchall()
# print(speedresult)
 for y in speedresult:
   print("id:"+str(y[0]))
   print("ping:"+str(y[1]))
   print("download:"+str(y[2]))
   print("upload:"+str(y[3]))
   print("server_name:"+y[4])
   print("server_sponsor:"+y[5])
   print("server_distance:"+str(y[6]))
   print("time_loged:"+str(y[7]))
   print("start_time:"+str(y[8]))
   print("end_time:"+str(y[9]))
   ws.append([x[1],x[2],code,str(y[0]),str(y[1]),str(y[2]),str(y[3]),str(y[4]),str(y[5]),str(y[6]),str(y[7]),str(y[8]),str(y[9])])
 print("-----我是分隔線-----")

#### TIME ####
datetime_dt = datetime.datetime.today()
datetime = datetime_dt.strftime("%y-%m-%d") 

wb.save(datetime + '.xlsx')
