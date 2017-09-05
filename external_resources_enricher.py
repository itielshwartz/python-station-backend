import json
import logging
from urllib.parse import urlsplit

import arrow as arrow
from tqdm import tqdm

from requests_utils import download_github_repo_data, get_trending_on_github, get_hn_mention, HN_FOR_HUMAN_SEARCH_QUERY, \
    get_reddit_mention, REDDIT_SEARCH_FOR_HUMAN


def enrich_github_projects(input_file, output_file):
    with open(input_file) as f:
        raw_github_projects = json.load(f)
    github_projects = enrich_and_filter_using_github(raw_github_projects)
    add_clean_fields(github_projects)
    add_is_trending_to_projects(github_projects)
    add_was_on_hn_to_projects(github_projects)
    add_was_on_reddit_to_projects(github_projects)
    with open(output_file, "w+") as f:
        json.dump(list(github_projects.values()), f, indent=4)


def enrich_and_filter_using_github(github_projects):
    valid_github_projects = {}
    for project_url, project_data in tqdm(github_projects.items()):
        try:
            owner, name = project_data["owner"], project_data["name"]
            resp = download_github_repo_data(param=(owner + "/" + name))
            if resp and resp.get("language") == 'Python':  # I want only python repos
                project_data["starts"] = resp["stargazers_count"]
                project_data["last_update"] = resp["updated_at"]
                project_data["description"] = resp["description"]
                project_data["forks"] = resp["forks"]
                valid_github_projects[project_url] = project_data
        except Exception as e:
            logging.exception(e)
    return valid_github_projects


def add_clean_fields(github_projects):
    for project_url, project_data in github_projects.items():
        project_data["clean_last_update"] = arrow.get(project_data["last_update"]).format("YYYY-MM-DD")
        project_data["clean_last_mention"] = arrow.get(project_data["last_mention"]).format("YYYY-MM-DD")
        project_data["mention_count"] = len(set((get_base_url(url) for url in project_data["blogs_ref"])))
        project_data["full_name"] = project_data["owner"] + "/" + project_data["name"]


def add_is_trending_to_projects(github_projects):
    trending_on_github = get_trending_on_github()
    for project_url, project_data in tqdm(github_projects.items()):
        if project_data["full_name"] in trending_on_github:
            print(project_data["full_name"])
            project_data["trending_link"] = trending_on_github[project_data["full_name"]]


def add_was_on_hn_to_projects(github_projects):
    for project_url, project_data in tqdm(github_projects.items()):
        hn_mention = get_hn_mention(param=project_data["full_name"])
        if hn_mention["hits"]:
            project_data["hn_query"] = HN_FOR_HUMAN_SEARCH_QUERY.format(project_data["full_name"])


def add_was_on_reddit_to_projects(github_projects):
    for project_url, project_data in tqdm(github_projects.items()):
        redit_mention = get_reddit_mention(param=project_data["full_name"])
        if redit_mention:
            project_data["reddit_query"] = REDDIT_SEARCH_FOR_HUMAN.format(project_data["full_name"])


def get_base_url(url):
    return "{0.scheme}://{0.netloc}/".format(urlsplit(url))
