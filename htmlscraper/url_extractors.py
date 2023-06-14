import re
from urllib.parse import urljoin, urlparse

class UrlExtractor:
    
    def extract_urls(self, html):
        raise NotImplementedError()

    def validate(self):
        pass

class SimpleAnchorHrefExtractor(UrlExtractor):

    def extract_urls(self, parent_url, html):

        a_href_regex = r'<a\s[^>]*href="(\s*(http|\/)[^"]*)"[^>]*>' # finds relative and absolute links in <a href>

        matches = re.findall(a_href_regex, html)
        matches = list(set(matches)) # Remove duplicates

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
                print(url)
                continue

        return result