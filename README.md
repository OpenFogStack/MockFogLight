# MockFog Light

This project is part of MockFog which includes the following subprojects:
* [MockFog-Meta](https://github.com/OpenFogStack/MockFog-Meta) Meta repository with a presentation and a demo video
* [MockFog-IaC](https://github.com/OpenFogStack/MockFog-IaC) MockFog Infrastructure as Code artifacts
* [MockFog-NodeManager](https://github.com/OpenFogStack/MockFog-NodeManager) MockFog Node Manager
* [MockFog-Agent](https://github.com/OpenFogStack/MockFog-Agent) MockFog Agent
* [MockFogLight](https://github.com/OpenFogStack/MockFogLight) A lightweight version of MockFog without a visual interface

Fog computing is an emerging computing paradigm that uses processing and storage capabilities located at the edge, in the cloud, and possibly in between. Testing fog applications, however, is hard since runtime infrastructures will typically be in use or may not exist, yet.
MockFog is a tool that can be used to emulate such infrastructures in the cloud. Developers can freely design emulated fog infrastructures, configure their performance characteristics, and inject failures at runtime to evaluate their application in various deployments and failure scenarios.

If you use this software in a publication, please cite it as:

### Text
Jonathan Hasenburg, Martin Grambow, Elias Grünewald, Sascha Huk, David Bermbach. **MockFog: Emulating Fog Computing Infrastructure in the Cloud**. In: Proceedings of the First IEEE International Conference on Fog Computing 2019 (ICFC 2019). IEEE 2019.

### BibTeX
```
@inproceedings{hasenburg_mockfog:_2019,
	title = {{MockFog}: {Emulating} {Fog} {Computing} {Infrastructure} in the {Cloud}},
	booktitle = {Proceedings of the First {IEEE} {International} {Conference} on {Fog} {Computing} 2019 (ICFC 2019)},
	author = {Hasenburg, Jonathan and Grambow, Martin and Grunewald, Elias and Huk, Sascha and Bermbach, David},
	year = {2019},
	publisher = {IEEE}
}
```

A full list of our [publications](https://www.mcc.tu-berlin.de/menue/forschung/publikationen/parameter/en/) and [prototypes](https://www.mcc.tu-berlin.de/menue/forschung/prototypes/parameter/en/) is available on our group website.

## Instructions

This project aims to provide a light version of [MockFog](https://github.com/OpenFogStack/MockFog-Meta) without a graphical user interface and the option to update characteristics at runtime to improve stability.
Thus, it should be mainly used to create an infrastructure testbed.

Code is largely based on the MockFog adoption of (flonix8)[https://github.com/flonix8/master-thesis-experiment].

### Requirements
Before running any roles, make sure `python` and `virtualenv` are installed

In addition:
- aws credentials configured in `~/.aws/credentials`
- valid AWS ssh key stored at `./mockfog.pem`
- read the individual READMEs for each role -> do what they say
- in Makefile set AWS ssh KEY parameter to `mockfog.pem`.

### Running MockFogLight

- Setup python virtualenv and install dependencies - `make build`
- Run all MockFogLight tasks - `make mockfog`
- Destroy all running AWS instances - `make destroy`
- Clean build - `make clean`

See later sections for detailed information about running specific tasks:

#### Create Testbed Definition

- configure the topology via `testbed/topology_definition.yml`
- create the testbed definition with `make topology` or run `python testbed/generate_testbed_definition.py`

#### MockFog Topology
This role:
- bootstraps (or destroys) an AWS infrastructure based on the generated testbed definition
- adds the **testbed_config** field to hostvars; useable via other roles and templates, e.g., `hostvars[inventory_hostname].testbed_config.bandwidth_out` (actually done on the fly via `ec2.py`)
- sets the name, internal_ip, and role tag of EC2 instances

Use with:
- To deploy topology to AWS - `make bootstrap`
- To destroy topology - `make destroy`

or alternatively execute the following commands:
```fish
ansible-playbook --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_topology.yml --tags bootstrap
ansible-playbook --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_topology.yml --tags destroy
```
#### MockFog Network
This role:
- configures delays via TC
Use with:
```fish
ansible-playbook -i inventory/ec2.py --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_network.yml
```

#### MockFog Info
This role:
- Fetches MockFog instance metadata and tags mapping
- Data is stored in `mapping.yml` in the project directory

Use with:
- `make info`

or alternatively, execute
```
ansible-playbook -i inventory/ec2.py --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_info.yml
```

#### MockFog Agent
This role:
- deploys MockFog agent on nodes and starts it

Use with:
- `make agent`

or alternatively, execute
```fish
ansible-playbook -i inventory/ec2.py --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_application.yml --tags deploy_agent
```

#### MockFog Application
This role:
- deploys application on nodes and starts it
- collects logs

Use with:
- `make application`

or alternatively, execute
```fish
ansible-playbook -i inventory/ec2.py --key-file=mockfog.pem --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_application.yml --tags deploy
```
