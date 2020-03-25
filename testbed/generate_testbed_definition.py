#!/usr/bin/env python

import sys

import networkx as nx
import yaml
from matplotlib import pyplot as plt

import generate_topologies
import topologies

from common import (
    fill_node_attrs,
    get_app_configurations,
    resolve_names,
    validate_graph
)

g = nx.Graph()

# Generate topology

generate_topologies.topology(g)

# Process graph

validate_graph(g)

fill_node_attrs(g)

resolve_names(g)

app_configs = get_app_configurations()

# Build topology data

topo = {
    'nodes': [attrs for node, attrs in g.nodes(data=True) if attrs['type'] == 'machine']
}

# Write yaml file (path should match variable defined in defaults)
with open(f'{sys.path[0]}/testbed_definition.yml', 'w') as file:
    file.write(yaml.dump(topo, default_flow_style=False, sort_keys=False, explicit_start=True))

# Write app_configs to yaml file (path should match variable defined in defaults)
with open(f'{sys.path[0]}/application_definition.yml', 'w') as file:
    file.write(yaml.dump(app_configs, default_flow_style=False, sort_keys=False, explicit_start=True))

# Show graph for a quick sanity check
nx.draw_networkx(g)
plt.show()
