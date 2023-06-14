import os
import logging
import requests
from typing import List
from requests_html import AsyncHTMLSession
import time
import asyncio
import aiofiles
from .url_extractors import SimpleAnchorHrefExtractor
from .utils import get_html_filename_from_url

class Scraper:

    def __init__(self, url: str, scraping_depth: int, scraping_width: int, unique_urls_only: bool, data_dir: str, ignore_ssl_verification=False, loop=None) -> None:

        self._root_url = url
        self._scraping_depth = scraping_depth
        self._scraping_width = scraping_width
        self._unique_urls_only = unique_urls_only

        self._data_dir = data_dir
        self.ignore_ssl_verification = ignore_ssl_verification

        self._loop = asyncio.get_event_loop()

        self._pages_scraped_counter = 0
        self._failed_files_saves_counter = 0
        self._files_saved_counter = 0
        self._failed_scrapes_counter = 0

        self._scraped_urls = []  # For unique urls functionality


    def _get_html_filename(self, url: str, depth):

        path = os.path.join(self._data_dir, str(
            depth), get_html_filename_from_url(url))
         
        return path

    async def _write_html_to_file(self, html: bytes, url: str, depth: int):
        
        path = self._get_html_filename(url, depth)

        dirname = os.path.dirname(path) 
        os.makedirs(dirname, exist_ok=True) # Creating missing parent directories

        try:
            async with aiofiles.open(path, 'wb') as html_file:
                await html_file.write(html)
                self._files_saved_counter += 1

            logging.info(f"Wrote {url} to file {path}")
        except:
            self._failed_files_saves_counter += 1
            logging.info(f"Failed to Write {url} to file {path}")
    
    async def _get_html(self, url: str):
       
        try:
            response = await AsyncHTMLSession().get(
                url, verify=not self.ignore_ssl_verification, timeout=10)

            html = response.content
            self._scraped_urls.append(url)
            self._pages_scraped_counter += 1
            return html

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            logging.info(f"Failed to scrape {url}.")
            self._failed_scrapes_counter += 1

            return None

    def _extract_urls(self, html: bytes, first_n=-1):

        urls = []

        for url_extractor in self._url_extractors:
            urls += url_extractor().extract_urls(str(html), first_n)

        return urls

    async def scrape(self):

        start = time.time()

        current_depth_htmls = []
        next_depth_htmls = []  # A list that will hold only one level for htmls in the depth


        url = self._root_url
        response = await AsyncHTMLSession().get(url)
        root_html = response.content
        self._pages_scraped_counter += 1

        next_depth_htmls.append(root_html)

        depth = 1
        while True:

            if depth > self._scraping_depth:
                break
            
            current_depth_htmls = next_depth_htmls
            next_depth_htmls = []

            tasks = []

            for html in current_depth_htmls:

                if html is None:
                    continue

                await self._write_html_to_file(html, url, depth)
                
                urls = []

                if self._unique_urls_only == True:
                    urls = SimpleAnchorHrefExtractor().extract_urls(str(html), self._scraping_width, self._scraped_urls)

                else:
                    urls = SimpleAnchorHrefExtractor().extract_urls(str(html), self._scraping_width)

                for url in urls:
                    tasks.append(self._get_html(url))
                    logging.info(f"Scraped {url} at depth {depth}")


            next_depth_htmls = await asyncio.gather(*tasks)
            depth += 1

        logging.info(
            f"Scraped {self._pages_scraped_counter} websites. Failed to scrape {self._failed_scrapes_counter}. Wrote {self._files_saved_counter} files. Failed to save {self._failed_files_saves_counter}. Took {(time.time() - start)/self._pages_scraped_counter} per scrape")