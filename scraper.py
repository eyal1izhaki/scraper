import argparse
import logging
import urllib
import asyncio
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning


from htmlscraper.scraper import Scraper


def url_type(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return url
    else:
        raise argparse.ArgumentTypeError(f"'{url}' is not a valid URL")


def main():

    parser = argparse.ArgumentParser(
        description="Program that recursively scrapes htmls from a given root url to a given depth.")

    parser.add_argument('root_url', type=url_type,
                        help='Root url to start scrape from.')
    parser.add_argument('--level', '-l', type=int, required=True,
                        help='Max depth of the recursive scrape.')
    parser.add_argument('--width', '-w', type=int, required=True,
                        help='Max urls to scrape per html page.')
    parser.add_argument('--unique', '-u', action='store_true',
                        help='Scrape unique urls only.')

    parser.add_argument('--output_dir', '-o', type=str, default='./scraped_data',
                        help='Output directory to store scraped htmls')
    parser.add_argument('--ignore_ssl_verification', action='store_true',
                        help="Scrape html even if ssl verification failed.")

    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Enable verbose mode.")
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug mode.")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    else:
        # Disable warnings about insecure requests when ignore_ssl_verification is set to true
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    scraper = Scraper(
        root_url=args.root_url,
        scraping_depth=args.level,
        scraping_width=args.width,
        unique_urls_only=args.unique,
        data_dir=args.output_dir,
        ignore_ssl_verification=args.ignore_ssl_verification
    )

    asyncio.run(scraper.start_scrape())


if __name__ == '__main__':
    main()
