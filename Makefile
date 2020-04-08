.PHONY: install clean

VENV=.env/bin/activate
# The AWS ssh key. Default is mockfog.pem
KEY=mockfog.pem
# AWS ssh key on AWS (not the file name but the resource name)
KEY_NAME=mockfog

install: clean
	python3 -m venv .env
	.env/bin/pip3 install -r requirements.txt

generate:
	. $(VENV); cd topology; python3 generate.py ../topology.json

show:
	. $(VENV); cd topology; python3 show.py ../topology.json

deploy: vars.yml topology/testbed_definition.yml
	. $(VENV); cp vars.yml deploy/vars/main.yml
	. $(VENV); DYLD_FALLBACK_LIBRARY_PATH=/usr/local/opt/openssl/lib ansible-playbook --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" --extra-vars "ssh_key_name=$(KEY_NAME)" deploy.yml --tags bootstrap

network: topology/testbed_definition.yml
	. $(VENV); DYLD_FALLBACK_LIBRARY_PATH=/usr/local/opt/openssl/lib ansible-playbook -i inventory/ec2.py --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" network.yml

prepare: topology/testbed_definition.yml
	. $(VENV); DYLD_FALLBACK_LIBRARY_PATH=/usr/local/opt/openssl/lib ansible-playbook -i inventory/ec2.py --key-file=$(KEY)  --ssh-common-args="-o StrictHostKeyChecking=no" prepare.yml --tags prepare

application: prepare topology/testbed_definition.yml
	. $(VENV); DYLD_FALLBACK_LIBRARY_PATH=/usr/local/opt/openssl/lib ansible-playbook -i inventory/ec2.py --key-file=$(KEY)  --ssh-common-args="-o StrictHostKeyChecking=no" application.yml --tags deploy

collect: 
	. $(VENV); DYLD_FALLBACK_LIBRARY_PATH=/usr/local/opt/openssl/lib ansible-playbook -i inventory/ec2.py --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" application.yml --tags collect

destroy:
	. $(VENV); DYLD_FALLBACK_LIBRARY_PATH=/usr/local/opt/openssl/lib ansible-playbook --key-file=$(KEY) --ssh-common-args="-o StrictHostKeyChecking=no" deploy.yml --tags destroy

mockfog: generate deploy network prepare application

clean:
	rm -rf .env/
	rm -rf mapping.*
	rm -rf deploy/vars/main.yml
	rm -rf topology/testbed_definition.yml
	rm -rf application/vars/mapping.yml