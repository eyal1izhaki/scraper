import asyncio
import requests
from typing import Awaitable
from requests import Response

from .const import ILLEGAL_FILENAME_CHARS


def get_html_filename_from_url(url: str) -> str:
    """Generates filenames from a given url

    Args:
        url (str): The url to generate name for

    Returns:
        str: Filename for the given url
    """

    additional_chars_to_replace = ['.'] # A legal character to also replace

    stripped_url = url.removeprefix('https://').removeprefix('http://')

    filename = ''
    for char in stripped_url:

        if char in ILLEGAL_FILENAME_CHARS:
            filename += '_'
            continue

        if char in additional_chars_to_replace:
            filename += '_'
            continue

        filename += char

    return filename + '.html'


async def async_get(url: str, *args, **kwargs) -> Response:
    """Returns an async version of the requests.get method

    Args:
        url (str): URL to send get request to.

    Returns:
        Response: Response to the sent get request
    """
    return await asyncio.to_thread(requests.get, url, *args, **kwargs)
