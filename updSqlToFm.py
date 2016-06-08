#!/usr/bin/python
# coding: utf-8
#
# filename updSqlToFm.py
# version 0.36 - June 8, 2016 by <Jaap at kroesschell-ictconsulting.ch>
# Objective read sql data and check for changes in the last 24 hours (timestamp)
# 
#
# python 2.7 
#
import unicodedata
import os
import MySQLdb
from datetime import datetime, timedelta
from PyFileMaker import FMServer

# Get access details from env / Or set locally (for debugging only) 
FMDBHOST = os.environ.get('FMDBHOST')	# FMDBHOST = 'host name or ip address'
FMDB 	= os.environ.get('FMDB')	# FMDB = 'fm database name'
FMDBUSER = os.environ.get('FMDBUSER')	# FMDBUSER = 'fm user name'
FMDBPASSWORD = os.environ.get('FMDBPASSWORD')	# FMDBPASSWORD = 'fm password'

SQLDBHOST = os.environ.get('SQLDBHOST')	# SQLDBHOST = 'host name or ip address'
SQLDB = os.environ.get('SQLDB')	# SQLDB = 'sql database name'
SQLDBUSER = os.environ.get('SQLDBUSER')	# SQLDBUSER = 'sql user name'
SQLDBPASSWORD = os.environ.get('SQLDBPASSWORD')	# SQLDBPASSWORD = 'sql password'

# TC AWS db ( also change db name in sql code manually)
# SQLDBHOST = os.environ.get('TCAWS_SQLDBHOST')	# SQLDBHOST = 'host name or ip address'
# SQLDB = os.environ.get('TCAWS_SQLDB')	# SQLDB = 'sql database name'
# SQLDBUSER = os.environ.get('TCAWS_SQLDBUSER')	# SQLDBUSER = 'sql user name'
# SQLDBPASSWORD = os.environ.get('TCAWS_SQLDBPASSWORD')	# SQLDBPASSWORD = 'sql password'

FMACCESS = FMDBUSER+':'+FMDBPASSWORD+'@'+FMDBHOST	# Facilitate fm db connection
fm = FMServer('http://'+FMACCESS)	# Facilitate fm db connection
# fm._debug = True	# Enable fms debugging (exposes urls)
fm.setDb(FMDB)	# Declare fms db to be used



sqlFields = ["Customer_ID", "name", "province_id", "province_la_en", "district_id", "district_la", "village_id", "village_la", \
"sub_unit", "latitude", "longitude", "phone_1", "phone_2", "notes", "collector_id", "sync_datetime", "update_datetime"]

fmFields = ["Customer_ID", "Customers_Village_Sale.District_ID", "Customers_Village_Sale.Name_Full_Bilingual", "Customers_Village_Sale.Notes", \
"Customers_Village_Sale.Phone_1", "Customers_Village_Sale.Province_ID", "Customers_Village_Sale.Ship_To_Street_Lao","Customers_Village_Sale.Village_ID", \
"Date_Payment_10", "Date_Payment_11", "Date_Payment_12", "Date_Payment_1_Initial", "Date_Payment_2", "Date_Payment_3", "Date_Payment_4", \
"Date_Payment_5", "Date_Payment_6", "Date_Payment_7", "Date_Payment_8", "Date_Payment_9", "Date_Payment_Adjustment_1","Date_Payment_Adjustment_2", \
"Date_Scheduled_Payment_2", "Date_Scheduled_Payment_3", "Date_Scheduled_Payment_4", "Date_Scheduled_Payment_5", "Date_Scheduled_Payment_6", \
"Date_Scheduled_Payment_7", "Date_Scheduled_Payment_8", "Date_Scheduled_Payment_9", "District_Reference_Village_Sales.District_Name_English", \
"District_Reference_Village_Sales.District_Name_Lao", "MODID", "Notes", "Notes_Adjustment_1", "Notes_Adjustment_2", \
"Payment_10", "Payment_10_Collector_ID", "Payment_10_Receipt_No", "Payment_11", "Payment_11_Collector_ID", "Payment_11_Receipt_No", \
"Payment_12", "Payment_12_Collector_ID", "Payment_12_Receipt_No", "Payment_1_Initial", "Payment_2", "Payment_2_Collector_ID", "Payment_2_Receipt_No", \
"Payment_3", "Payment_3_Collector_ID", "Payment_3_Receipt_No", "Payment_4", "Payment_4_Collector_ID", "Payment_4_Receipt_No", "Payment_5", \
"Payment_5_Collector_ID", "Payment_5_Receipt_No", "Payment_6", "Payment_6_Collector_ID", "Payment_6_Receipt_No", "Payment_7", "Payment_7_Collector_ID", \
"Payment_7_Receipt_No", "Payment_8", "Payment_8_Collector_ID", "Payment_8_Receipt_No", "Payment_9", "Payment_9_Collector_ID", "Payment_9_Receipt_No", \
"Payment_Adjustment_1", "Payment_Adjustment_1_Collector_ID", "Payment_Adjustment_1_Receipt_No", "Payment_Adjustment_2", "Payment_Adjustment_2_Collector_ID", \
"Payment_Adjustment_2_Receipt_No", "Payment_Due_Collections", "Payment_Outstanding", "Payment_Scheduled_2", "Payment_Scheduled_3", "Payment_Scheduled_4", \
"Payment_Scheduled_5", "Payment_Scheduled_6", "Payment_Scheduled_7", "Payment_Scheduled_8", "Payment_Scheduled_9", \
"Province_Reference_Village_Sales.Province_Name_Bilingual", "Province_Reference_Village_Sales.Province_Name_English", \
"Province_Reference_Village_Sales.Province_Name_Lao", "RECORDID", "Receipt", "Receipt_ID", "Sales_Agent_ID", \
"Village_Reference_Village_Sales.Village_Name_English", "Village_Reference_Village_Sales.Village_Name_Lao"]

fmSelection = [0,]
# read timestamp for all records, and see if it is changed since moment x and print customer_id

def readSql():
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB,charset='utf8',
                     use_unicode=True) # Open sql connection 
	cursor = db.cursor()	# Prepare a cursor object using cursor() method		

	selector = 'export sync'	# Define layout from fms
	fm.setLayout(selector)	# Use defined layout

	# def timeFilter(HRS, MINS=0, SECS=0):
	# 	return datetime.now() - timedelta(hours=HRS, minutes=MINS, seconds=SECS)

	# print "filter configured", timeFilter(1,30)
	# arg1='2016-06-08 09:58:01'
	# arg2='2016, 6, 8, 10, 55, 43'

	# the part below is to show how to write date back to fm
	# in this case I updated the notes field and the sync_datetime (can be update_datetime as well)
	# the do a query on the sql sb to find the recently updated record
	# then read Notes field from sql record, and put this in the fm db.
	# note that there is no logic implemented for checking : this needs to be further worked out
	# 1) sync process
	# 2) update process
	# 3) verification process 
	try:
		cursor.execute("SELECT * FROM customer where sync_datetime > '2016-06-08 13:58:01'") # fixed filter for testing
		# cursor.execute("SELECT * FROM customer where update_datetime > %s ", timeFilter(1)) 
		print("fetchall:")
		result = cursor.fetchall() 
		for row in result:
			record = row[0]
			a = fm.doFind(_Customer_ID=record) # find the record in fm corresponding with the sql record based on Customer_ID
			r = a[0]	#select first result
			# print "old value Notes= ", r.Notes
			# print "Customer_ID =", result[0][0]
			# print result[0][13] # first record, item 13 = notes
			r.Notes = result[0][13] # update field in fm with data from sql
			fm.doEdit(r) # commit change in fm
			# print "new value Notes= ", r.Notes # read field from fm after update 

			# for index in range(0,17):
			# 	print '\t index ', index,
				# print sqlFields[index], '=', row[index],',' # show result in display
				# Get to the right record in fmdb row[0] = Customer_ID
				# Then update the fields in fmdb for this record.


				# print dir(r)
				# for each in r:
				# 	print a.each



		# cursor.execute("SELECT * FROM customer where update_datetime >'2016-06-08 13:58:01'") 
		# print("\nfetch one:")
		# res = cursor.fetchone() 
		# print(res)
	except IOError as e:
		print "Error: unable to fetch data from customer",e
	cursor.close()
	return

def run():
	readSql()
	# for x in range(0,95):
	# 	print x, fmFields[x]
	return

run()


