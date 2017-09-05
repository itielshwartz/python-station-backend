import requests
from bs4 import BeautifulSoup

HN_SEARCH_QUERY = "http://hn.algolia.com/api/v1/search?query={}"
HN_FOR_HUMAN_SEARCH_QUERY = "https://hn.algolia.com/?query={}&sort=byPopularity&prefix=false&page=0&dateRange=all&type=all"
REDDIT_SEARCH_QUERY = "https://www.reddit.com/search.json?q={}"
REDDIT_SEARCH_FOR_HUMAN = "https://www.reddit.com/r/search/search?q={}"
BASE_TRENDING_URL = "https://github.com/trending/python?since={}"
trending_times = ["daily", "weekly", "monthly"]

import os, json

import praw

REDDIT_CLIENT_ID = None
REDDIT_CLIENT_SECRET = None
REDDIT_USER_AGENT = None

if REDDIT_CLIENT_SECRET:
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         user_agent=REDDIT_USER_AGENT)
else:
    reddit = None

GITHUB_API_TOKEN = None


def requests_with_cache(dir):
    def decorator(func):
        def wrapper(**kwargs):
            cache_key = str(kwargs.get("param", "default.json"))
            cache_url = dir + "/" + cache_key.replace("/", "-").replace("_", "-")
            if os.path.isfile(cache_url):
                with open(cache_url, 'r') as f:
                    print(cache_url)
                    return json.load(f)
            with open(cache_url, 'w+') as f:
                ret = func(**kwargs)
                json.dump(ret, f)
                return ret

        return wrapper

    return decorator


@requests_with_cache("github_trending_cache")
def get_trending_on_github():
    trending_on_python = {}
    for trending_time in trending_times:
        trend_url = BASE_TRENDING_URL.format(trending_time)
        trending_on_python[trend_url] = []
        r = requests.get(trend_url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        all_h3 = soup.find_all("h3")
        for h3 in all_h3:
            link = h3.find(href=True).get("href")
            trending_on_python[link.split("/", 1)[1]] = trend_url
    return trending_on_python


@requests_with_cache("github_cache")
def download_github_repo_data(param):
    owner, name = param.split("/")
    url = "https://api.github.com/repos/{}/{}".format(owner, name)
    headers = {'Authorization': 'token %s' % GITHUB_API_TOKEN} if GITHUB_API_TOKEN else None
    r = requests.get(url, headers=headers)
    return r.json()


@requests_with_cache("reddit_cache")
def get_reddit_mention(param):
    if reddit:
        has_match = bool(reddit.get("search.json?q={}".format(param)).children)
        return has_match


@requests_with_cache("hn_cache")
def get_hn_mention(param, url=HN_SEARCH_QUERY):
    url = HN_SEARCH_QUERY.format(param)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()
