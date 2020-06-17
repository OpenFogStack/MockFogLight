# mockfog_network

Configures the network using the hostvars set by mockfog_topology.
The respective playbook is placed in the parent directory.

### Requirements

- needs to be run after mockfog_toplogy --tags bootstrap

### Role Variables

A playbook needs to be run with the following parameters:

```bash
--key-file=XXXX
--ssh-common-args="-o StrictHostKeyChecking=no"
```

Assume that the playbook supplies the testbed definition in the form of a vars file.
