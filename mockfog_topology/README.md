mockfog_toplogy
=========

The respective playbook is placed in the parent directory.

Tags:
- bootstrap: setup environment
- destroy: destroy environment

### Requirements

- vars configured in `vars/main.yml`
    - The AMI should be based on Amazon Linux 2. Needed packages:
        * TC (z.B. iproute-tc)
        * Docker
        * Python und Pip
- testbed generated and supplied as vars file

### Role Variables

Assumes that the playbook supplies the testbed definition in the form of a vars file.

A playbook needs to be run with the following parameters:
```bash
--key-file=XXXX
--ssh-common-args="-o StrictHostKeyChecking=no"
```
