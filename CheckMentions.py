import tweepy
from config import client
from TweetParser import parse_command
from PumpLaunch import send_local_create_tx
import random
from datetime import datetime, timedelta, timezone

def check_mentions(time_window_minutes=15):
    my_twitter_id = client.get_me().data.id
    all_mentions = []
    next_token = None

    time_window = timedelta(minutes=time_window_minutes)
    current_time = datetime.now(timezone.utc)

    start_time = ((current_time-time_window).strftime("%Y-%m-%dT%H:%M:%SZ"))
    end_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Starting to fetch mentions for the last {time_window_minutes} minutes...")
    print(start_time)
    print(end_time)
    mentions_fetched = 0
    while len(all_mentions) < 500:
        mentions = client.get_users_mentions(
            id=my_twitter_id,
            max_results=100,
            media_fields="url",
            expansions="attachments.media_keys",
            tweet_fields=["public_metrics"],
            pagination_token=next_token,
            start_time = start_time,
            end_time = end_time
        )
        print(mentions)
        if mentions.data:
            all_mentions.extend(mentions.data)
            mentions_fetched += len(mentions.data)
            print(f"Fetched {len(mentions.data)} mentions. Total fetched: {mentions_fetched}")
        else:
            print("No new mentions fetched.")

        next_token = mentions.meta.get('next_token')
        if not next_token:
            break

    print(f"Total mentions collected: {len(all_mentions)}")

    media_dict = {media.media_key: media.url for media in mentions.includes.get("media", [])}
    valid_results = []

    for tweet in all_mentions:
        media_url = None
        if 'attachments' in tweet and 'media_keys' in tweet.attachments:
            media_url = media_dict.get(tweet.attachments['media_keys'][0])

        if media_url:
            try:
                result = parse_command(tweet.text, media_url)
                result['like_count'] = tweet.public_metrics['like_count']
                result['mention_id'] = tweet.id
                valid_results.append(result)
            except Exception as e:
                print(f"Failed to parse command for Tweet ID: {tweet.id}. Error: {e}")

    print(f"Valid results after parsing: {len(valid_results)}")
    print(valid_results)

    if valid_results:
        max_like_count = max(result['like_count'] for result in valid_results)
        top_results = [result for result in valid_results if result['like_count'] == max_like_count]
        selected_result = random.choice(top_results)
        print("Selected result:")
        print(selected_result)

        success, message = send_local_create_tx(
            selected_result['token_name'],
            selected_result['ticker'],
            selected_result['description'],
            selected_result['image_url']
        )
        print(f"Transaction creation result: Success={success}, Message={message}")

        if success:
            reply_text = f"Token '{selected_result['token_name']}' created successfully! 🚀\n{message}"
            tweet = client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=selected_result['mention_id']
            )
            print(tweet.data['id'])
            client.retweet(tweet.data['id'])
            print("Tweet and repost sent successfully!")
        else:
            print("Failed to create transaction. Skipping tweet.")
    else:
        print("No valid results found.")
