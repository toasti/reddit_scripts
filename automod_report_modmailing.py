
import sys
import praw
import prawcore
import datetime
import re
import pandas as pd
import pytz


CLIENT_ID = 'id'
CLIENT_SECRET = 'secret'
USER_AGENT = 'automod mail tests'
USER_PASSWORD = 'password'
USER_NAME = 'username'


SUBREDDIT = "earthporn"
MODERATOR = "t0asti"


# main
######
def main():
    reddit = login()
    today = datetime.datetime(2019, 11, 12, 0, 0, 0, tzinfo=datetime.timezone.utc)

    automod_log = []
    for log in reddit.subreddit(SUBREDDIT).mod.log(mod = 'AutoModerator', action = 'removelink', limit=1000):
        if log.details == 'reports':
            date = datetime.datetime.utcfromtimestamp(log.created_utc)
            date = pytz.utc.localize(date)
            if date > today:
                post_id = re.sub("t3_", "", log.target_fullname)
                automod_log.append(post_id)

    automod_log = pd.DataFrame(automod_log)

    automod_mail = []
    for conv in reddit.subreddit(SUBREDDIT).modmail.conversations(state='archived', limit = 100):
        if conv.authors[0].name == 'AutoModerator':
            if conv.subject == 'Submission has been reported.':
                msg = conv.messages[0]
                date = datetime.datetime.strptime(msg.date, "%Y-%m-%dT%H:%M:%S.%f%z")
                if date > today: 
                    match = re.search("/comments/[a-zA-Z0-9]*/" , msg.body_markdown).group()
                    match = re.sub("/comments/", "", match)
                    match = re.sub("/", "", match)
                    automod_mail.append(match)
    
    automod_mail = pd.DataFrame(automod_mail)

    automod_log = automod_log.assign(mailed=automod_log[0].isin(automod_mail[0]).astype(int))
    automod_mail = automod_mail.assign(logged=automod_mail[0].isin(automod_log[0]).astype(int))
    print("------")
    print("modlog:")
    print(automod_log)
    print("------")
    print("modmail:")
    print(automod_mail)
    print("\n")
    not_mailed = automod_log.mailed.size - automod_log.mailed.sum()
    not_logged = automod_mail.logged.size - automod_mail.logged.sum()
    print("logged but not mailed: {}".format(not_mailed))
    print("mailed but not logged: {}".format(not_logged))
    

# -- main end --#

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
# -- login end --#
    
main()