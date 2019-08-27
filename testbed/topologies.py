from networkx.classes import Graph

from common import node_attrs, edge_attrs, app_config


def simple_topology(g: Graph):
    # zones are used to prevent cyclies
    g.add_node('cloud1', **node_attrs(type='zone'))

    # if you do not supply a zone, the node is interpreted as being a machine
    # the role is attached as tag to the AWS instance and can be used to run tasks only on machines with a certain role
    g.add_node('cloud1_broker1', **node_attrs(role='broker',
                                              app_configs=[
                                                  app_config(
                                                      # this automatically adds an internal_ip field to the output with the respective node ip
                                                      connect_to='cloud1_client1',
                                                      # you can define in commons whether fields are mandatory
                                                      timeout=10
                                                  ),
                                                  app_config(
                                                      connect_to='cloud1_client2',
                                                      timeout=10
                                                  )]))
    g.add_node('cloud1_client1', **node_attrs(role='client',
                                              app_configs=[
                                                  app_config(
                                                      connect_to='cloud1_client2',
                                                      timeout=10
                                                  )]))
    g.add_node('cloud1_client2', **node_attrs(role='client',
                                              app_configs=[
                                                  app_config(
                                                      connect_to='cloud1_client1',
                                                      timeout=10
                                                  )]))


    g.add_edge('cloud1_broker1', 'cloud1', **edge_attrs(delay=4))
    g.add_edge('cloud1_client1', 'cloud1', **edge_attrs(delay=2))
    g.add_edge('cloud1_client2', 'cloud1', **edge_attrs(delay=2))
