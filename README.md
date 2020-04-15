# MockFog Light

This project is part of MockFog which includes the following sub projects:

- [MockFog-Meta](https://github.com/OpenFogStack/MockFog-Meta) Meta repository with a presentation and a demo video
- [MockFog-IaC](https://github.com/OpenFogStack/MockFog-IaC) MockFog Infrastructure as Code artifacts
- [MockFog-NodeManager](https://github.com/OpenFogStack/MockFog-NodeManager) MockFog Node Manager
- [MockFog-Agent](https://github.com/OpenFogStack/MockFog-Agent) MockFog Agent
- [MockFogLight](https://github.com/OpenFogStack/MockFogLight) A lightweight version of MockFog without a visual interface

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

To use MockFog, the following steps need to be completed:

1. Install requirements
1. Create a topology
1. Generate a testbed definition from the topology
1. Deploy the testbed definition as AWS EC2 machines
1. Configure network settings for machines
1. Deploy applications to machines

You can use `make mockfog` as a shorthand but it is recommended to familiarize yourself with the details as described below.

### Install Requirements

MockFogLight requires `Pyhon3`, `pip` and `virtualenv`. You can install `virtualenv` with `pip install virtualenv`.
Other requirements can be installed automatically with:

```bash
make install
```

Furthermore, you should have AWS credentials configured in `~/.aws/credentials` (you can use `aws configure` if you have the AWS CLI installed). You should also have an AWS SSH key stored at `./mockfog.pem` that is valid for your selected region (don't forget to make it usable with `chmod 400 mockfog.pem` !)

### Create Topology

A topology can be created using a simple JSON file. An example is given in [topology/topology.json](topology/topology.json). The format follows that of [FogExplorer](https://github.com/OpenFogStack/FogExplorer).

### Generate Testbed Definition

A testbed definition can be generated from the topology file with:

```bash
make generate
```

To show a graph of your topology so you can check that everything looks as expected use:

```bash
make show
```

Please note that `make` will use [topology/topology.json](topology/topology.json) as a topology file so name your file correctly.

### Deploy Testbed Definition to AWS EC2

You will first need to set up your variable file by changing [vars.yml](./vars.yml). Here, set your preferred AWS region and AWS EC2 AMI. We strongly recommend Amazon Linux 2 as an operating system. Be sure that the AMI and key file you provide fit the region you specify.

With your testbed definition ready, you can now move on to the deploy phase with:

```bash
make deploy
```

### Configure Network Settings

Next up are network details which can be deployed with:

```bash
make network
```

### Deploy Application

Finally your application can be deployed with:

```bash
make prepare
make application
```

Your application should be a Docker container that is available on Docker hub as `{{ repo_name }}/{{ service_name }}` with `repo_name` as configured in `vars.yml`. `service_name` is taken from modules of your `topology.json`. These applications should expose ports as specified in the environment variables, these will be bound directly to the host interface.

Inside the container, addresses and ports of other services are available as environment variables in the form of `{{ SERVICE_NAME }}_IP` and `{{ SERVICE_NAME }}_PORT` (note that `SERVICE_NAME` is all uppercase). Note that ports are mapped regardless of whether your container actually uses them.

You can collect application logs with `make collect`.
