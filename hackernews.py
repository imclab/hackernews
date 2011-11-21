#!/usr/bin/env python

import argparse, re, requests
from pyquery import PyQuery as pq


def _login(args):
    """Log in to Hacker News and return the cookies."""

    r = requests.get('https://news.ycombinator.com/newslogin')
    J = pq(r.content)

    fnid = J('input[name="fnid"]').val()

    payload = {
        'fnid': fnid,
        'u': args.username,
        'p': args.password,
    }

    r = requests.post('https://news.ycombinator.com/y', data=payload)

    return r.cookies

def _get_saved_stories(args, r=None, saved=None):
    """Returns a sorted list of the user's saved stories."""

    if r is None:
        cookies = _login(args)
        r = requests.get('http://news.ycombinator.com/saved?id=%s' % args.username, cookies=cookies)
        saved = []
    else:
        cookies = r.cookies

    J = pq(r.content)
    stories = J('table table td.title')

    for story in stories:
        title = J(story).text()
        if not re.match('\d+\.|More', title):

            url = J('a', story).attr('href')

            if not url.startswith('http'):
                url = 'https://news.ycombinator.com/' + url

            saved.append({
                'title': title,
                'url': url,
            })

    if args.all:
        last = J('a', J('table table tr td.title:last'))
        if last.text() == 'More':
            r = requests.get('https://news.ycombinator.com%s' % last.attr('href'), cookies=cookies)
            _get_saved_stories(args, r=r, saved=saved)

    return saved

def saved(args):
    """Returns a formatted list of the logged-in user's saved stories."""

    stories = _get_saved_stories(args)
    print stories

    return ''

# Parser
parser = argparse.ArgumentParser(prog='Hacker News')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
subparsers = parser.add_subparsers()

# Subparsers
saved_parser = subparsers.add_parser('saved')
saved_parser.add_argument('-u', '--username', dest='username', help='HN Username', required=True)
saved_parser.add_argument('-p', '--password', dest='password', help='HN Password', required=True)
saved_parser.add_argument('--all', dest='all', help='Get all saved stories?', action='store_true')
saved_parser.set_defaults(func=saved)

# Args
args = parser.parse_args()
args.func(args)