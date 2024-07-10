'''
a proxy server use flask & requests
'''
import logging

import requests

from app import app


log = logging.getLogger(__file__)


@app.route('/p/<path:url>')
def proxy(url):
    resp = get_source_resp(url)


def get_source_resp(url):
    url = 'http://%s' % url
    log.info('Fetching %s', url)
    return requests.get(url, stream=True, proxy=)


def get_proxy():
    