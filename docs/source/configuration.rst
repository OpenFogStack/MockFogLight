Configuration
=============

To define a topology and deploy and configure an application, 3 configuration files are required:

* topology.yaml: This file only includes configuration of the virtual nodes themselves, i.e. their ID, their links to other nodes, their EC2 instance types as well as their image identifier. 
* application_definition.yaml: This file includes specifications for the different kinds of applications that will be deployed on the nodes. These include which docker container should be used as well as which ports should be openend and forwarded.
* application_configuration.yaml: This file defines one or more application configuration. These, among other things, will map application definitions to node ids, as well as provide a way to set environment variables.


Topology
========

The topology file specifies characteristics of the EC2 instances to be deployed. An example could look like this. ::


    Nodes:
    - name: cloud1_generator1
      type: t3.nano
      image: ami-xxxxxxxxxxxxxxx

    - name: cloud1_application
    ...
    ...

    Edges:
    - u_of_edge: generator1
      v_of_edge: application1
      delay: 2


Application Definition
======================

The application_definition file specifies different kinds of applications to be deployed. An example could look like this. ::


  application_definition:
  - name: application
    container_name: application
    image_name: mockfogoverload/exampleapp:mvp
    expose: 4568
    ports: 4568:4567

  - name: generator
    container_name: generators
    image_name: mockfogoverload/generators:mvp
    expose: 8081
    ports: 8081:8080

Application Configuration
=========================

The application_configuration file allows users to create more fine grained application configurations in which he specifies which application definition is used and on which nodes the configuration should be deployed. An example could look like this. ::


  application_config:
  - name: genConf1
    application_definition: generator
    nodes: cloud1_generator1, cloud1_generator2
    vars:
      env:
        - remote: null

  - name: appConf1
    application_definition: application
    nodes: cloud1_application
    vars:
      env:
        - remote: null

Application Playbook
=========================

The Application Playbook is used to deploy applications as defined in application_definition.yml and application_config.yml. ::


  ---
  # Playbook to control the mockfog_application role
    - name: Rollout Applications
      hosts: all_nodes # based on defined role
      vars_files:
        - "{{ playbook_dir }}/mockfog_application/vars/application_definition.yml"
        - "{{ playbook_dir }}/mockfog_application/vars/application_config.yml"
      remote_user: ec2-user
      become: yes
      vars:
        _app_config: "{{(lookup('vars', 'application_config'))}}"
        _app_def: "{{(lookup('vars', 'application_definition'))}}"
      roles:
        - mockfog_application