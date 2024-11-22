from atproto import Client, AtUri
import argparse
from collections import defaultdict
from time import sleep
import pprint as pp

parser = argparse.ArgumentParser()
parser.add_argument('-u', type=str, nargs="?", dest="username")
parser.add_argument('-p', type=str, nargs="?", dest="password")
parser.add_argument('-b', type=str, nargs="?", dest="block")
args = parser.parse_args()


class Config():
    def __init__(self, args):
        self.username = args.username
        self.password = args.password

config = Config(args)

cli = Client()
profile = cli.login(config.username, config.password)

def bsky_get_followers_paginated(client:Client, user:str, config=None) -> list[str]:
    cursor = None
    followers = []

    while True:
        # Fetch the current page
        response = client.get_followers(actor=user, cursor=cursor, limit=100)
        dids = [f.did for f in response.followers]
        followers.extend(dids)

        cursor = response.cursor
        if not cursor:
            break
        sleep(0.1)

    return followers

followers = bsky_get_followers_paginated(cli, args.block)
for f in followers:
    cli.mute(actor=f)

cli.mute(args.block)
