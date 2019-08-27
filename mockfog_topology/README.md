mockfog_toplogy
=========

The respective playbook is placed in the parent directory.

### Requirements

- vars configured in `vars/main.yml`
    - The AMI should be based on Amazon Linux 2. Needed packages:
        * TC (z.B. iproute-tc)
        * Docker
        * Python und Pip

### Role Variables

A playbook needs to be run with the following parameters:
```bash
--key-file=XXXX
--ssh-common-args="-o StrictHostKeyChecking=no"
```

Assume that the playbook supplies the testbed definition in the form of a vars file.
