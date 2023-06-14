import re

class UrlExtractor:
    
    def extract_urls(self, html):
        raise NotImplementedError()

    def validate(self):
        pass


class SimpleAnchorHrefExtractor(UrlExtractor):
    
    def extract_urls(self, html):

        a_href_regex = r'<a\s[^>]*href="(\s*http[^"]*)"[^>]*>'

        matches = re.findall(a_href_regex, html)

        matches = list(set(matches))

        return matches
    
class RequestsHTMLLinksExtractor(UrlExtractor):

    def extract_urls(self, html):

        links = list(html.absolute_links)

        http_only = []

        for link in links:
            if link.startswith('http'):
                http_only.append(link)
            

        return http_only
