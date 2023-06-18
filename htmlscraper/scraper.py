import os
import logging
import requests
import time
import asyncio
import urllib3.exceptions
import concurrent.futures
from typing import List, Awaitable

from .urls_extractors import SimpleAnchorHrefExtractor
from .utils import get_html_filename_from_url, async_get
from .exceptions import FailedToScrape


class Scraper:
    """Class the helps recursively scrape htmls pages"""

    def __init__(self, root_url: str, scraping_depth: int, scraping_width: int, unique_urls_only: bool, data_dir: str, ignore_ssl_verification=False) -> None:
        """constructor

        Args:
            root_url (str): URL to start the scraping from.
            scraping_depth (int): Max depth to scrape.
            scraping_width (int): Max urls to scrape per page.
            unique_urls_only (bool): Scrape unique URLs only
            data_dir (str): Destination to store scrape data
            ignore_ssl_verification (bool, optional): Ignore SSL verification when sending requests. Defaults to False.
        """

        self._root_url = root_url
        self._scraping_depth = scraping_depth
        self._scraping_width = scraping_width
        self._unique_urls_only = unique_urls_only

        self._data_dir = data_dir
        self.ignore_ssl_verification = ignore_ssl_verification

        self._scraped_htmls_counter = 0
        self._failed_files_writes_counter = 0
        self._files_writes_counter = 0
        self._failed_scrapes_counter = 0

        self._visited_urls = []  # For unique URLs functionality

    def _get_html_filename(self, url: str, depth: int) -> str:
        """get new filename used to write the scraped html content to a file.

        Args:
            url (str): URL of the scraped html.
            depth (int): Depth of the scraped html.

        Returns:
            str: Filename including full path for the given HTML
        """

        path = os.path.join(self._data_dir, str(
            depth), get_html_filename_from_url(url))

        return path

    def _write_html_to_file(self, html: bytes, url: str, depth: int) -> None:
        """Writes a given html to a file.

        Args:
            html (bytes): HTML content to write to a file.
            url (str): URL of the given HTML.
            depth (int): Depth the HTML scraped in.
        """

        path = self._get_html_filename(url, depth)

        dirname = os.path.dirname(path)
        # Creating missing parent directories
        os.makedirs(dirname, exist_ok=True)

        try:
            with open(path, 'wb') as file:
                file.write(html)

            self._files_writes_counter += 1
            logging.debug(f"Wrote {url} to file {path}")

        except OSError: # Failed probably due to filename too long
            self._failed_files_writes_counter += 1
            logging.debug(f"Failed to Write {url} to file {path}")

    async def _get_html(self, url: str) -> bytes | None:
        """Sends a GET request to a given url and returns the responded HTML.

        Args:
            url (str): URL to send the request to.

        Raises:
            FailedToScrape: Raised when async_get fails to get the requested HTML

        Returns:
            bytes: Scraped HTML or None when fails to scrape
        """
        try:
            response = await async_get(
                url, verify=not self.ignore_ssl_verification, timeout=10)

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout,
                requests.exceptions.TooManyRedirects, requests.exceptions.InvalidURL,
                requests.exceptions.MissingSchema, urllib3.exceptions.LocationParseError):

            logging.debug(f"Failed to scrape {url}.")
            self._failed_scrapes_counter += 1
            return None
    
        html = response.content
        self._scraped_htmls_counter += 1
        logging.debug(f"Scraped {url}.")
        return html


    def _get_urls(self, parent_url: str, html: bytes, first_n=-1) -> List[str]:
        """Extracts urls from a given HTML using URLExtractors

        Args:
            parent_url (str): The URL of the HTML to extract the links from.
            html (bytes): The HTML to extract the URLs from.
            first_n (int, optional): Limit the number of extracted urls. Defaults to -1.

        Returns:
            List[str]: List of extracted URLs
        """

        urls = SimpleAnchorHrefExtractor().extract(parent_url, str(html))

        if self._unique_urls_only == True:

            filtered_urls = []

            for url in urls:
                if url not in self._visited_urls:
                    self._visited_urls.append(url)
                    filtered_urls.append(url)

            return filtered_urls[:first_n]

        return urls[:first_n]

    async def _scrape_task(self, url: str, depth: int, should_extract_urls=True) -> List[str]:
        """Performs a complete scraping task. Gets the HTML, extract te URLs from it and Saves
        the HTML to the disk

        Args:
            url (str): URL to send get request to.
            depth (int): Depth in the scraping tree
            should_extract_urls (bool, optional): Should the method extract urls or just get an HTML and write it. Defaults to True.

        Returns:
            List[str]: List of extracted URLs
        """

        html = await self._get_html(url)

        if html is None:
            return []

        with concurrent.futures.ThreadPoolExecutor() as pool: # Performing writes in a different thread
            await asyncio.get_event_loop().run_in_executor(
                pool, self._write_html_to_file, html, url, depth)

        if not should_extract_urls:
            return []

        extracted_urls = self._get_urls(url, html, self._scraping_width)

        return extracted_urls

    async def start_scrape(self) -> None:
        """Start the scraping process"""

        start = time.time()

        current_urls = []
        next_depth_urls = [self._root_url]

        depth = 0

        while depth <= self._scraping_depth:

            logging.info(
                f"Scraping {len(next_depth_urls)} htmls at level {depth}")

            # TODO: Find more elegant way to perform this
            should_extract_urls = depth < self._scraping_depth

            current_urls = next_depth_urls
            next_depth_urls = []

            tasks = []
            for url in current_urls:
                task = asyncio.create_task(
                    self._scrape_task(url, depth, should_extract_urls))
                tasks.append(task)

            extracted_urls_arrays = await asyncio.gather(*tasks)

            next_depth_urls = [
                url for extracted_urls_array in extracted_urls_arrays for url in extracted_urls_array]

            depth += 1

        logging.info(
            f"Scraped {self._scraped_htmls_counter} websites. Failed to scrape {self._failed_scrapes_counter}. Wrote {self._files_writes_counter} files. Failed to save {self._failed_files_writes_counter}. Took {(time.time() - start)/self._scraped_htmls_counter} per scrape")
