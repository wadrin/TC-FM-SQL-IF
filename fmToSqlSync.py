#!/usr/bin/python
# coding: utf-8
#
# filename fmToSqlSync.py
# version 0.35 - June 7, 2016 by <Jaap at kroesschell-ictconsulting.ch>
# Objective read costomer records from export set and save into sql db
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
FMDB 	= os.environ.get('FMDB')	# FMDB = 'fm database name'
FMDBUSER = os.environ.get('FMDBUSER')	# FMDBUSER = 'fm user name'
FMDBPASSWORD = os.environ.get('FMDBPASSWORD')	# FMDBPASSWORD = 'fm password'
SQLDBHOST = os.environ.get('SQLDBHOST')	# SQLDBHOST = 'host name or ip address'
SQLDB = os.environ.get('SQLDB')	# SQLDB = 'sql database name'
SQLDBUSER = os.environ.get('SQLDBUSER')	# SQLDBUSER = 'sql user name'
SQLDBPASSWORD = os.environ.get('SQLDBPASSWORD')	# SQLDBPASSWORD = 'sql password'

FMACCESS = FMDBUSER+':'+FMDBPASSWORD+'@'+FMDBHOST	# Facilitate fm db connection
fm = FMServer('http://'+FMACCESS)	# Facilitate fm db connection
# fm._debug = True	# Enable fms debugging (exposes urls)
fm.setDb(FMDB)	# Declare fms db to be used


def initSqldb():	# (re)create a new table for testing
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB) # Open sql connection
	cursor = db.cursor()	# Prepare a cursor object using cursor() method									
	try: # setup customer table
		cursor.execute("""DROP TABLE IF EXISTS `customer`""")
		cursor.execute("""CREATE TABLE `customer` (\
	`customer_id` INT(11) NOT NULL COMMENT '_Customer ID',
	`name` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Customers::Name Full Bilingual' COLLATE 'utf8_unicode_ci',\
	`province_id` INT(11) NULL DEFAULT NULL COMMENT 'Customers::_Province ID',\
	`province_la_en` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Province_Customer Reference::Province Name Bilingual' COLLATE 'utf8_unicode_ci',\
	`district_id` INT(11) NULL DEFAULT NULL COMMENT 'Customers::_District ID',\
	`district_la` VARCHAR(50) NULL DEFAULT NULL COMMENT 'District_Customer Reference::District Name_Lao' COLLATE 'utf8_unicode_ci',\
	`village_id` INT(11) NULL DEFAULT NULL COMMENT 'Customers::_Village ID',
	`village_la` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Village_Customer Reference::Village Name Lao' COLLATE 'utf8_unicode_ci',\
	`sub_unit` VARCHAR(25) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',\
	`latitude` DECIMAL(8,6) NULL DEFAULT NULL COMMENT 'new column for GIS',\
	`longitude` DECIMAL(9,6) NULL DEFAULT NULL COMMENT 'new column for GIS',\
	`phone_1` VARCHAR(25) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',\
	`phone_2` VARCHAR(25) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',\
	`notes` VARCHAR(250) NULL DEFAULT NULL COMMENT 'Notes' COLLATE 'utf8_unicode_ci',\
	`collector_id` INT(11) NULL DEFAULT NULL,\
	`sync_datetime` DATETIME NULL DEFAULT NULL,\
	`update_datetime` DATETIME NULL DEFAULT NULL,\
	PRIMARY KEY (`customer_id`)) \
	COLLATE='utf8_unicode_ci' """)
		db.commit()
	except IOError as e:
		print 'customer :', e
		db.rollback()

	try: # setup collector table
		cursor.execute("""DROP TABLE IF EXISTS `collector`""")
		cursor.execute("""CREATE TABLE `collector` ( \
	`collector_id` INT(11) NOT NULL, \
	`name` VARCHAR(25) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci', \
	`password` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci', \
	PRIMARY KEY (`collector_id`)) \
	COLLATE='utf8_unicode_ci' """)
		db.commit()
	except IOError as e:
		print 'collector :', e
		db.rollback()

	db.close()	# Disconnect from server

def getFromFmToSql():
	db = MySQLdb.connect(SQLDBHOST,SQLDBUSER,SQLDBPASSWORD,SQLDB) # Open sql connection
	cursor = db.cursor()	# Prepare a cursor object using cursor() method		
	db.set_character_set('utf8')
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')	
	selector = 'export sync'	# Define layout from fms
	fm.setLayout(selector)	# Use defined layout

	def hasValue(intFieldName):	#  Function: if the given field contains a string, it is converted to an int
		if intFieldName:
			output=int(intFieldName)
		else:
			output=None
		return output

	count = 0
	play = True
	firstRecord = 33574
	steps = 50
	lastRecord = firstRecord + steps

	while play:
		myList = list(range(firstRecord,lastRecord))
		lastRecord = lastRecord + steps
		firstRecord = firstRecord + steps
		# print "------  from ", firstRecord, " to ", lastRecord," ------"
		# play = False



		myList = list(range(firstRecord,lastRecord))	# Look for the x records, range([start], stop[, step
		# print "list", myList
		results = fm.doFindQuery({'_Customer_ID': myList, })
		importedRecords = len(results)	
		if importedRecords > 0:
			play = True
		else:
			play = False
			print 

		for entry in results:
			# print '.',
			try:
				cursor.execute("""INSERT IGNORE INTO `test_database`.`customer` (`Customer_ID`, `name`, \
					`province_id`,`province_la_en`, `district_id`, `district_la`, `village_id`, `village_la`, \
					`sub_unit`,`latitude`, `longitude`, `phone_1`, `phone_2`, `notes`, `collector_id`, \
					`sync_datetime`, `update_datetime`) VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s )""", 
				 	(int(entry.Customer_ID), 
				 		entry.Customers_Village_Sale.Name_Full_Bilingual, 
				 		hasValue(entry.Customers_Village_Sale.Province_ID),
				 		entry.Province_Reference_Village_Sales.Province_Name_Bilingual, 
				 		hasValue(entry.Customers_Village_Sale.District_ID),
				 		entry.District_Reference_Village_Sales.District_Name_Lao, 
				 		hasValue(entry.Customers_Village_Sale.Village_ID),
				 		entry.Village_Reference_Village_Sales.Village_Name_Lao, 
				 		None, 
				 		None, 
				 		None, 
				 		entry.Customers_Village_Sale.Phone_1, 
				 		None, 
				 		entry.Customers_Village_Sale.Notes, 
				 		None, 
				 		None, 
				 		None ))
				db.commit()
			except IOError as e:
				print "Customer_ID ", entry.Customer_ID , "sql transaction not succesful ", e
				db.rollback()
		else:
			print  "."
	db.close()	# Disconnect from sql server
	return


def run():
	initSqldb()
	getFromFmToSql()
	return


run()