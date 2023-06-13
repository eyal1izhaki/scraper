import threading
import re
import requests
import logging
import os


from .const import URL_REGEX


class Scraper:

    def __init__(self, url, level, max_per_page, uniqueness, saved_data_path) -> None:
        
        self._root_url = url
        self._level = level
        self._max_per_page = max_per_page
        self._uniqueness = uniqueness
        self._saved_data_path = saved_data_path

        self._threads = []
        self._result = []

    def _write_html_to_file(self, level, url):
        path = os.path.join(self._saved_data_path, str(level), )
        

    def _get_html(self, url: str) -> bytes:

        response = requests.get(url)
        return response.content

    def _scrape(self, url, level):

        logging.info(f"Scraping {url} at level {self._level - level}")

        if level == 0:
            return

        html = self._get_html(url)
        html_str = str(html)

        self._result.append(
            {
                "level": level,
                "data": html
            }
        )

        sub_urls = self._extract_urls(html_str, self._max_per_page)

        for sub_url in sub_urls:

            thread = threading.Thread(
                target=self._scrape, args=[sub_url, level-1])
            self._threads.append(thread)
            thread.start()

    # TODO: Optimize this
    def _extract_urls(self, html: str, first_n_occurrences):

        matches = re.findall(URL_REGEX, html)

        return matches[:first_n_occurrences]

    def scrape(self):

        main_thread = threading.Thread(target=self._scrape, args=[
                                       self._root_url, self._level])
        self._threads.append(main_thread)

        main_thread.start()

        for thread in self._threads:
            thread.join()
        
        self._threads = []
        result = self._result
        self._result = []

        return result
