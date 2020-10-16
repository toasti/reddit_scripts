### approve all posts in unmoderated queue

import praw
import datetime

CLIENT_ID = ''
CLIENT_SECRET = ''
USER_AGENT = ''
USER_PASSWORD = ''
USER_NAME = ''

SUBREDDIT = ""

# logs into reddit
def login():
    print("### Logging in...")
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         user_agent=USER_AGENT,
                         password=USER_PASSWORD,
                         username=USER_NAME)
    print("### Logged in!\n")
    return reddit


# main
######
def main():
    reddit = login()
    non_empty = True
    while non_empty:
        print("--- pulling next 100 posts")
        unmoderated = reddit.subreddit(SUBREDDIT).mod.unmoderated()
        non_empty = False
        for submission in unmoderated:
            print(f'{datetime.datetime.utcfromtimestamp(submission.created_utc)}')
            submission.mod.approve()
            non_empty = True


main()
