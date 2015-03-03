#!/usr/bin/python

###################################################################################
# twitter_analysis.py - Retrieves search data from Twitter and performs sentiment
# analysis to determine if sentiments are trending positive or negative.
#
# Philip R. Moyer
# February 2015
# Copyright (c) 2015 All rights reserved
###################################################################################

##################
# Libraries
##################

from socket import *
import time
import datetime
import sys
import nltk
import json
import urllib
import MySQLdb
import re
from twython import Twython, TwythonError
from dateutil.parser import parse


##################
# Globals
##################

searchTerm = 'SEARCHTERM'	# search term to run on Twitter

# Twitter API and OAuth keys:

API_key = "CONSUMER_KEY"
API_secret = "CONSUMER_SECRET"
accessToken = "ACCESS_TOKEN"
accessSecret = "ACCESS_KEY"

# Database access - mySQL

dbHost = "REMOTE_HOST"
dbUser = "mySQL_USER"
dbPass = "mySQL_PASSWORD"
dbName = "twitterv01"
dbTable = "tweets"	# id, tweet, tuser, tdate, ttime


##################
# Classes and Methods
##################

# Remote Twitter database

class remoteDB:
	def __init__(self):
		self.db = MySQLdb.connect(dbHost, dbUser, dbPass, dbName)
		self.curs = self.db.cursor()
		return None

	def insert(self, tID, tText, tUser, tTS):
		tDate = self.extractDate(tTS)
		tTime = self.extractTime(tTS)
		newTweet = cleanTweet(tText)
		iString = "INSERT INTO " + dbTable + " (id, tweet, tuser, tdate, ttime) VALUES (\"" + \
			repr(tID) + "\"," + \
			"\"" + newTweet + "\"," + \
			"\"" + tUser + "\"," + \
			"\"" + tDate + "\"," + \
			"\"" + tTime + "\");"
		self.curs.execute(iString)
		self.db.commit()

	# Extract the Date and Time from the stupidly formatted Twitter timestamp:
	# Wed Feb 18 10:28:18 +0000 2015

	def extractDate(self, tTimeStamp):
		dt = parse(tTimeStamp)
		# rv = repr(dt.month) + "/" + repr(dt.day) + "/" + repr(dt.year)
		rv = repr(dt.year) + "-" + repr(dt.month) + "-" + repr(dt.day)
		return rv

	def extractTime(self, tTimeStamp):
		dt = parse(tTimeStamp)
		rv = repr(dt.hour) + ":" + repr(dt.minute) + ":" + repr(dt.second)
		return rv

	def getMaxID(self):
		queryString = "SELECT MAX(id) FROM tweets;"
		rv = 0
		self.curs.execute(queryString)
		rv = self.curs.fetchall()
		rv = rv[0][0]
		return rv

	def getMinID(self):
		queryString = "SELECT MIN(id) FROM tweets;"
		rv = 0
		self.curs.execute(queryString)
		rv = self.curs.fetchall()
		rv = rv[0][0]
		return rv



# manage Twitter data retrieval

class twitSearch:
	def __init__(self, sTerm, db):
		self.minID = db.getMinID()	# to track the "tail" of the tweet stream
		self.maxID = db.getMaxID()	# to track the "head" of the tweet stream

		if self.minID == None:
			self.minID = 0
		if self.maxID == None:
			self.maxID = 0

		# Instantiate a twitter connection
		self.twitter = Twython(API_key, API_secret, accessToken, accessSecret)
		try:
			# Run search, return 100 tweets, only in English, and most recent
			self.search_results = self.twitter.search(q=sTerm, count=100, lang='en', result_type='recent', since_id=repr(self.maxID+1).replace("L",""))
		except TwythonError as e:
			print e

		# Track the window of tweets we've seen

		for tweet in self.search_results['statuses']:
			if self.maxID == 0:
				self.maxID = tweet['id']
				self.minID = tweet['id']
			else:
				if tweet['id'] > self.maxID:
					self.maxID = tweet['id']
				if tweet['id'] < self.minID:
					self.minID = tweet['id']

		return None
		
	def doSearchOlder(self, sTerm, db):
		# Instantiate a twitter connection
		self.twitter = Twython(API_key, API_secret, accessToken, accessSecret)
		try:
			# Run search, return 100 tweets, only in English, and most recent
			self.search_results = self.twitter.search(q=sTerm, count=100, lang='en', result_type='recent', max_id=repr(self.minID-1).replace("L",""))
		except TwythonError as e:
			print e

		# Track the window of tweets we've seen

		for tweet in self.search_results['statuses']:
			if tweet['id'] > self.maxID:
				self.maxID = tweet['id']
			if tweet['id'] < self.minID:
				self.minID = tweet['id']

		return None

	def doSearchNewer(self, sTerm, db):
		# Instantiate a twitter connection
		self.twitter = Twython(API_key, API_secret, accessToken, accessSecret)
		try:
			# Run search, return 100 tweets, only in English, and most recent
			self.search_results = self.twitter.search(q=sTerm, count=100, lang='en', result_type='recent', since_id=repr(self.maxID+1).replace("L",""))
		except TwythonError as e:
			print e

		# Track the window of tweets we've seen

		for tweet in self.search_results['statuses']:
			if tweet['id'] > self.maxID:
				self.maxID = tweet['id']
			if tweet['id'] < self.minID:
				self.minID = tweet['id']

		return None

	def saveResults(self, db):
		for tweet in self.search_results['statuses']:
			try:
				db.insert(tweet['id'], tweet['text'].encode('utf-8'), tweet['user']['screen_name'].encode('utf-8'), tweet['created_at'])
			except TwythonError as e:
				print e
		return None

	def printResults(self):
		for tweet in self.search_results['statuses']:
			print tweet['id']
			print 'Tweet from @%s Date: %s' % (tweet['user']['screen_name'].encode('utf-8'), tweet['created_at'])
			print tweet['text'].encode('utf-8'), '\n'


##################
# Functions
##################

def cleanTweet(dirtyTweet):
	# Define emoticons and abbreviations to replace
	# Copied from "Building Machine Learning Systmes With Python"
	emo_repl = {
		# positive emoticons
		"&lt3": " good ",
		":d": " good ",
		":ddd": " good ",
		"=)": " happy ",
		"8)": " happy ",
		":-)": " happy ",
		":)": " happy ",
		";)": " happy ",
		"(-:": " happy ",
		"(:": " happy ",
		"=]": " happy ",
		"[=": " happy ",

		# negative emoticons
		":&gt;": " sad ",
		":')": " sad ",
		":-(": " bad ",
		":(": " bad ",
		":S": " bad ",
		":-S": " bad ",
	}

	emo_repl_order = [k for (k_len,k) in reversed(sorted([(len(k),k) for k in emo_repl.keys()]))]

	re_repl = {
		r"\br\b": "are",
		r"\bu\b": "you",
		r"\bhaha\b": "ha",
		r"\bhahaha\b": "ha",
		r"\don't\b": "do not",
		r"\bdoesn't\b": "does not",
		r"\bdidn't\b": "did not",
		r"\bhasn't\b": "has not",
		r"\haven't\b": "have not",
		r"\bhadn't\b": "had not",
		r"\bwon't\b": "will not",
		r"\bwouldn't\b": "would not",
		r"\bcan't\b": "can not",
		r"\bcannot\b": "can not",
		r"\bain't\b": "are not",
		r"\bwhat's\b": "what is",
		r"\bthere's\b": "there is",
	}

	# End copied code

	# Remove hyperlinks
	tmpTweet = re.sub("http://[^\s]*\s", "", dirtyTweet)
	tmpTweet = re.sub("https://[^\s]*\s", "", tmpTweet)

	# Convert to lowercase
	tmpTweet2 = tmpTweet.lower()

	# Convert eemoticonss to text
	for k in emo_repl_order:
		tmpTweet2 = tmpTweet2.replace(k, emo_repl[k])

	# Convert Twitter abbreviations to text
	for r, repl in re_repl.iteritems():
		tmpTweet2 = re.sub(r, repl, tmpTweet2)

	# Remove all punctuation except hashtag and at sign
	# rv = re.sub("[`~!$%^&*()_-=+\[{\]}\\|;:'\",<.>/?]", "", tmpTweet2)
	rv = re.sub("[\W]+", " ", tmpTweet2)

	return rv


##################
# Main
##################

if __name__ == "__main__":
	# Instantiate a connection to the remote database
	mysqlDB = remoteDB()

	# Perform the first block search
	twitterSearch = twitSearch(searchTerm, mysqlDB)
	twitterSearch.saveResults(mysqlDB)

	# Loop
	while True:
		# Get the block of 100 tweets older than the oldest we've seen so far
		searchResult = twitterSearch.doSearchOlder(searchTerm, mysqlDB)
		twitterSearch.saveResults(mysqlDB)

		# Get the newer tweets than we've seen so far (if any)
		searchResult = twitterSearch.doSearchNewer(searchTerm, mysqlDB)
		twitterSearch.saveResults(mysqlDB)
		
		# Delay for some time period
		break
		time.sleep(10)	# API is rate-limited to 450/15 minutes

