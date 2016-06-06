#!/usr/bin/python
# coding: utf-8
#
# filename main.py 
# version 0.3 - June 6, 2016 by <Jaap at kroesschell-ictconsulting.ch>
# Objective read payments , modify and update payment using PyFileMaker
# 
#
# python 2.7 
#
import unicodedata
import os
import MySQLdb
import datetime
from PyFileMaker import FMServer

# Get access details from env / Or set locally (for debugging only) 
FMDBHOST = os.environ.get('FMDBHOST')					# FMDBHOST = 'host name or ip address'
FMDB = os.environ.get('FMDB')							# FMDB = 'fm database name'
FMDBUSER = os.environ.get('FMDBUSER')					# FMDBUSER = 'fm user name'
FMDBPASSWORD = os.environ.get('FMDBPASSWORD')			# FMDBPASSWORD = 'fm password'
SQLDBHOST = os.environ.get('SQLDBHOST')					# SQLDBHOST = 'host name or ip address'
SQLDB = os.environ.get('SQLDB')							# SQLDB = 'sql database name'
SQLDBUSER = os.environ.get('SQLDBUSER')					# SQLDBUSER = 'sql user name'
SQLDBPASSWORD = os.environ.get('SQLDBPASSWORD')			# SQLDBPASSWORD = 'sql password'

FMACCESS = FMDBUSER+':'+FMDBPASSWORD+'@'+FMDBHOST		# Facilitate fm db connection
fm = FMServer('http://'+FMACCESS)						# Facilitate fm db connection
fm._debug = True 										# Enable fms debugging (exposes urls)
fm.setDb(FMDB) 	 										# Declare fms db to be used


def getLayoutsFromFMdb():
	# create a list of tables and views
	for item in fm.getLayoutNames():
		print item
		fm.setLayout(item)
		print 
		if item:
			for item in fm.doView():
				print item
	return


def dateFormat(sourceDate):													# Define format for sql injection
	try:
		newdate = sourceDate.strftime("%Y-%m-%d")
	except IOError as e:
		print e

	return newdate


def intFormat(sourceInt):
	if isinstance( sourceInt , int ):
		return sourceInt
	else:
		print sourceInt, "is no integer "  
		return 


def getFromFMdb(): 															# read 10 records from "export sync" and put in sql db
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)			# Open sql connection
	cursor = db.cursor()
	selector = 'export sync'												# Define layout from fms
	fm.setLayout(selector)													# Use defined layout

	myList = list(range(29000,29010)) 										# Look for the x records
	results = fm.doFindQuery({'_Customer_ID': myList, }) 
	print 'Number of results : ', len(results) 														# Display the numeber of objects (records) found 
	for entry in results: 
		# print dir(entry)
		print '.',
		try:
			cursor.execute("""INSERT INTO `export` VALUES (%s,%s,%s,%s,%s  )""", (entry.Customer_ID, int(entry.Sales_Agent_ID), entry.Receipt_ID, entry.Notes, entry.Date_Scheduled_Payment_2))   
			db.commit()
		except ValueError as e:
			print "RecordID ", entry.RECORDID , "sql transaction not succesful ", e
			db.rollback()

	db.close()																# Disconnect from sql server
	return


def getFromSqldb():
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)			# Open sql connection
	cursor = db.cursor()													# Prepare a cursor object using cursor() method
	# Prepare SQL query to INSERT a record into the database.
	# sql = "SELECT * FROM `export` "
	sql = "SELECT * FROM  `export` WHERE Customer_ID > 29000 "
	try:
		cursor.execute(sql)													# Execute the SQL command
		results = cursor.fetchall() 										# Fetch all the rows in a list of lists.
		dbList=[]
		for row in results:
			Customer_ID = row[0]
			Sales_Agent_ID = row[1]
			Receipt_ID = row[2]
			Notes = row[3]
			Date_Scheduled_Payment_2 = row[4]
			record = "Customer_ID=%s,Sales_Agent_ID=%s,Receipt_ID=%s,Notes=%s,Date_Scheduled_Payment_2=%s" % \
			(Customer_ID, Sales_Agent_ID, Receipt_ID, Notes, Date_Scheduled_Payment_2)
			dbList.append(record)
	except IOError as e:
		print "Error: unable to fetch data", e	
	db.close()																	# Disconnect from server
	return dbList

def sendToFMdb():
	fm.setDb('tc_export_trial') 												# Declare fms db to be used
	selector = 'export sync'													# Define layout 
	fm.setLayout(selector)														# Use defined layout
	result = fm.doFind(_Customer_ID = 29000 ) 
	return result

def editFMdb():
	fm.setDb('tc_export_trial') 												# Declare fms db to be used
	selector = 'export sync'													# Define layout 
	fm.setLayout(selector)														# Use defined layout
	result = fm.doFind(_Customer_ID = 29000) 
	for item in result:
		newData = getNewValue()
		print newData
		item.Notes = str(newData)
		fm.doEdit(item)
	return 


def initSqldb():																# Recreate a new table for testing
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)				# Open sql connection
	cursor = db.cursor()														# Prepare a cursor object using cursor() method									# Debug  test sql db access
	try:
		cursor.execute("""DROP TABLE IF EXISTS  `export`""")
		cursor.execute("""CREATE TABLE `export` \
				(`Customer_ID` INT NULL, `Sales_Agent_ID` INT NULL, `Receipt_ID` INT NULL, \
					`Notes` TEXT NULL, `Date_Scheduled_Payment_2` DATE NULL)""")
		db.commit()
	except:
		db.rollback()
	db.close()																	# Disconnect from server

def updateSqlRecord(newNotesField):															# update hardcoded record
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)				# Open sql connection
	cursor = db.cursor()
	try:
		cursor.execute("""UPDATE `test_database`.`export` SET `Notes`=%s WHERE  `Customer_ID`=29000 AND `Sales_Agent_ID`=85 AND `Receipt_ID`=29094 LIMIT 1;""", [newNotesField])
		db.commit()
	except IOError as e:
		print e
		db.rollback()
	db.close()		
	return

def getNewValue():
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)				# Open sql connection
	cursor = db.cursor()
	cursor.execute("""SELECT `Notes` FROM `test_database`.`export` WHERE  `Customer_ID`=29000 LIMIT 1;""")
	data = str((cursor.fetchone()[0]))
	print 'output from sql fetch is : ', data
	db.close()	
	return data

def run():
	# Customer_ID = 29000
	initSqldb()												# erase all data in sql db
	getFromFMdb()											# 10 records from fm to sql
	updateSqlRecord('1) This is a note entered into sql db ')	# update notes field in one sql record with indicated text			
	editFMdb()												# write field back from sql db to fm db for this record

	return

run() 

# note = ຄຳມ່ວນ

# 
# getFromFMdb()

# --
# s = getFromSqldb()
# for each in s:
# 	record = each.split(',')
# 	for item in range(0,5):
# 		print (record[item].split('='))
# --
# currentlist = getFromSqldb()

# some sql stuff
# UPDATE `test_database`.`export` SET `Notes`='test 2.' WHERE  `Customer_ID`=29000 AND `Sales_Agent_ID`=85 AND `Receipt_ID`=29094 AND `Notes`='None'  LIMIT 1;
# SELECT `Customer_ID`, `Sales_Agent_ID`, `Receipt_ID`, `Notes`, `Date_Scheduled_Payment_2` FROM `test_database`.`export` WHERE  `Customer_ID`=29000 AND `Sales_Agent_ID`=85 AND `Receipt_ID`=29094 AND `Notes`='This is an example note.' AND `Date_Scheduled_Payment_2`='0000-00-00' LIMIT 1;






	


