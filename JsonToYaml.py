#!/usr/bin/env python
import sys
import json
import yaml

ec2_mapping = {}
mapping_json = json.loads(open("mapping.json").read())
for item in mapping_json:
    ec2_mapping[item['id']] = item['ip']

with open('mapping.yml', 'w') as outfile:
    outfile.write("nodes: \n")
    print(yaml.dump(yaml.load(json.dumps(mapping_json)), outfile, default_flow_style=False))

with open('mockfog_application/vars/mapping.yml', 'w') as outfile:
    outfile.write("nodes: \n")
    print(yaml.dump(yaml.load(json.dumps(ec2_mapping)), outfile, default_flow_style=False))
