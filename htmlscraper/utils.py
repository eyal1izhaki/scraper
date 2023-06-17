import asyncio
import requests

from .const import ILLEGAL_FILENAME_CHARS


def get_html_filename_from_url(url: str):

    additional_chars_to_replace = ['.']

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


async def async_get(url, *args, **kwargs):
    return await asyncio.to_thread(requests.get, url, *args, **kwargs)
