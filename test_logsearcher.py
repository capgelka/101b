import pytest
import subprocess

import sys
sys.path.append('.')
import requests

from logsearcher import logs_by_mask, get_links_from_html

@pytest.fixture(scope='session')
def docker(request):
    return subprocess.run(['docker', 'run', '-p', '8080:80', 'ldyach/logstorage'], 
                          stdout=subprocess.PIPE)


@pytest.fixture(scope='session')
def html(request, docker):
    return requests.get('http://localhost:8080', auth=('test', 'test')).text

# def test_fake():
#     assert 1 == 1

# @pytest.mark.usefixtures(docker)
@pytest.mark.parametrize(['mask', 'count'], 
                         [('notexists', 0),
                          ('dmesg', 1),
                          ('Xo', 2),
                          ('Xo*.3', 1),
                          (r'd\w+', 1),
                          ('.*', 5)
                         ])
# @pytest.mark.usefixtures(docker)
def test_mask(docker, html, mask, count):
    logs = list(get_links_from_html(html, mask))
    assert len(logs) == count
