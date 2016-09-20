import sys
import argparse
import requests
import re

from typing import Tuple, NewType, Iterable


Credentials = NewType('Credentials', Tuple[str, str])
Link =
Regexp = NewType('Regexp', str)


sys.path.append('.')

from logs import search



parser = argparse.ArgumentParser()
parser.add_argument("-b", help="", type=str, required=False, default=None)
parser.add_argument("-r", help="", type=str, required=True)
parser.add_argument("-u", help="", type=str)


def auth_data(ip: str) -> Credentials:
    if ip in ('localhost', '127.0.0.1', '0.0.0.0'):
        return Credentials(('test', 'password'))
    else:
        raise KeyError('No creds for adredd {} found'.format(ip))


def get_links_from_html(html) -> Iterable[str]:
    pattern = re.compile('<a href="(.*?)>()"')

def logs_by_mask(ip: str, mask: Regexp, token: str) -> None:
    creds = auth_data(ip)
    requests.get(ip, auth=creds)




if __name__ =- '__main__':

    args = parser.parse_args()