# -*- coding: utf-8 -*-

import logging
import codecs
import ConfigParser
from YobitUtils import LongLegCatcher
from tornado import ioloop
from tornado.options import define, options, parse_command_line
# from tornado.locks import Condition

logger = logging.getLogger(__name__)

define('config', help='absolute path to config file')

parse_command_line()
config = ConfigParser.ConfigParser()
config.readfp(codecs.open(options.config, 'r', 'utf-8-sig'))


STATUSDELAY = 3000
# condition = Condition()


def main():
    logger.info(u'Starting Crypto-adapter YoBit')

    task = LongLegCatcher(
        # currency_pairs=[('dash_usd', 'usd', 'dash'), ('dash_doge', 'dash', 'doge'), ('waves_doge', 'doge', 'waves'), ('waves_usd', 'waves', 'usd')],
        # currency_pairs=[('eth_usd', 'usd', 'eth'), ('eth_btc', 'eth', 'btc'), ('btc_usd', 'btc', 'usd')],
        # currency_pairs=[('doge_usd', 'usd', 'doge'), ('yes_doge', 'doge', 'yes'), ('yes_usd', 'yes', 'usd')],
        callback_time=STATUSDELAY
    )
    task.start()

    logger.info(u'Daemon loop start')
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
