#!/usr/bin/python
# coding: utf-8
#
# filename main.py 
# version 0.2 - June 6, 2016 by <Jaap at kroesschell-ictconsulting.ch>
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
		"---------------------"
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
	except ValueError as e:
		print e

	return newdate


def intFormat(sourceInt):
	if isinstance( sourceInt , int ):
		return sourceInt
	else:
		print sourceInt, "is no integer "  
		return 


def getFromFMdb(): # and put in sql db
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)			# Open sql connection
	selector = 'export sync'												# Define layout from fms
	fm.setLayout(selector)													# Use defined layout

	myList = list(range(29000,29010)) 										# Look for the x records
	results = fm.doFindQuery({'_Customer_ID': myList, }) 
	print len(results) 														# Display the numeber of objects (records) found 

	print "===================="
	print '   send to sql db   '
	print "===================="
	for entry in results: 
		# print dir(entry)
		print '.',
		try:
			cursor.execute("""INSERT INTO `export` VALUES (%s,%s,%s,%s,%s  )""", (entry.Customer_ID, int(entry.Sales_Agent_ID), entry.Receipt_ID, entry.Notes, entry.Date_Scheduled_Payment_2))   
			db.commit()
		except:
			print "RecordID ", entry.RECORDID , "sql transaction not succesful "
			db.rollback()

	db.close()																# Disconnect from sql server
	return


def getFromSqldb():
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)			# Open sql connection
	cursor = db.cursor()													# Prepare a cursor object using cursor() method
	# Prepare SQL query to INSERT a record into the database.
	# sql = "SELECT * FROM `export` "
	sql = "SELECT * FROM  `export` WHERE Customer_ID > 29001 "
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
	result = fm.doFind(_Receipt_ID = 29001 ) 
	return results

def editFMdb():
	fm.setDb('tc_export_trial') 												# Declare fms db to be used
	selector = 'export sync'													# Define layout 
	fm.setLayout(selector)														# Use defined layout
	result = fm.doFind(_Receipt_ID = 29001 ) 
	for item in result:
		item.Notes = 'write back'
		fm.doEdit(item)
	return result


def initSqldb():																# Recreate a new table for testing
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)				# Open sql connection
	cursor = db.cursor()														# Prepare a cursor object using cursor() method
	cursor.execute("SELECT VERSION()")											# Execute SQL query using execute() method.
	data = cursor.fetchone()													# Fetch a single row using fetchone() method.
	# print "Database version : %s " % data 									# Debug  test sql db access
	try:
		cursor.execute("""DROP TABLE IF EXISTS  `export`""")
		cursor.execute("""CREATE TABLE `export` \
				(`Customer_ID` INT NULL, `Sales_Agent_ID` INT NULL, `Receipt_ID` INT NULL, `Notes` TEXT NULL, `Date_Scheduled_Payment_2` DATE NULL)""")
		db.commit()
	except:
		db.rollback()
	db.close()																	# Disconnect from server

# run 

# initSqldb()
# getFromFMdb()
s = getFromSqldb()
for each in s:
	record = each.split(',')
	for item in range(0,5):
		print (record[item].split('='))

# currentlist = getFromSqldb()








	


