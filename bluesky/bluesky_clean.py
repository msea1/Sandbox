from atproto import Client, AtUri
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument('-u', type=str, nargs="?", dest="username")
parser.add_argument('-p', type=str, nargs="?", dest="password")
args = parser.parse_args()


class Config():
    def __init__(self, args):
        self.days_to_keep = {"posts": 7, "reposts": 7}
        self.username = args.username
        self.password = args.password

config = Config(args)

cli = Client()
profile = cli.login(config.username, config.password)

def paginated_list_records(cli, repo, collection):
    params = {"repo": repo, "collection": collection, "limit": 100}
    records = []

    while True:
        resp = cli.com.atproto.repo.list_records(params)
        records.extend(resp.records)
        if resp.cursor:
            params["cursor"] = resp.cursor
        else:
            break

    return records

now = datetime.now(timezone.utc)

post_delta = timedelta(days=config.days_to_keep["posts"])
post_hold_datetime = now - post_delta

repost_delta = timedelta(days=config.days_to_keep["reposts"])
repost_hold_datetime = now - repost_delta

records = {}
for collection in ["app.bsky.feed.post", "app.bsky.feed.repost"]:
    records[collection] = paginated_list_records(cli, config.username, collection)
    print(f"{collection}: {len(records[collection])}")


deletes = []
for collection, posts in records.items():
    if collection == "app.bsky.feed.post":
        hold_datetime = post_hold_datetime
    elif collection == "app.bsky.feed.repost":
        hold_datetime = repost_hold_datetime
    else:
        break

    for post in reversed(posts):
        # remove charactors on `created_at` behind of `Z`
        z_index_in_created_at = post.value.created_at.index('Z')
        post_created_at = datetime.fromisoformat(post.value.created_at[:z_index_in_created_at+1])
        if post_created_at <= hold_datetime:
            uri = AtUri.from_str(post.uri)
            deletes.append({
                "$type": "com.atproto.repo.applyWrites#delete",
                "rkey": uri.rkey,
                "collection": collection,
            })
        else:
           pass 


print(f'{datetime.now()} COMMENCE DELETE: {len(deletes)} posts/reposts')
if len(deletes) > 0:
    for i in range(0, len(deletes), 200):
        cli.com.atproto.repo.apply_writes({"repo": config.username, "writes": deletes[i:i+200]})
print(f'{datetime.now()} DELETE COMPLETED')