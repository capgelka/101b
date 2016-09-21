import sys
import argparse
import requests
import re

from typing import Tuple, NewType, Iterable
from collections import namedtuple

Link = namedtuple('Link', ('url', 'name'))


Credentials = NewType('Credentials', Tuple[str, str])


sys.path.append('.')

from logs import search



parser = argparse.ArgumentParser()
parser.add_argument("-b", help="", type=str, required=False, default=None)
parser.add_argument("-r", help="", type=str, required=True)
parser.add_argument("-u", help="", type=str)


def auth_data(addr: str) -> Credentials:
    if addr in ('localhost', '127.0.0.1', '0.0.0.0', 'http://localhost:8080', 'localhost:8080'):
        return Credentials(('test', 'test'))
    else:
        raise KeyError('No creds for adress {} found'.format(addr))


def get_links_from_html(html: str, mask: str=None) -> Iterable[Link]:
    pattern = re.compile('<a href="(.*?)">({})</a>'.format('.*?' if mask is None else mask))
    # print(html)
    # print([Link(*match.groups()) for match in re.finditer(pattern, html)])
    yield from (Link(*match.groups()) for match in re.finditer(pattern, html))

def logs_by_mask(addr: str, mask: str, token: str) -> None:
    creds = auth_data(addr)
    def gen():
        for link in get_links_from_html(requests.get(addr, auth=creds).text,
                                        mask):
            yield from map(lambda x: x.decode('utf8'), requests.get(link.url if link.url.startswith('http')
                                             else  "/".join([addr, link.url]), 
                                             stream=True,
                                             auth=creds).iter_lines())
    # for x in gen():
    #     print(x, type(x))
    search(gen(), token) 




if __name__ == '__main__':

   logs_by_mask('http://localhost:8080', 'dmesg', '96.855757')