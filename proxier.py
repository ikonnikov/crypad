# -*- coding: utf-8 -*-

import urllib2
import string
import requests
from random import randint
from bs4 import BeautifulSoup as bsoup


def is_bad_proxy(pip):
    try:
        proxy_handler = urllib2.ProxyHandler({'http': pip})

        opener = urllib2.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        urllib2.install_opener(opener)
        req = urllib2.Request(u'http://www.google.com/')
        sock = urllib2.urlopen(req, timeout=10)
    except:
        return True

    return False


def get_random_proxy(proxy_list):
    proxy = {}
    bad_proxy_list = []

    if not proxy_list:
        return proxy

    try:
        my_proxy = u''
        my_proxy_type = u''

        tries = 3
        while tries > 0:
            tries -= 1

            index = randint(0, len(proxy_list))

            proxy_row = proxy_list[index]
            proxy_args = string.split(proxy_row, u'/')

            my_proxy = proxy_args[0]
            my_proxy_type = proxy_args[1]

            if my_proxy in bad_proxy_list:
                continue

            if is_bad_proxy(my_proxy):
                bad_proxy_list.append(my_proxy)
                continue
            else:
                break

        if not my_proxy:
            raise ValueError(u'No proxy')

        proxy[u'proxy'] = my_proxy
        proxy[u'proxy_type'] = my_proxy_type
    except Exception:
        pass # no proxy if out of index

    return proxy


class Proxy(object):
    def __init__(self):
        self._proxy_url = u'http://www.ip-adress.com/proxy_list/'
        self.proxies_list = []

    def parse(self):
        r = requests.get(self._proxy_url)

        soup = bsoup(r.content, u'html.parser')
        proxies_tag = soup.find(u'table', class_=u'htable proxylist').find(u'tbody').find_all(u'tr')

        for proxy_tag in proxies_tag:
            self.proxies_list.append(proxy_tag.find_all(u'td')[0].text.strip())

    def get_proxy(self):
        proxy_dict = {}

        for proxy in self.proxies_list:
            if not is_bad_proxy(proxy):
                proxy_dict[u'proxy'] = proxy
                proxy_dict[u'proxy_type'] = u'http'

                break
            else:
                continue

        return proxy_dict

# example:
# proxier = Proxy()
# proxier.parse()
# print(proxier.proxies_list)
