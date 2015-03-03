#!/usr/bin/python

###################################################################################
# twitter_phaseII.py - Read the tweets collected and calculate the sentiment 
# content based on SentiWordNet.
#
# Philip R. Moyer
# February 2015
# Copyright (c) 2015 All rights reserved
###################################################################################

#######################
# Libraries
#######################

from __future__ import division
import nltk
import time
import datetime
import sys
import MySQLdb
import collections
from twython import Twython, TwythonError
from dateutil.parser import parse
from nltk.corpus import stopwords


#######################
# Globals
#######################

# Database access - mySQL

dbHost = "REMOTE_HOST"
dbUser = "mySQL_USER"
dbPass = "mySQL_PASSWORD"
dbName = "twitterv01"
dbTable = "tweets"	# id, tweet, tuser, tdate, ttime
dbSentTable = "sentiment"	# id, pos, posscore, negscore, word, gloss, cid


#######################
# Classes and Methods
#######################

# Remote Twitter database

class remoteDB:
	def __init__(self):
		self.db = MySQLdb.connect(dbHost, dbUser, dbPass, dbName)
		self.curs = self.db.cursor()
		return None

	# Twitter database methods

	def fetchData(self):
		# Fetch the tweets from the database
		qString = "SELECT tweet FROM tweets;"
		self.curs.execute(qString)
		self.data = self.curs.fetchall()
		# Text is a list of tokens
		rv = self.convertToList(self.data)
		return rv

	def convertToList(self, data):
		rv = []
		for tweet in data:
			for tSent in tweet:
				# Remove stopwords
				for tVal in stopwords.words("english"):
					# print "removing ", tVal
					tRep = " " + tVal + " "
					tSent = tSent.replace(tRep, " ")
				rv = rv + tSent.split()
		return rv

	# SentiWordNet methods

	def initializeSentiment(self):
		self.cache = dict()
		return None

	def fetchWord(self, word):
		if word in self.cache.keys():
			# print word, " is in cache ", self.cache[word]
			return self.cache[word]
		newWord = word + "#%"
		qString = "SELECT pos,posscore,negscore FROM sentiment WHERE word LIKE \"" + newWord + "%\";"
		self.curs.execute(qString)
		self.data = self.curs.fetchall()
		# self.data is a list of word matches
		self.sentiment = 0.0
		for tData in self.data:
			self.sentiment = self.sentiment + tData[1] - tData[2]
		self.cache[word] = self.sentiment
		# print word, " sentiment ", self.sentiment
		return self.sentiment


#######################
# Functions
#######################

# Calculate the lexical diversity of the text
def lexicalDiversity(text):
	return len(text)/len(set(text))

# Create and return a dictionary of word counts, sorted 
# in decreasing order
def FreqDist(textList):
	wordDict = dict()
	for word in textList:
		if word in wordDict:
			wordDict[word] += 1
		else:
			wordDict[word] = 1
	# To sort by value: OrderedDict(sorted(d.items(), key=lambda t: t[1]))
	rv = collections.OrderedDict(sorted(wordDict.items(), key=lambda t: t[1]))
	return rv


#######################
# Main
#######################

if __name__ == "__main__":
	# Connect to mySQL
	tweetDB = remoteDB()
	# Retreive a list of words from tweets
	tweetText = tweetDB.fetchData()

	# Calculate the lexical diversity using NLTK functions
	# print "Lexical diversity: ", lexicalDiversity(tweetText)
	# print "Count of Deloitte: ", tweetText.count("deloitte")

	# Tokenizee the tweets
	# tweetTokens = set(tweetText)
	# tweetTokens = sorted(tweetTokens)
	# print "Token count: ", len(tweetTokens)

	# Frequency distributions
	# twFreqDist = FreqDist(tweetText)
	# twVocab = twFreqDist.keys()

	# Print the frequency distribution (wordy)
	# for twWord, twCount in twFreqDist.iteritems():
	#	print twWord, ": ", twCount
	
	# Print the words longer than five characters long and occuring at least three times
	# newList = sorted(w for w in set(tweetText) if len(w) > 5 and twFreqDist[w] > 2)
	# print "Words longer than 5 and occuring at least three times:"
	# print newList
	# print ""
	
	# Use collocations to extract bigrams for analysis
	# twBigrams = nltk.bigrams(tweetText)
	# bigramCounts = dict()
	# print "Bigrams:"
	# for tVal in twBigrams:
	# 	if tVal in bigramCounts.keys():
	# 		bigramCounts[tVal] += 1
	# 	else:
	# 		bigramCounts[tVal] = 1
	# print len(bigramCounts), " unique bigrams"
	# print ""

	# Calculate the sentiment value of the tweets
	# print "Calculating sentiment."
	tweetDB.initializeSentiment()
	totSent = 0.0
	totWordCount = 0
	PosSent = 0.0
	NegSent = 0.0
	for tWord in tweetText:
		rv = tweetDB.fetchWord(tWord)
		totSent += rv
		if rv < 0:
			NegSent += rv
		else:
			PosSent += rv
		totWordCount += 1
	# print ""
	print "Total sentiment: " + repr(totSent)
	print "Positive Sentiment: ", PosSent, " Negative Sentiment: ", NegSent
	print "Average Sentiment: ", totSent/totWordCount, " per word"

	exit

