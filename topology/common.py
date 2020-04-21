import random
import sys

import networkx as nx
from networkx import Graph, NetworkXNoCycle, NetworkXNoPath

# .1, .2, .3, .255 are reserved by AWS and we keep .4 through .10 as static options
ip_address_pool = ['10.0.2.' + str(i) for i in range(11, 255)]


def generate_random_ip():
    if len(ip_address_pool) == 0:
        print('IP address space exhausted! Aborting...')
        sys.exit(1)
    random_ip = random.choice(ip_address_pool)
    ip_address_pool.remove(random_ip)
    return random_ip


def node_attrs(**kwargs):
    attrs = {
        'type': 'machine',
        'flavor': 't2.small',
        'internal_ip': generate_random_ip(),
        **kwargs,
    }
    assert 'type' in attrs
    assert 'flavor' in attrs
    assert 'internal_ip' in attrs
    return attrs


def edge_attrs(**kwargs):
    attrs = {
        'delay': 0,
        'bandwidth': 10000,
        **kwargs,
    }
    assert 'delay' in attrs
    assert 'bandwidth' in attrs
    return attrs


def app_config(**kwargs):
    config = {
        **kwargs,
    }
    assert 'timeout' in config
    return config


def get_path_between_machines(graph: Graph, src, dst):
    return nx.shortest_path(graph, source=src, target=dst, weight='delay')


def get_path_bandwidth(graph: Graph, path):
    b = float("inf")

    for i in range(0, len(path) - 1):
        bandwidth = graph[path[i]][path[i + 1]]["bandwidth"]

        if bandwidth < b:
            b = bandwidth

    return b


def get_path_latency(graph: Graph, path):
    l = 0

    for i in range(0, len(path) - 1):
        latency = graph[path[i]][path[i + 1]]["delay"]
        l += latency

    return l


def build_name_to_ip(g: Graph):
    name_to_ip = {}
    machine_nodes = {attrs['name']: attrs['internal_ip'] for node, attrs in g.nodes(data=True) if
                     attrs['type'] == 'machine'}
    for node, attrs in machine_nodes:
        name_to_ip[attrs['name']] = attrs['internal_ip']
    return name_to_ip


def validate_graph(g: Graph):
    # Check for cycles (lets not allow cycles for now)
    # try:
    #     c = nx.find_cycle(g)
    #     print("Cycle found! Aborting...")
    #     print(c)
    #     sys.exit(1)
    # except NetworkXNoCycle:
    #     pass

    # Check if graph is connected
    try:
        nx.is_connected(g)
    except NetworkXNoPath:
        print("Graph is not connected! Aborting...")
        sys.exit(1)


def fill_node_attrs(g: Graph):
    # Add name and delay paths
    machine_nodes = [(node, attrs) for node, attrs in g.nodes(
        data=True) if attrs['type'] == 'machine']
    for node, attrs in machine_nodes:
        attrs_update = {
            'name': node,
            'connections': []
        }
        for dst_node, dst_attrs in filter(lambda n: n[0] != node, machine_nodes):

            path = get_path_between_machines(g, node, dst_node)

            attrs_update['connections'].append({
                'target': dst_node,
                'internal_ip': dst_attrs['internal_ip'],
                'latency': int(get_path_latency(g, path)*1000),
                'bandwidth': int(get_path_bandwidth(g, path)/1000000)
            })
        g.node[node].update(attrs_update)


def resolve_names(g):
    name_to_ip = {attrs['name']: attrs['internal_ip'] for node, attrs in g.nodes(data=True) if
                  attrs['type'] == 'machine'}
    machine_nodes = [(node, attrs) for node, attrs in g.nodes(data=True) if
                     attrs['type'] == 'machine']
    for node, attrs in machine_nodes:
        for config in attrs['app_configs']:
            config['internal_ip'] = name_to_ip[config['connect_to']]
        g.node[node]['app_configs'] = attrs['app_configs']
