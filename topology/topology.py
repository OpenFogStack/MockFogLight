from networkx.classes import Graph

from common import node_attrs, edge_attrs, app_config

import json


def create(g: Graph, file):
    # read json file

    with open(file) as json_data:
        d = json.load(json_data)

    # add nodes

    for n in d["nodes"]:
        g.add_node(n["id"], **node_attrs(role=n["id"], app_configs=[]))
        #g.add_node(n["id"], **node_attrs(app_configs=[]))

    # add data paths

    for e in d["connections"]:
        g.add_edge(e["from"], e["to"], **edge_attrs(delay=float(e["baseProperties"]
                                                                ["latency"]*1000), bandwidth=e["baseProperties"]["availableBandwidth"]))

    # g.add_edge("cloud1_broker1", "cloud1", **edge_attrs(delay=4))

    # # zones are used to prevent cycles
    # g.add_node("cloud1", **node_attrs(type="zone"))

    # # if you do not supply a zone, the node is interpreted as being a machine
    # # the role is attached as tag to the AWS instance and can be used to run tasks only on machines with a certain role (see mockfog_application.yml notebook)
    # g.add_node(
    #     "cloud1_broker1",
    #     **node_attrs(
    #         role="broker",
    #         # there can be multiple app configs, if needed
    #         app_configs=[
    #             app_config(
    #                 # this automatically adds an internal_ip field to the output with the respective node ip
    #                 connect_to="cloud1_client1",
    #                 # you can define in commons whether fields are mandatory
    #                 timeout=10,
    #             )
    #         ],
    #     )
    # )
    # g.add_node(
    #     "cloud1_client1",
    #     **node_attrs(
    #         role="client",
    #         app_configs=[app_config(connect_to="cloud1_client2", timeout=10)],
    #     )
    # )
    # g.add_node(
    #     "cloud1_client2",
    #     **node_attrs(
    #         role="client",
    #         app_configs=[app_config(connect_to="cloud1_client1", timeout=10)],
    #     )
    # )

    # g.add_edge("cloud1_broker1", "cloud1", **edge_attrs(delay=4))
    # g.add_edge("cloud1_client1", "cloud1", **edge_attrs(delay=2))
    # g.add_edge("cloud1_client2", "cloud1", **edge_attrs(delay=2))
