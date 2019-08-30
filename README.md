# MockFog Light

This project aims to provide a light version of [MockFog](https://github.com/OpenFogStack/MockFog-Meta) without a graphical user interface and the option to update characteristics at runtime to improve stability.
Thus, it should be mainly used to create an infrastructure testbed.

Code is largely based on the MockFog adoption of (flonix8)[https://github.com/flonix8/master-thesis-experiment].

**Related Publication**:
Jonathan Hasenburg, Martin Grambow, Elias Grünewald, Sascha Huk, David Bermbach. **MockFog: Emulating Fog Computing Infrastructure in the Cloud**. In: Proceedings of the First IEEE International Conference on Fog Computing 2019 (ICFC 2019). IEEE 2019. [Bib](http://www.mcc.tu-berlin.de/fileadmin/fg344/publications/2019-02-11_mockfog.bib). [PDF](http://www.mcc.tu-berlin.de/fileadmin/fg344/publications/2019-02-11_mockfog.pdf).


### Requirements
Before running any roles, you should setup a virtualenv and install all requirements

```fish
virtualenv venv
source venv/bin/activate.fish
pip install -r requirements.txt
```

In addition:
- aws credentials configured in `~/.aws/config`
- valid AWS ssh key stored at `./mockfog.pem`

### Create Testbed Definition

- configure the topology via `testbed/topologies.py`
- create the testbed definition with `python testbed/generate_testbed_definition.py`

### MockFog Topology

- bootstraps (or destroys) an AWS infrastructure based on the generated testbed definition
- adds the **testbed_config** field to hostvars; useable via other roles and templates, e.g., `hostvars[inventory_hostname].testbed_config.bandwidth_out` (actually done on the fly via `ec2.py`)
- sets the name, internal_ip, and role tag of EC2 instances

```fish
ansible-playbook --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_topology.yml --tags bootstrap
ansible-playbook --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_topology.yml --tags destroy
```
# MockFog Network

- configures delays via TC

```fish
ansible-playbook -i inventory/ec2.py --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_network.yml
```

# MockFog Rollout

- rolls out application and starts it

```fish
ansible-playbook -i inventory/ec2.py --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_rollout.yml
```
