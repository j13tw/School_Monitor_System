import MySQLdb
import os
import xlrd
import subprocess

f = open('/etc/mysql/debian.cnf', 'r')
fr = f.read()
mysql_user = fr.split(" = ")[2].split("\n")[0]
mysql_passwd = fr.split(" = ")[3].split("\n")[0]

#define DB connection
db = MySQLdb.connect(host="localhost",user="root",passwd="kiss5891",charset="utf8")
cursor = db.cursor()

#exe
cursor.execute("SELECT schema_name from INFORMATION_SCHEMA.SCHEMATA WHERE schema_name NOT IN('information_schema', 'mysql', 'performance_schema', 'sys', 'test', 'school_monitor_system', 'vp' , 'vp_cmd_test', 'vp_school_1234', 'factory', 'lib800003name')")
#store results
result = cursor.fetchall()

#讀excel
school_list = xlrd.open_workbook("315校名單.xlsx")
school_sheet = school_list.sheets()[0]

#close connection
db.close()

#get datetime
updateInfo = subprocess.Popen(["date" , "+%m"],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
month, stderr = updateInfo.communicate()

updateInfo = subprocess.Popen(["date" , "+%Y"],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
year, stderr = updateInfo.communicate()

month=str(month).replace("b",'').replace("'",'').replace("n",'').replace("\\",'')
year=str(year).replace("b",'').replace("'",'').replace("n",'').replace("\\",'')

#backup data from 2 month ago
curry=year
currm=month

if month == "02":
  currm="12"
  curry=str(int(year)-1)
if month == "03":
  currm="01"
if month == "04":
  currm="02"
if month == "05":
  currm="03"
if month == "06":
  currm="04"
if month == "07":
  currm="05"
if month == "08":
  currm="06"
if month == "09":
  currm="07"
if month == "10":
  currm="08"
if month == "11":
  currm="09"
if month == "12":
  currm="10"
if month == "01":
  currm="11"

print(currm)
print(curry)

#DB loop
for x in result:
 code = str(x).replace("(",'').replace(")",'').replace(",",'').replace("'",'').replace("school_",'')
#skip school for testing
 if code == "800001":
   continue
 if code == "800002":
   continue
 if code == "800003":
   continue
 if code == "900001":
   continue
 if code == "900002":
   continue
 if code == "900003":
   continue
 #find the shcool name using school number
 #excel loop
 for y in range(1, school_sheet.nrows):
    if str(school_sheet.row_values(y)[3]) == code:
        schoolchname = str(school_sheet.row_values(y)[2])

#if the folder does not exist
 if not os.path.exists('/home/ubuntu/k12ea/' + schoolchname + "/" + curry + "-" + currm):
    db = MySQLdb.connect(host="localhost",user="root",charset="utf8")
    cursor = db.cursor()
    print("<<<<<<<<<<我是分割線>>>>>>>>>>")
    print("學校: " + schoolchname + " 學校代碼: " + code)
    print('/home/ubuntu/k12ea/' + schoolchname + "/" + curry + "-" + currm + " 資料夾不存在")
    os.system("sudo mkdir -p " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm)
    os.system("sudo chown ubuntu " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm)
    os.system("sudo chgrp ubuntu " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm)
    os.system("sudo chown ubuntu " + "/home/ubuntu/k12ea/" + schoolchname)
    os.system("sudo chgrp ubuntu " + "/home/ubuntu/k12ea/" + schoolchname)
    os.system("chmod 744 " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm)
    #speedtest
    cursor.execute("select count(*) from school_" + str(code) + ".speedtest" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " speedtest --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".speedtest." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".speedtest." + curry + "-" + currm + ".sql")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".speedtest where time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        print(schoolchname + ".speedtest." + curry + "-" + currm)
    else:
        print(schoolchname + ".speedtest " + curry + "-" + currm +  " 為空，跳過")

    #ports
    cursor.execute("select count(*) from school_" + str(code) + ".ports" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " ports --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".ports." + curry + "-" + currm + ".sql --skip-add-drop-table") 
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".ports where time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".ports." + curry + "-" + currm + ".sql") 
        print(schoolchname + ".ports." + curry + "-" + currm)
    else:
        print(schoolchname + ".ports " + curry + "-" + currm +  " 為空，跳過")

    #deviecs just for backup
    os.system("sudo mysqldump -uroot  school_"+ code + " devices " + "> " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" +  "school_" + code +".devices." + curry + "-" + currm + ".sql")
    print(schoolchname + ".devices." + curry + "-" + currm)

    #device_state_history
    cursor.execute("select count(*) from school_" + str(code) + ".device_state_history" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " device_state_history --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".device_state_history." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".device_state_history where time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".device_state_history." + curry + "-" + currm + ".sql")
        print(schoolchname + ".device_state_history." + curry + "-" + currm)
    else:
        print(schoolchname + ".device_state_history " + curry + "-" + currm +  " 為空，跳過")

    #device_perf
    cursor.execute("select count(*) from school_" + str(code) + ".device_perf" + " where timestamp BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " device_perf --where=\"timestamp BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".device_perf." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".device_perf where \"timestamp BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".device_perf." + curry + "-" + currm + ".sql")
        print(schoolchname + ".device_perf." + curry + "-" + currm)
    else:
        print(schoolchname + ".device_perf " + curry + "-" + currm +  " 為空，跳過")

    #alert_log
    cursor.execute("select count(*) from school_" + str(code) + ".alert_log" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " alert_log --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" +  "school_" + code +".alert_log." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".alert_log where \"time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" +  "school_" + code +".alert_log." + curry + "-" + currm + ".sql")
        print(schoolchname + ".alert_log." + curry + "-" + currm)
    else:
        print(schoolchname + ".alert_log " + curry + "-" + currm +  " 為空，跳過")
    db.close()

 else:
    db = MySQLdb.connect(host="localhost",user="root",charset="utf8")
    cursor = db.cursor()
    print("<<<<<<<<<<我是分割線>>>>>>>>>>")
    print("學校: " + schoolchname + " 學校代碼: " + code)
    os.system("chown ubuntu " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm)
    os.system("chgrp ubuntu " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm)
    os.system("sudo chown ubuntu " + "/home/ubuntu/k12ea/" + schoolchname)
    os.system("sudo chgrp ubuntu " + "/home/ubuntu/k12ea/" + schoolchname)
    os.system("chmod 744 " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm)
    print('/home/ubuntu/k12ea/' + schoolchname + " 資料夾存在")

    #speedtest
    cursor.execute("select count(*) from school_" + str(code) + ".speedtest" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " speedtest --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".speedtest." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".speedtest where time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".speedtest." + curry + "-" + currm + ".sql")
        print(schoolchname + ".speedtest." + curry + "-" + currm)
    else:
        print(schoolchname + ".speedtest " + curry + "-" + currm +  " 為空，跳過")

    #ports
    cursor.execute("select count(*) from school_" + str(code) + ".ports" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " ports --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".ports." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".ports where time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".ports." + curry + "-" + currm + ".sql")
        print(schoolchname + ".ports." + curry + "-" + currm)
    else:
        print(schoolchname + ".ports " + curry + "-" + currm +  " 為空，跳過")

    #device just for backup
    os.system("sudo mysqldump -uroot  school_"+ code + " devices " + "> " + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".devices." + curry + "-" + currm + ".sql")
    print(schoolchname + ".devices." + curry + "-" + currm)

    #device_state_history
    cursor.execute("select count(*) from school_" + str(code) + ".device_state_history" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " device_state_history --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".device_state_history." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".device_state_history where time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        print(schoolchname + ".device_state_history." + curry + "-" + currm)
    else:
        print(schoolchname + ".device_state_history " + curry + "-" + currm +  " 為空，跳過")

    #device_perf
    cursor.execute("select count(*) from school_" + str(code) + ".device_perf" + " where timestamp BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " device_perf --where=\"timestamp BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".device_perf." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".device_perf where timestamp BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".device_perf." + curry + "-" + currm + ".sql")
        print(schoolchname + ".device_perf." + curry + "-" + currm)
    else:
        print(schoolchname + ".device_perf " + curry + "-" + currm +  " 為空，跳過")

    #alert log
    cursor.execute("select count(*) from school_" + str(code) + ".alert_log" + " where time_logged BETWEEN " + "\'" + curry +  "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'")
    result = cursor.fetchall()
    if int(str(result).replace("(",'').replace(")",'').replace(",",'')) != 0:
        os.system("sudo mysqldump -u" + mysql_user + " -p" + mysql_passwd + " school_"+ code + " alert_log --where=\"time_logged BETWEEN "+ "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  "and" + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + "\"" + ">" + "/home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" + "school_" + code +".alert_log." + curry + "-" + currm + ".sql --skip-add-drop-table")
        os.system("sudo mysql -uroot  -e " + '\"' + "delete from school_"+ code + ".alert_log where time_logged BETWEEN " + "\'" + curry + "-" + currm + "-01 00:00:00" +  "\'" +  " and " + "\'" + curry  + "-" + currm + "-31 23:59:59" + "\'" + '\"')
        os.system("sudo sed -i 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' " + " /home/ubuntu/k12ea/" + schoolchname + "/" + curry + "-" + currm + "/" +  "school_" + code +".alert_log." + curry + "-" + currm + ".sql")
        print(schoolchname + ".alert_log." + curry + "-" + currm)
    else:
        print(schoolchname + ".alert_log " + curry + "-" + currm +  " 為空，跳過")
    db.close()
