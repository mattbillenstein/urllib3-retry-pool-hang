#!/usr/bin/env python2

import sys
import threading
import time
import urllib3
from urllib3.util import Retry
from urlparse import urlparse

url = sys.argv[-1]
assert url.startswith('http'), url

def make_pool(url):
    parsed = urlparse(url)
    assert parsed.scheme == 'http', parsed
    host = parsed.netloc
    port = 80
    if ':' in host:
        host, port = host.split(':')
        port = int(port)

    retries = False
    if '--retry' in sys.argv:
        retries = Retry(
            total = 3,
            backoff_factor = 0.1,
            raise_on_status = False,
            status_forcelist = [404],
        )

    return urllib3.HTTPConnectionPool(host, port, maxsize=10, block=True, retries=retries)

pool = make_pool(url)

def worker():
    while 1:
        res = pool.urlopen('GET', url, preload_content=False)
        assert res.status == 404
        res.release_conn()
        sys.stdout.write('.')
        sys.stdout.flush()

def main():
    workers = []
    for i in xrange(10):
        t = threading.Thread(target=worker)
        t.daemon = True
        workers.append(t)
        t.start()

    while 1:
        time.sleep(3)
        if all(not _.isAlive() for _ in workers):
            break

if __name__ == '__main__':
    main()
