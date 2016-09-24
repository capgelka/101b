import pytest
import subprocess

import sys
sys.path.append('.')
import requests
from time import sleep

from logsearcher import log_search, get_links_from_html

@pytest.fixture(scope='session')
def docker(request):
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
    yield docker
    docker.terminate()


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


@pytest.mark.parametrize(['mask', 'token', 'current', 'count', 'expected_exc', 'exc_message'], 
                         [('Xorg.02', '6152.002', 
                           'current: [  6152.002] (II) XKB: reuse xkmfile'
                           ' /var/lib/xkb/server-FFD7F0C098264F028A1D8B92D2B11BFAFFBFB85B.xkm',
                           115, None, None),
                         ('Xo', '6152.002', 
                           'current: [  6152.002] (II) XKB: reuse xkmfile'
                           ' /var/lib/xkb/server-FFD7F0C098264F028A1D8B92D2B11BFAFFBFB85B.xkm',
                           201, None, None),
                        # ('Xo', '6141.941', None, None, KeyError, 
                        #  'There are more then one string satisfies the predicate:'
                        #  ' [  6141.941] \tBefore reporting problems, check http:/'
                        #  '/wiki.x.org\n[  6141.941] Markers: (--) probed, (**) fr'
                        #  'om config file, (==) default setting,'),
                        ('No', '6141.941', 'No lines with specified mask found', 0,
                          None, None),
                        ('*', 'cpuset',
                         'current: [    0.000000] Initializing cgroup subsys cpuset', 201,
                          None, None),
                        ('dmesg', 'cpuset',
                         'current: [    0.000000] Initializing cgroup subsys cpuset', 101,
                          None, None),
                        ('dmesg', ' 96.855764',
                         'current: [   96.855764] cfg80211:   (57240000 KHz'
                         ' - 63720000 KHz @ 2160000 KHz), (N/A, 4000 mBm), (N/A)', 101,
                          None, None)
                          # ('dmesg', 1),
                          # ('Xo', 2),
                          # ('Xo*.3', 1),
                          # (r'd\w+', 1),
                          # ('.*', 5)
                         ])


def test_search(docker, capsys, mask, token, current, count, expected_exc, exc_message):
    if expected_exc is not None:
        with pytest.raises(expected_exc, message=exc_message):
            log_search('http://localhost:8080', mask, token)
    else:
        log_search('http://localhost:8080', mask, token)
        out, _ = capsys.readouterr()
        out_lines = out.split('\n')[:-1]
        assert out_lines[0] == current
        # raise Exception('!!!!' + out_lines[-1]+ '!!!!!)')
        assert len(out_lines[2:]) == count
        # print(out_lines)
    # raise Exception(out + str(type(out)))
