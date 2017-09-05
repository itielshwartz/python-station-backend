import json


def extract_github_projects_from_posts(input_file, output_file):
    with open(input_file) as f:
        data = json.load(f)
    extracted_github_projects = {}
    for post in data:
        for project_url, project_data in post.get("out_urls").items():  # get all links on page
            project_aggregated_data = extracted_github_projects.get(project_url,
                                                                    project_data)  # check to see if we already saw this repo
            project_aggregated_data["last_mention"] = max(project_aggregated_data.get("last_mention", ""),
                                                          post["created"])  # find the latest mention on the repo
            project_aggregated_data["blogs_ref"] = project_aggregated_data.get("blogs_ref", []) + [
                post["url"]]  # update ref
            extracted_github_projects[project_url] = project_aggregated_data
    with open(output_file, "w+") as f:
        json.dump(extracted_github_projects, f, sort_keys=True, indent=4)
