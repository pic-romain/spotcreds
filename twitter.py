import tweepy
import json
import re


def auth_twitter(twitter_client):
    CONSUMER_KEY = twitter_client["key"]
    CONSUMER_SECRET = twitter_client["secret"]
    ACCESS_TOKEN = twitter_client["access_token"]
    ACCESS_TOKEN_SECRET = twitter_client["access_token_secret"]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    twitter_api = tweepy.API(auth)
    return twitter_api

def read_last_seen(file_name):
    file = open(file_name,"r")
    try:
        last_seen_id = int(file.read().strip())
    except:
        last_seen_id = None
    file.close()
    return last_seen_id

def write_last_seen(file_name,last_seen_id):
    file = open(file_name,"w")
    file.write(str(last_seen_id))
    file.close()
    return last_seen_id