.PHONY: build clean

VENV=.env/bin/activate
# The AWS ssh key. Default is mockfog.pem
KEY=mockfog.pem

build: clean
	python3 -m venv .env
	.env/bin/pip3 install -r requirements.txt

topology:
	. $(VENV); cd testbed; python3 generate_testbed_definition.py

bootstrap:
	. $(VENV); ansible-playbook --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_topology.yml --tags bootstrap

info:
	. $(VENV); ansible-playbook -i inventory/ec2.py --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_info.yml

agent:
	. $(VENV); ansible-playbook -i inventory/ec2.py --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_application.yml --tags deploy_agent

application:
	. $(VENV); ansible-playbook -i inventory/ec2.py --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_application.yml --tags deploy

destroy:
	. $(VENV); ansible-playbook --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" mockfog_topology.yml --tags destroy

mockfog: bootstrap info agent application

clean:
	rm -rf .env/
	rm -rf mapping.*
	rm -rf testbed/testbed_definition.yml
	rm -rf mockfog_app lication/vars/mapping.yml