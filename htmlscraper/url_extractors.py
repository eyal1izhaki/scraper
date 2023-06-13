import re

class UrlExtractor:
    
    def extract_urls(self, html, first_n):
        raise NotImplementedError()


class AnchorHrefExtractor(UrlExtractor):
    
    def extract_urls(self, html, first_n=-1):

        a_href_regex = r'<a\s[^>]*href="([^"]*)"[^>]*>'

        matches = re.findall(a_href_regex, html)

        matches = list(set(matches))

        return matches[:first_n]