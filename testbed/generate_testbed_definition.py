#!/usr/bin/env python

import sys

import networkx as nx
import yaml
from matplotlib import pyplot as plt

import topologies
from common import validate_graph, fill_node_attrs, resolve_names

g = nx.Graph()

# Generate topology

topologies.simple_topology(g)

# Process graph

validate_graph(g)

fill_node_attrs(g)

resolve_names(g)

# Build topology data

topo = {
    'nodes': [attrs for node, attrs in g.nodes(data=True) if attrs['type'] == 'machine']
}

# Write yaml file (path should match variable defined in defaults)
with open(f'{sys.path[0]}/testbed_definition.yml', 'w') as file:
    file.write(yaml.dump(topo, default_flow_style=False, sort_keys=False, explicit_start=True))

# Show graph for a quick sanity check
nx.draw_networkx(g)
plt.show()
