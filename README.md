# twitter_sentiment
Python code to use SentiWordNet to analyze Twitter sentiment content.

You will need a Twitte application configured, which you can do at https://apps.twitter.com.

This software assumes there is a remote mySQL database constructed to hold sentiment data from SentiWordNet. The schema
for this datbase is embedded in the code (sorry).  You will need to edit the code to include your own Oauth keys for Twitter
and the appropriate connection information for the mySQL database. I have a database named "twitter" with two tables: tweets
and sentiment.

The first step, once the database is constructed properly, is to download SentiWordNet text sentiment file. This is 13 MB
uncompressed. We don't want to load it into the Raspberry Pi's memory, so we'll use the database instead. Once you have the
SentiWordNet file saved in a location, and uncompressed, edit the code to put in the correct location. Then run
loadsentiwordnet.py to load the fields into the database.

The next step is to edit and run twitter_analysis_v04.py. Edit it to contain the proper searh terms, along with the Twitter
and database authentication information. Then simply run the program (you may need to use sudo) to load tweets into the
database.

After you have loaded tweets, edit twitter_phaseII_v01.py with authentication information as before (it's all in the
"Globals" section). Then simply run the program, and it will display sentiment values (total, positive, negative, and percentage
per word).

ToDo:
Add schema definition files to repository.
