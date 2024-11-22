from atproto import Client, AtUri
import argparse
from collections import defaultdict
from time import sleep
import pprint as pp

parser = argparse.ArgumentParser()
parser.add_argument('-u', type=str, nargs="?", dest="username")
parser.add_argument('-p', type=str, nargs="?", dest="password")
parser.add_argument('-post', type=str, nargs="?", dest="post")
args = parser.parse_args()


class Config():
    def __init__(self, args):
        self.username = args.username
        self.password = args.password

config = Config(args)

cli = Client()
profile = cli.login(config.username, config.password)

def get_likes(client:Client, at_uri:str, config=None) -> list[str]:
    cursor = None
    likers = []

    while True:
        response = client.get_likes(uri=at_uri, cursor=cursor, limit=100)
        likes = [l.actor.did for l in response.likes]
        likers.extend(likes)

        cursor = response.cursor
        if not cursor:
            break
        sleep(0.1)

    return likers

likers = get_likes(cli, args.post)
for f in followers:
    cli.mute(actor=f)

# mute author of post too
