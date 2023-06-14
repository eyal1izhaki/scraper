import re

class UrlExtractor:
    
    def extract_urls(self, html, first_n):
        raise NotImplementedError()

    def validate(self):
        pass


class SimpleAnchorHrefExtractor(UrlExtractor):
    
    def extract_urls(self, html, first_n=-1, exclude_list=[]):

        a_href_regex = r'<a\s[^>]*href="(\s*http[^"]*)"[^>]*>'

        matches = re.findall(a_href_regex, html)

        matches = list(set(matches))

        if len(exclude_list) != 0:

            unique_matches = []
            for match in matches:
                if match not in exclude_list:
                    unique_matches.append(match)
                
            matches = unique_matches

        return matches[:first_n]