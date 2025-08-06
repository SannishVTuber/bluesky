#!/usr/bin/env python3

'''
Script to output all bluesky follows who haven't posted in the last 4 months

Setup:
1. Install atproto package with something like pip
    pip install atproto
2. Create secrets folder
3. Add file named bluesky with your password
4. Update my_handle variable to your profile 
5. Run!

Could this have been written with a __main__ function and command line arguments?  Sure could have!

'''

from datetime import datetime, timezone
from atproto import Client
import json

def get_secret(key):
    with open('secrets/' + key, 'r') as file:
        return file.read()

username = 'sannish.bsky.social'
# Optionally ignore the secrets folder and just put your password here
password = get_secret('bluesky')

# Authenticate
client = Client()
client.login(username, password)

# Page through followers to create a list of user ids ("did" in the atproto api)
def get_follow_list():

    users = list()

    # Get first 50 follows since I didn't want to put list/cursor initialization into the while loop
    response = client.get_follows(
        actor=username,
        limit = 50
    )

    # Add follow ids to the list
    for follow in response.follows:
        users.append(follow.did)

    # Keep paginating through the list using the cursor
    index = 0
    while (response.cursor != "" and response.cursor != None):
        response = client.get_follows(
            actor=username,
            limit = 50,
            cursor = response.cursor
        )

        for follow in response.follows:
            users.append(follow.did)

    return users

users = get_follow_list()


# Check each follow
for did in users:

    # Get 30 of their posts/reposts
    follow_feed = client.get_author_feed(
        actor=did,
        filter='posts_and_author_threads',
        limit=30,
    )

    # Get their username
    handle = client.get_profile(actor = did).handle

    # Output accounts with no posts at all
    if len(follow_feed.feed) == 0:
        print("No posts for: https://bsky.app/profile/" + handle)
        continue


    # Get the last post date
    last_posted = follow_feed.feed[0].post.indexed_at
    for post in follow_feed.feed:
        if last_posted < post.post.indexed_at:
            last_posted = post.post.indexed_at

    # If it's been over 120 days, output their profile URL to take a look
    days_since_last_post = (datetime.now(timezone.utc) - datetime.fromisoformat(last_posted)).days
    if days_since_last_post > 120:
        # This is where a person *could* automate unfollows
        print("https://bsky.app/profile/" + handle + " last posted " + str(days_since_last_post) + " days ago on " + last_posted)

    