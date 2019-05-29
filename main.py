import json
import praw
import re
import time


reddit = praw.Reddit('FlagBot')

with open('countries.json', encoding='utf-8') as f:
    temp = json.load(f)
    glos = dict()
    for k, v in temp.items():
        glos[k.lower()] = v


def link(country):
    return f'[{country}]({glos[country.lower()]})'


def commentReply(body):
    """This implies that the body definitely starts with '!flag'"""
    devname = '[\/u\/TuttleStripes](https://www.reddit.com/user/TuttleStripes)'
    countries = re.split(r', ?', body[6:])
    hits = set()
    misses = set()
    for i in countries:
        try:
            hits.add(link(i))
        except KeyError:
            misses.add(i)
    
    reply = f'Flag of{":" * (len(hits) > 1)} {", ".join(sorted(hits))}' * bool(hits)
    if misses:
        reply += f'\n\nCountr{"y" if len(misses) == 1 else "ies"} missed: {", ".join(misses)}. Go yell at {devname}'
    reply += f'\n\n---\n\n^Send ^all ^requests ^and ^complaints ^to ^{devname}. ^Source ^code ^can ^be ^found ^[here](https://github.com/TuttleStripes/flagbot).'
    return reply


if __name__ == '__main__':
    while True:
        sub = reddit.subreddit('vexillology')
        time.sleep(5)
        try:
            for comment in sub.stream.comments():
                body = comment.body
                if body.startswith('!flag') and comment.author.name != 'FlaggyMcFlaggerson':
                    try:
                        comment.reply(commentReply(body))
                        comment.upvote()
                    except Exception as e:
                        print('Respond error:')
                        print(e)
        except Exception as e:
            print(e)
