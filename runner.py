from htmlscraper.scraper import Scraper
from htmlscraper.urls_extractors import SimpleAnchorHrefExtractor
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
# from htmlscraper.scraper2 import Scraper
from htmlscraper.scraper import Scraper
# from htmlscraper.scraper_threads import Scraper
import asyncio
from requests_html import AsyncHTMLSession

import time

# Disable SSL verification
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# logging.basicConfig(level=logging.INFO)

# scraper = Scraper('https://www.ynetnews.com/', scraping_depth=7, scraping_width=3, unique_urls_only=True,
#                   data_dir='C:/Users/eyal1izhaki/Documents/code/scraper-task/scraped_data',
#                   url_extractors=[SimpleAnchorHrefExtractor], ignore_ssl_verification=False)

# scraper.scrape_to_fs()

scraper = Scraper('https://www.ynetnews.com/', scraping_depth=4, scraping_width=8, unique_urls_only=True,
                  data_dir='C:/Users/eyal1izhaki/Documents/code/scraper-task/scraped_data', ignore_ssl_verification=True)




if __name__ == "__main__":
    
    start = time.time()
    try:
        asyncio.run(scraper.scrape())

    except KeyboardInterrupt:
        print(f"Ctrl C Pressed took {time.time - start}")