import re
from urllib.parse import urlparse
from typing import List

class URLExtractor:
    """Class the inherit from, in order to write custom Extractor"""

    def extract(self, html: str):
        """Extracts urls from a given html string.

        Args:
            html (str): HTML string to extract urls from.

        Raises:
            NotImplementedError: Inherit classes need to implement the logic of extracting the urls
        """
        raise NotImplementedError()


class SimpleAnchorHrefExtractor(URLExtractor):
    """URL Extractor that extract urls inside href attribute of Anchor HTML element"""

    def extract(self, parent_url: str, html: str) -> List[str]:
        """Extracts urls from a given html string.

        Args:
            parent_url (str): URL of the given html. Used to convert relative urls to absolute ones.
            html (str): HTML string to extract urls from.

        Returns:
            List[str]: List of extracted urls
        """

        # finds relative and absolute links in <a href>
        a_href_regex = r'<a\s[^>]*href="(\s*(http|\/)[^"]*)"[^>]*>'

        matches = re.findall(a_href_regex, html)

        result = []

        for match in matches:

            url = match[0].strip() # Removes prefix and suffix spaces

            if url.startswith('/') and not url.startswith('//'):  # starts with one /
                parsed_url = urlparse(parent_url)
                absolute_url = parsed_url.scheme + "://" + parsed_url.netloc + url
                result.append(absolute_url)

            elif url.startswith('//'):  # starts with //
                parsed_url = urlparse(parent_url)
                absolute_url = parsed_url.scheme + ":" + url
                result.append(absolute_url)

            # starts with http:// or https://
            elif url.startswith('http://') or url.startswith('https://'):
                result.append(url)

            else:  # Not a valid url
                continue

        return result
