import re
from urllib.parse import urlparse

class UrlsExtractor:
    
    def extract(self, html):
        raise NotImplementedError()

class SimpleAnchorHrefExtractor(UrlsExtractor):

    def extract(self, parent_url, html):

        a_href_regex = r'<a\s[^>]*href="(\s*(http|\/)[^"]*)"[^>]*>' # finds relative and absolute links in <a href>

        matches = re.findall(a_href_regex, html)

        result = []

        for match in matches:

            url = match[0].strip()

            if url.startswith('/') and not url.startswith('//'): # starts with one /
                parsed_url = urlparse(parent_url)
                absolute_url = parsed_url.scheme + "://" + parsed_url.netloc + url
                result.append(absolute_url)

            elif url.startswith('//'): # starts with //
                parsed_url = urlparse(parent_url)
                absolute_url = parsed_url.scheme + ":" + url
                result.append(absolute_url)

            elif url.startswith('http://') or url.startswith('https://'): # starts with http:// or https://
                result.append(url)

            else: # Not a valid url
                continue

        return result