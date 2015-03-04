# Twitter Sentiment (twitter_sentiment)

Python code to use SentiWordNet to analyze Twitter sentiment content.

## Pre-requisites

- You will need a Twitter application configured, which you can do at https://apps.twitter.com.
- You will need the Twython library.

This software assumes there is a remote mySQL database constructed to hold tweets from Twitter and
sentiment data from SentiWordNet. The schema
for this datbase is embedded in the code.  You will need to edit the code to include your own Oauth keys for Twitter
and the appropriate connection information for the mySQL database. These settings are all in the "Globals" section in
the code. I have a database named "twitter" with two tables: tweets and sentiment.

## Setting up SentiWordNet

The first step, once the database is constructed properly, is to download SentiWordNet text sentiment file. This is 13 MB
uncompressed. We don't want to load it into the Raspberry Pi's memory, so we'll use the database instead. Once you have the
SentiWordNet file saved in a location, and uncompressed, edit the code to put in the correct location. Then run
_loadsentiwordnet.py_ to load the fields into the database.

## Running the programs

The next step is to edit and run _twitter_analysis_v04.py_. Edit it to contain the proper searh terms, along with the Twitter
and database authentication information. Then simply run the program (you may need to use sudo) to load tweets into the
database.

After you have loaded tweets, edit _twitter_phaseII_v01.py_ to add authentication information as before (it's all in the
"Globals" section). Then simply run the program, and it will display sentiment values (total, positive, negative, and percentage
per word).

ToDo:

 - Add schema definition files to repository.
