#!/usr/bin/python
# coding: utf-8
#
# filename main.py 
# version 0.31 - June 6, 2016 by <Jaap at kroesschell-ictconsulting.ch>
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
FMDBHOST = os.environ.get('FMDBHOST')	# FMDBHOST = 'host name or ip address'
FMDB = os.environ.get('FMDB')			# FMDB = 'fm database name'
FMDBUSER = os.environ.get('FMDBUSER')	# FMDBUSER = 'fm user name'
FMDBPASSWORD = os.environ.get('FMDBPASSWORD')	# FMDBPASSWORD = 'fm password'
SQLDBHOST = os.environ.get('SQLDBHOST')	# SQLDBHOST = 'host name or ip address'
SQLDB = os.environ.get('SQLDB')			# SQLDB = 'sql database name'
SQLDBUSER = os.environ.get('SQLDBUSER')	# SQLDBUSER = 'sql user name'
SQLDBPASSWORD = os.environ.get('SQLDBPASSWORD')	# SQLDBPASSWORD = 'sql password'

FMACCESS = FMDBUSER+':'+FMDBPASSWORD+'@'+FMDBHOST	# Facilitate fm db connection
fm = FMServer('http://'+FMACCESS)					# Facilitate fm db connection
fm._debug = True 									# Enable fms debugging (exposes urls)
fm.setDb(FMDB) 	 									# Declare fms db to be used


def checkDbserver():					# wake sqlserver when sleeping (beta)
	hostname = SQLDBHOST#example
	response = os.system("ping -c 1 " + hostname)
	#and then check the response...
	if response == 0:
		print hostname, 'is up!… '
		print getDbseverVersion()
	else:
		  from subprocess import call
		  call(["~/scripts/wakepve.sh"]) # actual script to send wol package


def getDbseverVersion():				 # return version number of the sql server
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)	
	cursor = db.cursor()
	cursor.execute("SELECT VERSION()")	 # execute SQL query using execute() method.
	data = cursor.fetchone()			 # Fetch a single row using fetchone() method.
	version = "Database version : %s " % data
	db.close()	# disconnect from server
	return version


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


def dateFormat(sourceDate):					# Define format for sql injection
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


def getFromFMdb(): 								# read 10 records from "export sync" and put in sql db
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)	# Open sql connection
	cursor = db.cursor()
	selector = 'export sync'					# Define layout from fms
	fm.setLayout(selector)						# Use defined layout

	myList = list(range(29000,29010)) 			# Look for the x records
	results = fm.doFindQuery({'_Customer_ID': myList, }) 
	print 'Number of results : ', len(results) 	# Display the numeber of objects (records) found 

	cursor = db.cursor()


	print "===================="
	print '   send to sql db   '
	print "===================="
	for entry in results: 
		# print dir(entry)
		print '.',
		try:
			cursor.execute("""INSERT INTO `test_database`.`export` (`Customer_ID`, \
				`Sales_Agent_ID`, `Receipt_ID`, `Notes`, `Date_Scheduled_Payment_2`) VALUES (%s,%s,%s,%s,%s )""", \
				(entry.Customer_ID, entry.Sales_Agent_ID, entry.Receipt_ID, entry.Notes, entry.Date_Scheduled_Payment_2))
			db.commit()
		except ValueError as e:
			print "RecordID ", entry.RECORDID , "sql transaction not succesful ", e
			db.rollback()

	db.close()										# Disconnect from sql server
	return


def getFromSqldb():
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)	# Open sql connection
	cursor = db.cursor()							# Prepare a cursor object using cursor() method
	# Prepare SQL query to INSERT a record into the database.
	# sql = "SELECT * FROM `export` "
	sql = "SELECT * FROM  `export` WHERE Customer_ID > 29000 "

	try:
		cursor.execute(sql)							 # Execute the SQL command
		results = cursor.fetchall() 				 # Fetch all the rows in a list of lists.
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
	db.close()										# Disconnect from server
	return dbList

def sendToFMdb():
	fm.setDb('tc_export_trial') 					# Declare fms db to be used
	selector = 'export sync'						# Define layout 
	fm.setLayout(selector)							# Use defined layout
	result = fm.doFind(_Customer_ID = 29000 ) 
	return result

def editFMdb():
	fm.setDb('tc_export_trial') 					# Declare fms db to be used
	selector = 'export sync'						# Define layout 
	fm.setLayout(selector)							# Use defined layout
	result = fm.doFind(_Customer_ID = 29000) 
	for item in result:
		newData = getNewValue()
		print newData
		item.Notes = str(newData)
		fm.doEdit(item)
	return 


def initSqldb():									# Recreate a new table for testing
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB) # Open sql connection
	cursor = db.cursor()							# Prepare a cursor object using cursor() method									
	try:
		cursor.execute("""DROP TABLE IF EXISTS  `export`""")
		cursor.execute("""CREATE TABLE `export` \
				(`Customer_ID` INT NULL, `Sales_Agent_ID` INT NULL, `Receipt_ID` INT NULL, \
					`Notes` TEXT NULL, `Date_Scheduled_Payment_2` DATE NULL)""")
		db.commit()
	except:
		db.rollback()
	db.close()											# Disconnect from server

<<<<<<< HEAD
def updateSqlRecord(newNotesField):						# update hardcoded record
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB) # Open sql connection
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
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB)	# Open sql connection
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
	updateSqlRecord('1) This is a note entered into sql db.')	# update notes field in one sql record with indicated text			
	editFMdb()												# write field back from sql db to fm db for this record
	return

run() 

# original content note field = ຄຳມ່ວນ

# --
# s = getFromSqldb()
# for each in s:
# 	record = each.split(',')
# 	for item in range(0,5):
# 		print (record[item].split('='))
# --


	


