import os
import schedule
import time
from dotenv import load_dotenv
from CheckMentions import check_mentions

load_dotenv()

def load_minutes():
    """Load minutes value from environment variable."""
    return int(os.getenv('CHECK_MENTIONS_INTERVAL', 15))

def job():
    """Function to be scheduled."""
    check_mentions(int(os.getenv('CHECK_MENTIONS_INTERVAL', 15)))

if __name__ == "__main__":
    try:
        schedule.every(load_minutes()).minutes.do(job)

        print(f"Twitter Bot started. Checking mentions every {load_minutes()} minutes...")

        job()

        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except Exception as e:
        print(f"An error occurred: {e}")
