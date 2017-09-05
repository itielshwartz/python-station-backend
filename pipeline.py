import logging
import os

import click as click

from download_planet_python import download_posts
from external_resources_enricher import enrich_github_projects
from extract_projects_from_posts import extract_github_projects_from_posts
from pages_into_posts import transform_pages_into_posts

FILE_NAME_RAW_PAGES = "step_0_planet_python_raw_pages.jl"
FILE_NAME_RAW_POSTS = "step_1_posts.json"
FILE_NAME_RAW_GITHUB_PROJECTS = "step_2_raw_github_projects.json"
FILE_NAME_FINAL_PROJECT = "step_3_final.json"

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--pages-to-download', default=500, help='Number of pages to download - use 0 for all')
@click.option('--files-prefix', default="", help='The prefix for pipeline files')
@click.option('--pipeline-steps-dir', default="pipeline_data", help='The dir for local files in the pipeline')
def main(pages_to_download, files_prefix, pipeline_steps_dir):
    file_for_pipeline_output, file_for_posts, file_for_raw_github_projects, file_for_raw_pages = init_files_url(
        files_prefix, pipeline_steps_dir)
    logging.info("Starting to download pages")
    download_posts(output_file=file_for_raw_pages, max_page_to_download=pages_to_download)
    logging.info("Starting to transform pages into posts")
    transform_pages_into_posts(input_file=file_for_raw_pages, output_file=file_for_posts)
    logging.info("Starting to extract github projects from posts")
    extract_github_projects_from_posts(input_file=file_for_posts, output_file=file_for_raw_github_projects)
    logging.info("Starting to enrich repos")
    enrich_github_projects(input_file=file_for_raw_github_projects, output_file=file_for_pipeline_output)
    logging.info("Finished")


def init_files_url(files_prefix, pipeline_steps_dir):
    file_for_raw_pages = get_file_url(FILE_NAME_RAW_PAGES, files_prefix, pipeline_steps_dir)
    file_for_posts = get_file_url(FILE_NAME_RAW_POSTS, files_prefix, pipeline_steps_dir)
    file_for_raw_github_projects = get_file_url(FILE_NAME_RAW_GITHUB_PROJECTS, files_prefix, pipeline_steps_dir)
    file_for_pipeline_output = get_file_url(FILE_NAME_FINAL_PROJECT, files_prefix, pipeline_steps_dir)
    return file_for_pipeline_output, file_for_posts, file_for_raw_github_projects, file_for_raw_pages


def get_file_url(file_name, files_prefix, cache_dir):
    file_name = files_prefix + "-" + file_name if files_prefix else file_name
    return os.path.join(cache_dir, file_name)


if __name__ == '__main__':
    main()
