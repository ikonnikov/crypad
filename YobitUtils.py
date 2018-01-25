# -*- coding: utf-8 -*-

import logging
import string
from tornado import ioloop, httpclient, gen, escape
import YobitRequester as YR

logger = logging.getLogger(__name__)

PRX_HOST = None
PRX_PORT = None
PRX_USER = None
PRX_PSWD = None


class LongLegCatcher(ioloop.PeriodicCallback):
    def __init__(self, currency_pairs, callback_time):
        self._currency_pairs = currency_pairs
        super(LongLegCatcher, self).__init__(self._callback, callback_time, None)

    def _get_pairs_names(self):
        return [pair for pair, _, _ in self._currency_pairs]

    @gen.coroutine
    def _callback(self):
        self._currency_info = yield self._get_currency_info()

        if len(self._currency_info) != len(self._currency_pairs):
            ioloop.IOLoop.current().stop()
            logger.error(u'Some currency pair is forbidden: {}'.format(self._get_pairs_names()))
            raise Exception(u'Some currency pair is forbidden')

        profit_rate = yield self._calc_order_data()
        if profit_rate > 1:
            logger.info(u'To DEAL it: {:.8f}'.format(profit_rate))
        else:
            logger.info(u'To next it: {:.8f}'.format(profit_rate))

    @gen.coroutine
    def _calc_order_data(self):
        pairs_data = yield self._get_currency_depth()
        # pairs_data = {
        #     u'eth_usd': {
        #         u'pair': {u'asset': u'eth', u'currency': u'usd'},
        #         u'sell': {u'price': 1508.00, u'amount': 1},
        #         u'buy': {u'price': 1506.00, u'amount': 1}
        #     },
        #     u'eth_btc': {
        #         u'pair': {u'asset': u'eth', u'currency': u'btc'},
        #         u'sell': {u'price': 0.09875098, u'amount': 1},
        #         u'buy': {u'price': 0.0984, u'amount': 1}
        #     },
        #     u'btc_usd': {
        #         u'pair': {u'asset': u'btc', u'currency': u'usd'},
        #         u'sell': {u'price': 15383.54, u'amount': 1},
        #         u'buy': {u'price': 15340.00, u'amount': 1}
        #     }
        # }

        profit_rate = 1
        for leg_pair, leg_from, leg_to in self._currency_pairs:
            pair_data = pairs_data[leg_pair]
            pair = pair_data[u'pair']

            if pair[u'asset'] == leg_from and pair[u'currency'] == leg_to:
                buy = pair_data[u'buy']
                profit_rate = self._buy(profit_rate, buy[u'price'], 0.2, 8)
            elif pair[u'currency'] == leg_from and pair[u'asset'] == leg_to:
                sell = pair_data[u'sell']
                profit_rate = self._sell(profit_rate, sell[u'price'], 0.2, 8)
            else:
                break

        raise gen.Return(profit_rate)

    @staticmethod
    def _sell(value, price, fee, prec=8):
        result = round(float(value) / float(price), prec)
        result = round(result * (1.0 - float(fee) / 100), prec)

        return result

    @staticmethod
    def _buy(value, price, fee, prec=8):
        result = round(float(value) * float(price), prec)
        result = round(result * (1.0 - float(fee) / 100), prec)

        return result

    @gen.coroutine
    def _get_currency_depth(self):
        http_response = yield self._urled_get_depth(top=5)
        if http_response.error:
            logger.error(http_response.error)
            raise Exception(http_response.error)

        depth_data = escape.json_decode(http_response.body)
        if depth_data is None:
            logger.error(u'Can\'t decode currency depth response')
            raise Exception(u'Can\'t decode currency depth response')

        pair_data = {}
        for currency_key in self._currency_info:
            asset, currency = self._get_currencies_names(currency_key)

            asset_data = depth_data[currency_key]
            pair_data.update(
                {
                    currency_key: {
                        u'pair': {u'asset': asset, u'currency': currency},
                        u'sell': {
                            u'price': asset_data[u'asks'][0][0],
                            u'amount': asset_data[u'asks'][0][1]
                        },
                        u'buy': {
                            u'price': asset_data[u'bids'][0][0],
                            u'amount': asset_data[u'bids'][0][1]
                        }
                    }
                }
            )
            pass

        raise gen.Return(pair_data)

    @staticmethod
    def _get_currencies_names(currency_key):
        curr_list = string.split(currency_key, u'_')
        asset = curr_list[0]
        currency = curr_list[1]

        return asset, currency

    @gen.coroutine
    def _get_currency_info(self):
        http_response = yield self._urled_get_info()
        if http_response.error:
            logger.error(http_response.error)
            raise Exception(http_response.error)

        info_data = escape.json_decode(http_response.body)
        if info_data is None:
            logger.error(u'Can\'t decode currency info response')
            raise Exception(u'Can\'t decode currency info response')

        raise gen.Return({key: val for key, val in info_data[u'pairs'].items() if
                          val[u'hidden'] == 0 and key in self._get_pairs_names()})

    @gen.coroutine
    def _urled_get_depth(self, top=150):
        http_client = httpclient.AsyncHTTPClient()
        http_response = yield gen.Task(
            http_client.fetch,
            YR.get_depth(
                pairs='-'.join(self._get_pairs_names()),
                top=top,
                prx_host=PRX_HOST,
                prx_port=PRX_PORT,
                prx_user=PRX_USER,
                prx_pswd=PRX_PSWD
            )
        )

        raise gen.Return(http_response)

    @gen.coroutine
    def _urled_get_info(self):
        http_client = httpclient.AsyncHTTPClient()
        http_response = yield gen.Task(
            http_client.fetch,
            YR.get_info(
                prx_host=PRX_HOST,
                prx_port=PRX_PORT,
                prx_user=PRX_USER,
                prx_pswd=PRX_PSWD
            )
        )

        raise gen.Return(http_response)


class CryptoPair(object):
    def __init__(self, name, coin_asset, coin_currency, precision=8):
        self._name = name
        self._asset = coin_asset
        self._currency = coin_currency
        self._precision = precision

    def sell(self, fee):
        pass

    def buy(self, fee):
        pass
