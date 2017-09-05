import json
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

time_units = "years", 'year', "months", 'month', "weeks", "week", "days", "day", "hours", "hour", "minutes", "seconds"
time_unit_dict = {"hour": "hours", "day": "days", 'week': 'weeks','month':'months','year':'years'}
BAD_DATE_CHRS = ["(", ")"]
BASE_GITHUB_PROJECT_URL = "https://github.com/{}/{}/"


def transform_pages_into_posts(input_file, output_file):
    posts = []
    with open(input_file) as f:
        pages = [json.loads(line) for line in f]  # load all pages
    for page in tqdm(pages):  # Iterate over all of the the pages in the site
        soup = BeautifulSoup(page, 'html.parser')
        page_posts = soup.find_all("div", class_="item")
        for raw_post in page_posts:  # Iterate over all posts in a single page
            clean_post = raw_post_to_clean_post(raw_post)  # Clean the post
            if clean_post:
                posts.append(clean_post)
    with open(output_file, "w+") as f:  # save output
        json.dump(posts, f, sort_keys=True, indent=4)


def raw_post_to_clean_post(item):
    try:
        parsed_post = {}
        parsed_post.update(extract_post_time_and_name(item))
        parsed_post.update(extract_github_urls_in_posts(item))
        return parsed_post
    except Exception as e:
        logging.exception(e)
        return None


def extract_href_name_and_url(href_raw):
    return href_raw.text, href_raw.get("href")


def parse_github_url(url):
    try:
        raw_owner_and_name = url.split("github.com/")[1]
        owner, name = raw_owner_and_name.split("/", 2)[:2]
        project_url = BASE_GITHUB_PROJECT_URL.format(owner, name)
    except Exception as e:
        return None, None, None
    return owner, name, project_url


def extract_post_time_and_name(item):
    post_data = {}
    title_data_raw = item.find("h2")
    raw_time = title_data_raw.find("span").text
    raw_time = clean_raw_time(raw_time)
    time_delta = string_time_to_timedelta_dict(raw_time)
    post_data["created"] = (datetime.utcnow() - relativedelta(**time_delta)).isoformat()
    h = title_data_raw.find(href=True)
    post_data["name"], post_data["url"] = extract_href_name_and_url(h)
    return post_data


def clean_raw_time(raw_time):
    for c in BAD_DATE_CHRS:
        raw_time = raw_time.replace(c, "")
    return raw_time


def string_time_to_timedelta_dict(raw_time):
    time_delta = {}
    for raw_time_unit in raw_time.split(","):
        for aviablite_time_unit in time_units:
            if aviablite_time_unit in raw_time_unit:
                key = time_unit_dict.get(aviablite_time_unit, aviablite_time_unit)
                time_delta[key] = int(raw_time_unit.split(aviablite_time_unit)[0].strip())
    return time_delta


def extract_github_urls_in_posts(item):
    post_data = {"out_urls": {}}
    main_post_raw = item.find("div", class_="summary")
    if main_post_raw:
        for raw_href in main_post_raw.find_all(href=True):
            url_title, url = extract_href_name_and_url(raw_href)
            if "github.com/" in url:
                project_owner, project_name, project_url = parse_github_url(url)
                if project_owner and not project_url in post_data.get("out_urls"):
                    post_data["out_urls"][project_url] = {"url_title": url_title, "link_in_blog": url,
                                                          "owner": project_owner,
                                                          "name": project_name,
                                                          "project_url": project_url}
    return post_data
