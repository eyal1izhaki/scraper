import logging
import requests
import asyncio
import time
import json

from htmlscraper.scraper import Scraper
from htmlscraper.urls_extractors import SimpleAnchorHrefExtractor
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from htmlscraper.scraper import Scraper



# Disable warnings about insecure requests when ignore_ssl_verification is set to true
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


with open('config.json') as config_file:
    config = json.loads(config_file.read())

scraper = Scraper('https://www.ynetnews.com/', scraping_depth=4, scraping_width=8, unique_urls_only=True,
                  data_dir=config["data_dir"], ignore_ssl_verification=True)


if __name__ == "__main__":
    
    start = time.time()
    try:
        asyncio.run(scraper.scrape())

    except KeyboardInterrupt:
        print(f"Ctrl C Pressed took {time.time - start}")