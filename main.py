import json
import praw
import os
import re
import requests
import time


try:
    reddit = praw.Reddit(client_id=os.environ['CLIENT_ID'],
                        client_secret=os.environ['CLIENT_SECRET'],
                        password=os.environ['REDDIT_PASS'],
                        username=os.environ['REDDIT_USER'],
                        user_agent=os.environ['USER_AGENT'])
except:
    reddit = praw.Reddit('FlagBot')

with open('countries.json', encoding='utf-8') as f:
    temp = json.load(f)
    glos = dict()
    for k, v in temp.items():
        glos[k.lower()] = v


def link(country, url=None):
    if url is None:
        return f'[{country}]({glos[country.lower()]})'
    else:
        return f'[{country}]({url})'


def commentReply(body):
    """This implies that the body definitely starts with '!flag'"""
    devname = '[\/u\/TuttleStripes](https://www.reddit.com/user/TuttleStripes)'
    countries = re.split(r', ?', body[6:])
    hits = []
    misses = []
    for i in countries:
        try:
            hits.append(link(i))
        except KeyError:
            the = requests.get(f'https://en.wikipedia.org/wiki/Flag_of_the_{i}')
            nothe = requests.get(f'https://en.wikipedia.org/wiki/Flag_of_{i}')
            if the.status_code != 404:
                hits.append(link(i, url=the.url))
            elif nothe.status_code != 404:
                hits.append(link(i, url=nothe.url))
            else:
                misses.append(i)
    
    reply = f'Flag of{":" * (len(hits) > 1)} {", ".join(hits)}' * bool(hits)
    if misses:
        reply += f'\n\nCountr{"y" if len(misses) == 1 else "ies"} missed: {", ".join(misses)}. Go yell at /u/TuttleStripes'
    reply += f'\n\n---\n\n^Send ^all ^requests ^and ^complaints ^to ^{devname}. ^Source ^code ^can ^be ^found ^[here](https://github.com/TuttleStripes/flagbot).'
    return reply


if __name__ == '__main__':  
    while True:
        sub = reddit.subreddit('vexillology')
        time.sleep(5)
        try:
            for comment in sub.stream.comments():
                body = comment.body
                if body.startswith('!flag') and not comment.saved:
                    try:
                        comment.reply(commentReply(body))
                        comment.save()
                    except Exception as e:
                        print('Respond error:')
                        print(e)
        except Exception as e:
            print(e)
