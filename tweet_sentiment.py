import re # Regex for Python
import tweepy # Library for connecting with Twitter API
from tweepy import OAuthHandler # Module for authentication process
from textblob import TextBlob # Popular library for NLP (Sentimental analysis specifically in our case)
import mysql.connector # Python-MySQL interface

# Authentication

## Obtained from Twitter
consumer_key = 'XXXXXXXXXXXXXXXXXXXXXX'
consumer_secret = 'XXXXXXXXXXXXXXXXXXXXXXXX'
access_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
access_token_secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'

## Perform Auth process

try:
    twit_auth = OAuthHandler(consumer_key,consumer_secret) # Create OAuth object for handling login
    twit_auth.set_access_token(access_token,access_token_secret) # Provide access tokens to OAuth
    twit_api = tweepy.API(twit_auth) # Call API to attempt login
except:
    print("Error: Authentication process failed!")

# Setup MySQL Environment

## Change parameters to match local database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  auth_plugin="mysql_native_password"
)

## Cursor to execute commands in MySQL server
my_cursor = mydb.cursor()

## Initial queries

my_cursor.execute("SET NAMES utf8mb4")
my_cursor.execute("CREATE DATABASE IF NOT EXISTS tweet_analysis")
my_cursor.execute("USE tweet_analysis")
my_cursor.execute("CREATE TABLE IF NOT EXISTS tweets (ID INT AUTO_INCREMENT PRIMARY KEY, Tweet VARCHAR(300), Sentiment VARCHAR(20), Product VARCHAR(100))")

# List of products to analyze - must be strings, can be extended or shortened as desired
products = ["Canon 5D Mark iii", "iPhone 12", "Samsung Galaxy S8"]

# Helper functions

def process_tweet(tweet):
    '''
    Removes links from tweets using regular expressions
    '''
    clean_tweet = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0–9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0–9@:%_\+.~#?&//=]*)', '', tweet, flags=re.MULTILINE) 
    clean_tweet = re.sub(r'[-a-zA-Z0–9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0–9@:%_\+.~#?&//=]*)', '', tweet, flags=re.MULTILINE) 

    ### Additional regex to remove hashtags, spelling errors available if needed
    return clean_tweet

def obtain_sentiment(tweet):
    '''
    Function to determine sentiment of tweet - Negative or Positive
    '''
    ### Create TextBlob object to analyze tweet
    sent = TextBlob(process_tweet(tweet))

    ### TextBlob determines sentiment based on a value called 'polarity'
    ### Polarity > 0: Positive reaction
    ### Polarity == 0: Neutral reaction
    ### Polarity < 0: Negative reaction
    if sent.sentiment.polarity > 0:
        return 'Positive'
    elif sent.sentiment.polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'

# Key function

def twitter_pull():
    '''
    Function to get Tweets from Twitter based on product
    '''
    ### Fetch Tweets based on query product
    try:
        my_cursor.execute("DELETE FROM tweets")
        for product in products:
            raw_tweets = twit_api.search(q = product, count = 50)
            
            ### Process tweets and add them to database
            for tweet in raw_tweets:
                tweet_text = str(tweet.text)
                tweet_sentiment = obtain_sentiment(tweet_text)
                
                query = "INSERT INTO tweets (Tweet, Sentiment, Product) VALUES (%s, %s, %s)"
                values = (tweet_text, tweet_sentiment, product)
                my_cursor.execute(query,values)

            mydb.commit()
        
    except tweepy.TweepError as error:
        ### Didn't work for some reason
        print("Error: " + str(error))

# Main call to twitter_pull function 

twitter_pull()

# Sample analysis of 'Canon' product

## Proportions of reactions to product
    
### Total number of tweets about product in database
my_cursor.execute("SELECT COUNT(*) FROM tweets WHERE Product = 'Canon 5D Mark iii'")
total_products = my_cursor.fetchone()[0]

print("\n\n----------------------PROPORTION OF SENTIMENT REACTIONS FOR PRODUCTS----------------------\n\n")

### Proportion of Positive tweets
my_cursor.execute("SELECT COUNT(Sentiment) AS Positive_Reactions FROM tweets WHERE PRODUCT = 'Canon 5D Mark iii' AND Sentiment = 'Positive'")
print(str(round((my_cursor.fetchone()[0] / total_products) * 100,2)) + "% of tweets about the Canon 5D Mark iii" + " were positive.")
    
### Proportion of Neutral tweets
my_cursor.execute("SELECT COUNT(Sentiment) AS Positive_Reactions FROM tweets WHERE PRODUCT = 'Canon 5D Mark iii' AND Sentiment = 'Neutral'")
print(str(round((my_cursor.fetchone()[0] / total_products) * 100,2)) + "% of tweets about the Canon 5D Mark iii" + " were neutral.")
    
### Proportion of Negative tweets
my_cursor.execute("SELECT COUNT(Sentiment) AS Positive_Reactions FROM tweets WHERE PRODUCT = 'Canon 5D Mark iii' AND Sentiment = 'Negative'")
print(str(round((my_cursor.fetchone()[0] / total_products) * 100,2)) + "% of tweets about the Canon 5D Mark iii" + " were negative.")

print("\n\n----------------------SAMPLE TWEETS FOR EACH REACTION----------------------\n\n")

### Sample Positive Tweet
print("POSITIVE:\n")
my_cursor.execute("SELECT Tweet FROM tweets WHERE Product = 'Canon 5D Mark iii' AND Sentiment = 'Positive' LIMIT 1;")
print(str(my_cursor.fetchone()[0]))

## Sample Neutral Tweet
print("\nNEUTRAL:\n")
my_cursor.execute("SELECT Tweet FROM tweets WHERE Product = 'Canon 5D Mark iii' AND Sentiment = 'Neutral' LIMIT 1;")
print(str(my_cursor.fetchone()[0]))

## Sample Negative Tweet
print("\nNEGATIVE:\n")
my_cursor.execute("SELECT Tweet FROM tweets WHERE Product = 'Canon 5D Mark iii' AND Sentiment = 'Negative' LIMIT 1;")
print(str(my_cursor.fetchone()[0]))