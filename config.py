import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")

def get_twitter_conn_v1(api_key, api_secret, access_token, access_token_secret) -> tweepy.API:
    """Get Twitter connection (v1.1)."""
    auth = tweepy.OAuth1UserHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    bearer_token=bearer_token,
)

client_v1 = get_twitter_conn_v1(consumer_key, consumer_secret, access_token, access_token_secret)