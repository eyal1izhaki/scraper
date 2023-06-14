import asyncio
import requests

from .const import ILLEGAL_FILENAME_CHARS

def get_html_filename_from_url(url: str):

    additional_chars_to_be_replaced = ['.']

    stripped_url = url.removeprefix('https://').removeprefix('http://')

    filename = ''
    for char in stripped_url:

        if char in ILLEGAL_FILENAME_CHARS:
            filename += '_'
            continue
        
        if char in additional_chars_to_be_replaced:
            filename += '_'
            continue
            
        filename += char
    
    return filename + '.html'
    

async def async_get(url, *args, **kwargs):
    return await asyncio.to_thread(requests.get, url, *args, **kwargs)

async def async_write_to_file(path: str, content: bytes):

    def sync_write():
        try:
            with open(path, 'wb') as file:
                file.write(content)
        except:
            pass

    return await asyncio.to_thread(sync_write)
    
