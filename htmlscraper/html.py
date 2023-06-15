import asyncio
import os
from typing import List
import logging
import requests
import urllib3

from .exceptions import MissingContent
from .utils import async_get, async_write_to_file
from .urls_extractors import SimpleAnchorHrefExtractor
from .utils import generate_filename_from_url

class ScrapedHTML:

    def __init__(self, url, depth, urls_extractors=[SimpleAnchorHrefExtractor], loop=None) -> None:
        
        self._url = url
        self._depth = depth
        self._loop = loop or asyncio.get_event_loop()
        self._urls_extractors = urls_extractors
        self._raw_content = None

    @property
    def url(self) -> str:
        return self._url
    
    @property
    def raw_content(self) -> bytes:

        if self._raw_content is None:
            MissingContent() # TODO: Add readable error message

        return self._raw_content
    
    @property
    def content(self) -> str:

        if self._raw_content is None:
            MissingContent() # TODO: Add readable error message

        return str(self._raw_content)
    
    @property
    def links(self) -> List[str]:
        return self._extract_links()
    
    def _generate_html_path(self, data_dir):
        # TODO: Should data_dir be passed as an argument?
        filename = generate_filename_from_url(self._url)
        path = os.path.join(data_dir, str(self._depth), filename)
        return path

    async def retrieve_data(self, ignore_ssl_verification=False, timeout=10):

        self._raw_content = None # In case retrieve_data is being called more that one
        try:
            response = await async_get(self._url, verify=not ignore_ssl_verification, timeout=timeout)
        
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.TooManyRedirects, requests.exceptions.InvalidURL, requests.exceptions.MissingSchema, urllib3.exceptions.LocationParseError):
            
            return None
        
        self._raw_content = response.content

        self.save_as_file_task('')

        # TODO: Is there any use with the returned data?
        return self._raw_content

    def retrieve_data_task(self, ignore_ssl_verification=False, timeout=10):
        return asyncio.create_task(self.retrieve_data(ignore_ssl_verification=ignore_ssl_verification, timeout=timeout))

    async def save_as_file(self, save_to):
        
        if self._raw_content is None:
            MissingContent() # TODO: Add readable error message

        save_to = 'C:/Users/eyal1izhaki/Documents/code/scraper-task/scraped_data'
        path = self._generate_html_path(save_to)

        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True) # Creating missing parent directories

        await async_write_to_file(path, self._raw_content)

        logging.info(f"Wrote {self._url} to file {path}")
    
    def save_as_file_task(self, save_to):
         
        if self._raw_content is None:
            MissingContent() # TODO: Add readable error message

        return asyncio.create_task(self.save_as_file(save_to))

    def _extract_links(self):
        
        if self._raw_content is None:
            MissingContent() # TODO: Add readable error message

        extracted_urls = []

        for Extractor in self._urls_extractors:
            extracted_urls += Extractor().extract(self)

        extracted_urls = list(set(extracted_urls)) # Removing duplicates

        return extracted_urls
