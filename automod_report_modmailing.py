import praw
import datetime
import re
import pandas as pd
import pytz

CLIENT_ID = 'clientid'
CLIENT_SECRET = 'clientsecret'
USER_AGENT = 'automod mail tests'
USER_PASSWORD = 'password'
USER_NAME = 'username'

SUBREDDIT = "earthporn"


# main
######
def main():
    reddit = login()
    startdate = datetime.datetime(2020, 6, 10, 0, 0, 0, tzinfo=datetime.timezone.utc)
    modlog_limit = 1000
    modmail_limit = 500

    automod_log = []
    for log in reddit.subreddit(SUBREDDIT).mod.log(mod='AutoModerator', action='removelink', limit=modlog_limit):
        if log.details == 'reports':
            date = datetime.datetime.utcfromtimestamp(log.created_utc)
            date = pytz.utc.localize(date)
            if date > startdate:
                post_id = re.sub("t3_", "", log.target_fullname)
                automod_log.append(post_id)

    automod_log = pd.DataFrame(automod_log)

    automod_mail = []
    for conv in reddit.subreddit(SUBREDDIT).modmail.conversations(state='archived', limit=modmail_limit):
        if conv.authors[0].name == 'AutoModerator':
            if conv.subject == 'Submission has been reported.':
                msg = conv.messages[0]
                date_string = msg.date
                last_colon_index = date_string.rfind(":")
                fixed_date_string = date_string[:last_colon_index] + date_string[last_colon_index + 1:]
                date = datetime.datetime.strptime(fixed_date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
                if date > startdate:
                    match = re.search("/comments/[a-zA-Z0-9]*/", msg.body_markdown).group()
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
