import os
import logging
import requests
import time
import asyncio
import urllib3.exceptions

from .urls_extractors import SimpleAnchorHrefExtractor
from .utils import get_html_filename_from_url, async_get, async_write_to_file

class Scraper:

    def __init__(self, url: str, scraping_depth: int, scraping_width: int, unique_urls_only: bool, data_dir: str, ignore_ssl_verification=False) -> None:

        self._root_url = url
        self._scraping_depth = scraping_depth
        self._scraping_width = scraping_width
        self._unique_urls_only = unique_urls_only

        self._data_dir = data_dir
        self.ignore_ssl_verification = ignore_ssl_verification

        self._pages_scraped_counter = 0
        self._failed_files_saves_counter = 0
        self._files_saved_counter = 0
        self._failed_scrapes_counter = 0

        self._visited_urls = []  # For unique urls functionality


    def _get_html_filename(self, url: str, depth):

        path = os.path.join(self._data_dir, str(
            depth), get_html_filename_from_url(url))
         
        return path

    async def _write_html_to_file(self, html: bytes, url: str, depth: int):

        path = self._get_html_filename(url, depth)

        dirname = os.path.dirname(path) 
        os.makedirs(dirname, exist_ok=True) # Creating missing parent directories

        try:    
            await async_write_to_file(path, html)
            self._files_saved_counter += 1
            logging.info(f"Wrote {url} to file {path}")
        except:
            self._failed_files_saves_counter += 1
            logging.info(f"Failed to Write {url} to file {path}")
    
    async def _get_html(self, url: str):

        try:
            response = await async_get(
                url, verify=not self.ignore_ssl_verification, timeout=10)
            
            html = response.content
            self._pages_scraped_counter += 1
            return html, url

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.TooManyRedirects, requests.exceptions.InvalidURL, requests.exceptions.MissingSchema, urllib3.exceptions.LocationParseError):
            logging.info(f"Failed to scrape {url}.")
            self._failed_scrapes_counter += 1

            return None, None

    def _get_urls(self, parent_url, html, first_n=-1):
        
        if self._unique_urls_only == True:
            result = []
            urls = SimpleAnchorHrefExtractor().extract(parent_url, str(html))
            
            for url in urls:
                
                if url not in self._visited_urls:
                    self._visited_urls.append(url)
                    result.append(url)
        else:
            result = SimpleAnchorHrefExtractor().extract(parent_url, str(html))

        return result[:first_n]

    async def scrape(self):

        start = time.time()

        current_depth_htmls = []
        next_depth_htmls = []  # A list that will hold only one level for htmls in the depth

        url = self._root_url
        root_html, root_url = await self._get_html(url)
        self._visited_urls.append(url)
        asyncio.create_task(self._write_html_to_file(root_html, url, 0))

        next_depth_htmls.append((root_html, root_url))

        depth = 1
        disk_tasks = []
        while True:

            if depth > self._scraping_depth:
                break
            
            print(depth)

            current_depth_htmls = next_depth_htmls
            next_depth_htmls = []

            network_tasks = []
            for html, parent_url in current_depth_htmls:

                if html is None:
                    continue

                urls = self._get_urls(parent_url, html, self._scraping_width)

                for url in urls:
                    network_task = asyncio.create_task(self._get_html(url))
                    network_tasks.append(network_task)
                    logging.info(f"Scraped {url} at depth {depth}")


            next_depth_htmls = await asyncio.gather(*network_tasks)

            for html, url in next_depth_htmls:

                if html is None:
                    continue

                disk_task = asyncio.create_task(self._write_html_to_file(html, url, depth))
                disk_tasks.append(disk_task)
            
            depth += 1

        for task in disk_tasks:
            await task

        print(
            f"Scraped {self._pages_scraped_counter} websites. Failed to scrape {self._failed_scrapes_counter}. Wrote {self._files_saved_counter} files. Failed to save {self._failed_files_saves_counter}. Took {(time.time() - start)/self._pages_scraped_counter} per scrape")