import os, sys
import xlrd
import time

school_list = xlrd.open_workbook("./315校名單.xlsx")
school_sheet = school_list.sheets()[0]
for x in range(int(sys.argv[1]), int(sys.argv[2])+1):
    os.system("python3 app.py " + str(int(school_sheet.row_values(x)[0])) + " " + str(school_sheet.row_values(x)[3]) + " > " + str(school_sheet.row_values(x)[3]) + ".log 2>&1 &")
    time.sleep(5)