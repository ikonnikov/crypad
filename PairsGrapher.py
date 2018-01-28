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
    find_coin = u'sbtc'

    http_client = httpclient.AsyncHTTPClient()
    http_response = yield gen.Task(http_client.fetch, YR.get_info())

    if http_response.error:
        logger.error(http_response.error)
        raise Exception(http_response.error)

    info_data = escape.json_decode(http_response.body)
    existing_pairs = {key: split_pair(key) for key, val in info_data[u'pairs'].items() if val[u'hidden'] == 0}

    graph = populate_graph(existing_pairs)

    # nx.draw(graph, pos=nx.spring_layout(graph), with_labels=True, font_weight='bold')
    # plt.savefig("path.png")

    basis_cycles = nx.cycle_basis(graph, find_coin)
    cycle_nodes_of_coin = [cycle for cycle in basis_cycles if find_coin in cycle]

    routes_list, pairs_list = get_routes_list(find_coin, cycle_nodes_of_coin, existing_pairs)

    print(routes_list)
    print(pairs_list)

    a = 1


def populate_graph(existing_pairs):
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

    return graph


def get_routes_list(find_coin, cycle_nodes_of_coin, existing_pairs):
    routes_list = []
    pairs_list = []
    for cycles in cycle_nodes_of_coin:
        cycles.insert(0, find_coin)

        current_route = []

        idx = 0
        while idx < len(cycles) - 1:
            current_coin = cycles[idx]
            next_coin = cycles[idx + 1]

            current_pair = get_pair_by_coins(current_coin, next_coin, existing_pairs)

            pairs_list.append(current_pair)
            current_route.append((current_pair, current_coin, next_coin))

            idx += 1

        if len(current_route) > 0:
            routes_list.append(current_route)

    pairs_list = list(set(pairs_list))

    return routes_list, pairs_list


def get_pair_by_coins(coin1, coin2, pairs):
    pair1 = coin1 + u'_' + coin2
    if pair1 in pairs:
        return pair1

    pair2 = coin2 + u'_' + coin1
    if pair2 in pairs:
        return pair2

    return None


def main():
    logger.info(u'Starting Crypto-adapter YoBit: grapher')

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(pairs_graph)


if __name__ == '__main__':
    main()
