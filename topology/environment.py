import json
import sys
import yaml

envs = ""

if (len(sys.argv) != 2):
    raise ValueError(
        "Script should be run with exactly one argument that is a relative path to the JSON file you're trying to load")

with open("testbed_definition.yml") as yaml_data:
    t = yaml.load(yaml_data, Loader=yaml.BaseLoader)

ips = {}

for n in t["nodes"]:
    ips[n["name"]] = n["internal_ip"]

with open(sys.argv[1]) as json_data:
    d = json.load(json_data)

# add service to
placements = d["placements"]

port = 8000

# Build topology data
for k, v in placements.items():
    envs += k.upper() + "_IP=" + ips[v] + "\n"
    envs += k.upper() + "_PORT=" + str(port) + "\n"
    port += 1

with open('mapping.env', 'w') as f:
    f.write(envs)
