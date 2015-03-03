#!/usr/bin/python

###################################################################################
# load_sentiwordnet.py - Loads sentiwordnet data into remote mySQL database.
#
# Philip R. Moyer
# February 2015
# Copyright (c) 2015 All rights reserved
###################################################################################

#######################
# Libraries
#######################

import sys
import os
import MySQLdb
import re


#######################
# Globals
#######################

# Path to the raw data file

sentPath = "SentiWordNet_3.0.0_20130122.txt"

# Database access - mySQL running on Feynman

dbHost = "REMOTE_HOST"
dbUser = "mySQL_USER"
dbPass = "mySQL_PASSWORD"
dbName = "twitterv01"
dbTable = "sentiment"	# id, pos, posscore, negscore, word, gloss, cid


#######################
# Classes and Methods
#######################

# Remote sentiment database

class remoteDB:
	def __init__(self):
		self.db = MySQLdb.connect(dbHost, dbUser, dbPass, dbName)
		self.curs = self.db.cursor()
		return None

	def insert(self, tLine):
		# SentiWordNet lines have tab-deliminated fields
		valueList = tLine.strip().split('\t')

		# Break out valueList
		self.pos = valueList[0]
		self.id = valueList[1]
		self.posscore = valueList[2]
		self.negscore = valueList[3]
		self.words = valueList[4]
		self.gloss = valueList[5]
		# print self.pos, self.id, self.posscore, self.negscore, self.words

		# escape punctuation
		self.gloss = self.cleanGloss(self.gloss)
		self.cid = self.makeCID(self.id, self.pos)

		for cWord in self.words.split():
			iString = "INSERT INTO " + dbTable + " (pos, posscore, negscore, word, gloss, cid) VALUES (\"" + \
				self.pos + "\"," + \
				"\"" + repr(self.posscore).replace("\'","") + "\"," + \
				"\"" + repr(self.negscore).replace("\'","") + "\"," + \
				"\"" + cWord + "\"," + \
				"\"" + self.gloss + "\"," + \
				"\"" + self.cid + "\");"
			# print iString
			# print ""
			self.curs.execute(iString)
			self.db.commit()
		return None

	# The glossary field can contain quotes, comas, doubleqoutes, etc.

	def cleanGloss(self, tGloss):
		rv = tGloss
		rv = re.sub("\"", "\\\"", rv)
		rv = re.sub("\'", "\\\'", rv)
		return rv

	# Build the combined ID (CID) which actually uniquely identifies a word
	
	def makeCID(self, tID, tPOS):
		rv = repr(tID) + tPOS
		rv = rv.replace("\'", "")
		return rv


#######################
# Functions
#######################


#######################
# Main
#######################

if __name__ == "__main__":
	# Instantiate a connection to the remote database
	mysqlDB = remoteDB()

	# Open the SentiWordNet file
	with open(sentPath) as fh:
		for tLine in fh:
			if tLine[0] != '#' and len(tLine) > 0:
				mysqlDB.insert(tLine)
	fh.close()

	exit

