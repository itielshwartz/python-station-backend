import itertools
import json
import logging
from time import sleep

import requests
from urllib3.exceptions import InsecureRequestWarning

BASE_URL = "https://aggape.de/feeds/view/53/?page={}"
UNVALID_PAGE_INDICATOR = "Guru Meditation"
should_stop_page = lambda page: UNVALID_PAGE_INDICATOR in page
logging.basicConfig(level=logging.INFO)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def download_posts(output_file, max_page_to_download=None):
    with open(output_file, "w") as f:  # open the output file
        pages_to_download_itr = range(1, max_page_to_download + 1) if max_page_to_download else itertools.count(1)
        for i in pages_to_download_itr:  # start itrate over the pages
            url = BASE_URL.format(i)
            logging.info("fetching %s", format(url))
            page_data = download_with_retry(url)
            if should_stop_page(page_data):  # validate it's not the last page
                return logging.info("Finished Downloading all data")
            f.write(json.dumps(page_data) + "\n")  # write page as jsonline
            logging.info("finished %s", format(url))


def download_with_retry(url):
    for sleep_time in itertools.count():
        page_data_raw = requests.get(url, verify=False)  # get the page
        page_data = page_data_raw.text
        if page_data_raw.status_code == 200 or should_stop_page(page_data):
            return page_data
        sleep(sleep_time)  # sleep in case bad response
