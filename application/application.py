import json
import sys
import yaml

if (len(sys.argv) != 2):
    raise ValueError("Script should be run with exactly one argument that is a relative path to the JSON file you're trying to load")

g = nx.Graph()

# Generate topology from JSON file

with open(sys.argv[1]) as json_data:
    d = json.load(json_data)

    # add service to 
placements = d["placements"]

# Build topology data

topo = {
    "nodes": [attrs for node, attrs in g.nodes(data=True) if attrs["type"] == "machine"]
}

# Write yaml file (path should match variable defined in defaults)
with open(f"{sys.path[0]}/testbed_definition.yml", "w") as file:
    file.write(
        yaml.dump(topo, default_flow_style=False, sort_keys=False, explicit_start=True)
    )

