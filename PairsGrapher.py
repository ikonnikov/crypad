# -*- coding: utf-8 -*-

import logging
import YobitRequester as YR
import networkx as nx
import matplotlib.pyplot as plt
from tornado import ioloop, gen, httpclient, escape

logger = logging.getLogger(__name__)


def split_pair(pair):
    coins_list = pair.split(u'_')

    return coins_list[0], coins_list[1]


@gen.coroutine
def pairs_graph():
    http_client = httpclient.AsyncHTTPClient()
    http_response = yield gen.Task(http_client.fetch, YR.get_info())

    if http_response.error:
        logger.error(http_response.error)
        raise Exception(http_response.error)

    info_data = escape.json_decode(http_response.body)
    existing_pairs = {key: split_pair(key) for key, val in info_data[u'pairs'].items() if val[u'hidden'] == 0}

    graph = nx.Graph()

    coins_list = []
    pairs_list = []
    for pair, coins in existing_pairs.items():
        pairs_list.append([coins[0], coins[1]])
        coins_list.append(coins[0])
        coins_list.append(coins[1])

    coins_list = list(set(coins_list))

    graph.add_nodes_from(coins_list)
    graph.add_edges_from(pairs_list)

    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.savefig("path.png")

    cycle_nodes_of_coin = nx.cycle_basis(graph, u'sbtc')
    print(cycle_nodes_of_coin)

    for cycle in cycle_nodes_of_coin:
        pass

    a = 1


def main():
    logger.info(u'Starting Crypto-adapter YoBit: grapher')

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(pairs_graph)


if __name__ == '__main__':
    main()
