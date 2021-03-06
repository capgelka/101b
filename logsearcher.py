#!/usr/bin/env python3

import sys
import requests
import re
from fnmatch import fnmatch

from typing import Tuple, NewType, Iterable, Optional


Credentials = NewType('Credentials', Tuple[str, str])


sys.path.append('.')

from logs import search


def auth_data(addr: str) -> Credentials:
    if addr in ('localhost', '127.0.0.1', '0.0.0.0', 'http://localhost:8080', 'localhost:8080'):
        return Credentials(('test', 'test'))
    else:
        raise KeyError('No creds for adress {} found'.format(addr))


def get_link_from_html(html: str, mask: str=None) -> Optional[str]:
    pattern = re.compile(r'<a href="(.*?)">(.*?)</a>')
    gen = (match.group(1) for match in re.finditer(pattern, html)
           if mask is None
           or fnmatch(match.group(2), mask) 
           or re.match(mask, match.group(2)))
    try:   
        result = next(gen)
    except StopIteration:
        result = None
    else:
        try:
            next(gen)
        except StopIteration:
            pass
        else:
            raise KeyError('More than one log matches the mask!')
    return result


def logs_by_mask(addr: str, mask: str) -> Iterable[str]:
    creds = auth_data(addr)
    link = get_link_from_html(requests.get(addr, auth=creds).text, mask)
    if link is None:
        return
    yield from map(lambda x: x.decode('utf8'), 
                   requests.get(link if link.startswith('http')
                                         else "/".join([addr, link]), 
                                stream=True,
                                auth=creds).iter_lines())


def log_search(addr: str, mask: str, token: str) -> None:
    stream = logs_by_mask(addr, mask)
    search(stream, token)

if __name__ == '__main__':
    import subprocess
    from time import sleep
    docker = subprocess.Popen(['docker', 'run', '-p', '8080:80', 'ldyach/logstorage'])
    for _ in range(10):
        try:
            requests.get('http://localhost:8080')
        except requests.ConnectionError:
            sleep(1)
        else:
            break
    else:
        raise OSError("Can't run docker container")
    log_search('http://localhost:8080', sys.argv[1], sys.argv[2])
    docker.terminate()