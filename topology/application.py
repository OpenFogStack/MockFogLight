import json
import sys
import yaml

if (len(sys.argv) != 2):
    raise ValueError(
        "Script should be run with exactly one argument that is a relative path to the JSON file you're trying to load")

# Generate topology from JSON file

with open(sys.argv[1]) as json_data:
    d = json.load(json_data)

# add service to
placements = d["placements"]

topo = []

port = 8000

# Build topology data
for k, v in placements.items():
    topo.append({
        "name": "Rollout " + k,
        "hosts": v + "_nodes",
        "remote_user": "ec2-user",
        "become": "yes",
        "vars": {
            "container_name": k,
            "image_name": k,
            "docker_repo": "pfandzelter"
        },
        "roles": ["application"]
    })

    port += 1

# Write yaml file (path should match variable defined in defaults)
with open(f"{sys.path[0]}/../application.yml", "w") as file:
    file.write(
        yaml.dump(topo, default_flow_style=False,
                  sort_keys=False, explicit_start=True)
    )
