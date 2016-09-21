import sys
import requests
import re
from fnmatch import fnmatch

from typing import Tuple, NewType, Iterable


Credentials = NewType('Credentials', Tuple[str, str])


sys.path.append('.')

from logs import search


def auth_data(addr: str) -> Credentials:
    if addr in ('localhost', '127.0.0.1', '0.0.0.0', 'http://localhost:8080', 'localhost:8080'):
        return Credentials(('test', 'test'))
    else:
        raise KeyError('No creds for adress {} found'.format(addr))


def get_links_from_html(html: str, mask: str=None) -> Iterable[str]:
    pattern = re.compile(r'<a href="(.*?)">(.*?)</a>')
    yield from (match.group(1) for match in re.finditer(pattern, html)
                if mask is None
                or fnmatch(match.group(2), mask) 
                or re.match(mask, match.group(2)))


def logs_by_mask(addr: str, mask: str) -> Iterable[str]:
    creds = auth_data(addr)
    for link in get_links_from_html(requests.get(addr, auth=creds).text,
                                    mask):
        yield from map(lambda x: x.decode('utf8'), 
                       requests.get(link if link.startswith('http')
                                             else "/".join([addr, link]), 
                                    stream=True,
                                    auth=creds).iter_lines())


def log_search(addr: str, mask: str, token: str) -> None:
    stream = logs_by_mask(addr, mask)
    search(stream, token)

if __name__ == '__main__':

   log_search('http://localhost:8080', 'dmesg', '96.855757')