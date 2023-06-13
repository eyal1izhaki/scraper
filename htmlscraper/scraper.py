import threading
import re
import requests
import logging
import os

from .const import URL_REGEX
from .utils import get_html_filename_from_url


class Scraper:

    def __init__(self, url, max_depth, max_per_page, uniqueness, saved_data_path, url_extractors, ignore_ssl_verification=False) -> None:
        
        self._root_url = url
        self._max_depth = max_depth
        self._max_per_page = max_per_page
        self._uniqueness = uniqueness
        self._saved_data_path = saved_data_path
        self._url_extractors = url_extractors
        self.ignore_ssl_verification = ignore_ssl_verification

        self._threads = []
        self._result = []

    def _write_html_to_file(self, html, depth, url):

        path = os.path.join(self._saved_data_path, str(depth), get_html_filename_from_url(url))
        dirname = os.path.dirname(path)

        os.makedirs(dirname, exist_ok=True)

        with open(path, 'wb') as html_file:
            logging.info(f"Writing {url} to file {path}")
            html_file.write(html)

    def _get_html(self, url: str) -> bytes:

        response = requests.get(url, verify=self.ignore_ssl_verification)
        return response.content

    def _scrape(self, url, depth):

        logging.info(f"Scraping {url} at depth {depth}")

        if depth == self._max_depth:
            return

        # TODO: Arguments order not consistent
        html = self._get_html(url)
        self._write_html_to_file(html, depth, url)
        html_str = str(html)

        self._result.append(
            {
                "depth": depth,
                "data": html
            }
        )

        sub_urls = self._extract_urls(html_str, self._max_per_page)

        for sub_url in sub_urls:

            thread = threading.Thread(
                target=self._scrape, args=[sub_url, depth+1])
            self._threads.append(thread)
            thread.start()

    def _extract_urls(self, html: str, first_n):

        urls = []

        for url_extractor in self._url_extractors:
            urls += url_extractor().extract_urls(html, first_n)

        return urls

    def scrape(self):

        main_thread = threading.Thread(target=self._scrape, args=[
                                       self._root_url, 0])
        self._threads.append(main_thread)

        main_thread.start()

        for thread in self._threads:
            thread.join()
        
        self._threads = []
        result = self._result
        self._result = []

        return result
