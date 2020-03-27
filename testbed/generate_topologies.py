import yaml

from networkx.classes import Graph

from common import node_attrs, edge_attrs, app_config

with open("topology_definition.yml", 'r') as stream:
    try:
        definitions = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def add_node(g: Graph, node):
    # zones are used to prevent cyclies
    if not node['role']:
        g.add_node(node['name'], **node_attrs(type='zone'))

    # if you do not supply a zone, the node is interpreted as being a machine
    # the role is attached as tag to the AWS instance and can be used to run
    # tasks only on machines with a certain role (see mockfog_application.yml notebook)
    else:
        g.add_node(node['name'], **node_attrs(role=node.get('role', None), flavor=node.get('flavor', None), image=node.get('image', None)))


def add_edge(g: Graph, edge):
    g.add_edge(edge['u_of_edge'], edge['v_of_edge'], **edge_attrs(delay=edge.get('delay', 0)))


def topology(g: Graph):
    for node in definitions['Nodes']:
        add_node(g, node)
    for edge in definitions['Edges']:
        add_edge(g, edge)