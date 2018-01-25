# -*- coding: utf-8 -*-

import logging
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders

logger = logging.getLogger(__name__)

# USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
BASE_URL = 'https://yobit.io'

get_headers = HTTPHeaders()
get_headers.add('Accept', 'application/json')

post_headers = HTTPHeaders()
post_headers.add('Content-Type', 'application/x-www-form-urlencoded')


def get_info(prx_host=None, prx_port=None, prx_user=None, prx_pswd=None):
    # https://yobit.net/api/3/info
    return HTTPRequest(
        url=BASE_URL + '/api/3/info',
        headers=get_headers,
        method='GET',
        validate_cert=False,
        user_agent=USER_AGENT,
        proxy_host=prx_host,
        proxy_port=prx_port,
        proxy_username=prx_user,
        proxy_password=prx_pswd
    )


def get_depth(pairs, top, prx_host=None, prx_port=None, prx_user=None, prx_pswd=None):
    # https://yobit.net/api/3/depth/{pair1[-pairN]}?limit=30
    return HTTPRequest(
        url=BASE_URL + '/api/3/depth/{}?limit={}'.format(pairs, top),
        headers=get_headers,
        method='GET',
        validate_cert=False,
        user_agent=USER_AGENT,
        proxy_host=prx_host,
        proxy_port=prx_port,
        proxy_username=prx_user,
        proxy_password=prx_pswd
    )
