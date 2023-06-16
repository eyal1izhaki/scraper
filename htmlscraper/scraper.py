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
        except ValueError:
            self._failed_files_saves_counter += 1
            logging.info(f"Failed to Write {url} to file {path}")
    
    async def _get_html(self, url: str):

        try:
            response = await async_get(
                url, verify=not self.ignore_ssl_verification, timeout=10)
            
            html = response.content
            self._pages_scraped_counter += 1
            logging.info(f"Scraped {url}.")
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

    async def _complete_scrape_task(self, url, depth, should_extract_urls=True):

        html, url = await self._get_html(url)

        if html is None:
            return []
        
        task = asyncio.create_task(self._write_html_to_file(html, url, depth))
        # await self._write_html_to_file(html, url, depth)

        if not should_extract_urls:
            return []
        
        extracted_urls = self._get_urls(url, html, self._scraping_width)

        await task

        return extracted_urls

    async def scrape(self):

        start = time.time()

        current_urls = []
        next_depth_urls = [self._root_url]
       
        depth = 0
        
        while True:

            if depth > self._scraping_depth:
                break

            should_extract_urls = depth < self._scraping_depth
            
            print(depth)

            current_urls = next_depth_urls
            next_depth_urls = []

            tasks = []
            for url in current_urls:

                task = asyncio.create_task(self._complete_scrape_task(url, depth, should_extract_urls))
                tasks.append(task)


            extracted_urls_arrays = await asyncio.gather(*tasks)
            
            next_depth_urls = [url for extracted_urls_array in extracted_urls_arrays for url in extracted_urls_array]

            depth += 1

        print(
            f"Scraped {self._pages_scraped_counter} websites. Failed to scrape {self._failed_scrapes_counter}. Wrote {self._files_saved_counter} files. Failed to save {self._failed_files_saves_counter}. Took {(time.time() - start)/self._pages_scraped_counter} per scrape")