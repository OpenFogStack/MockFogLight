import json
import logging
import re
import sched
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

import docker
import docker.errors


class ContainerStatus:
    def __init__(self, name):
        self.name = name
        self.memory_limit = "256"
        self.cpu_shares = "1024"
        self.connections = {}

    def get_name(self):
        return self.name

    def get_memory_limit(self):
        return self.memory_limit

    def set_memory_limit(self, memory_limit):
        self.memory_limit = memory_limit

    def get_cpu_shares(self):
        return self.cpu_shares

    def set_cpu_shares(self, cpu_shares):
        self.cpu_shares = cpu_shares

    def to_json_app(self):
        return """{
        "memory_limit": "%s",
        "cpu_shares": "%s",
    }""" % (self.memory_limit, self.cpu_shares)


class InterfaceStatus:
    def __init__(self, interface):
        self.interface = interface
        self.bandwidth = ""
        self.latency = "0.0ms"
        self.packet_loss = "0"
        self.active = "true"

    def get_interface(self):
        return self.interface

    def set_interface(self, interface):
        self.interface = interface

    def get_active(self):
        return self.active

    def set_active(self, active):
        self.active = active

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth

    def get_latency(self):
        return self.latency

    def set_latency(self, latency):
        self.latency = latency

    def get_packet_loss(self):
        return self.packet_loss

    def set_packet_loss(self, packet_loss):
        self.packet_loss = packet_loss

    def update_values(self):
        """ The result of tcshow looks like the following """
        """ {
            "docker0": {
                "outgoing": {
                    "dst-network=192.168.0.10/32, dst-port=8080, protocol=ip": {
                        "filter_id": "800::800",
                        "delay": "10.0ms",
                        "delay-distro": "2.0ms",
                        "loss": "0.01%",
                        "rate": "250Kbps"
                    }
                },
                "incoming": {
                    "protocol=ip": {
                        "filter_id": "800::800",
                        "delay": "1.0ms",
                        "loss": "0.02%",
                        "rate": "500Kbps"
                    }
                }
            }
        }"""

        try:
            result = subprocess.run(["tcshow", self.interface], stdout=subprocess.PIPE)
            data = json.loads(result.stdout)
            for _, values in data[self.interface]["outgoing"].items():
                if "delay" in values:
                    self.latency = values["delay"]
                if "loss" in values:
                    self.packet_loss = values["loss"]
                if "rate" in values:
                    self.bandwidth = values["rate"]
        except:
            print("'tcshow' failed, using saved values")

    def to_json_interface(self):
        self.update_values()

        return """{
        "bandwidth": "%s",
        "latency": "%s",
        "packet_loss": "%s",
        "active" : "%s",
    }""" % (self.bandwidth, self.latency, self.packet_loss, self.active)


class AgentStatus:
    def __init__(self):
        self.interface = InterfaceStatus("docker0")
        self.containers = {
        }

    def set_container(self, container_name):
        if not (container_name in self.containers):
            self.containers[container_name] = ContainerStatus(container_name)

    def get_container(self, container_name):
        return self.containers[container_name]

    def set_interface(self, interface_id):
        self.interface = InterfaceStatus(interface_id)

    def get_interface(self):
        return self.interface

    def to_json(self):
        json = "{\n    "
        i = 0

        if not self.containers:
            if i != 0:
                json += ',\n    '

            json += '"%s": ' % ("")
            json += ContainerStatus("").to_json_app()
            i += 1

            json += "\n\n    "
            json += '"%s": ' % (self.get_interface().interface)
            json += self.get_interface().to_json_interface()
            i += 1
            json += "\n}\n"
            return json


        for name, container in self.containers.items():
            if i != 0:
                json += ',\n    '

            json += '"%s": ' % (name)
            json += container.to_json_app()
            i += 1

            json += "\n\n    "
            json += '"%s": ' % (self.get_interface().interface)
            json += self.get_interface().to_json_interface()
            i += 1

        json += "\n}\n"
        return json


class Docker(object):
    __docker_client = docker.from_env()

    def __init__(self, status, name='docker'):
        self.name = name
        self.status = status

    def run(self, container_image, container_name):
        self.__docker_client.containers.run(image=container_image, name=container_name, detach=True,
                                            cpuset_cpus="0",
                                            mem_limit="256m")

    def update_memory_limit(self, container_name, mem_limit):
        """
        Update the memory limit by container name.
        :param container_name:
        :param mem_limit:
        :return:
        """
        try:
            container = self.__docker_client.containers.get(container_name)
            container.update(mem_limit=mem_limit, memswap_limit=mem_limit)
            self.status.set_container(container_name)
            self.status.get_container(container_name).set_memory_limit(mem_limit)
        except docker.errors.NotFound:
            logging.warning(container_name + ": not found on this host")
        except docker.errors.APIError as err:
            logging.warning("Failed to update " + container_name, err)

    def update_cpu_shares(self, container_name, cpu_shares):
        """
        Update the cpu shares by container name.

        :param container_name:
        :param cpu_shares:
            Set this flag to a value greater or less than the default of 1024 to increase or reduce the container’s
            weight, and give it access to a greater or lesser proportion of the host machine’s CPU cycles.
            This is only enforced when CPU cycles are constrained.
            When plenty of CPU cycles are available, all containers use as much CPU as they need.
            In that way, this is a soft limit. --cpu-shares does not prevent containers from being scheduled in
            swarm mode. It prioritizes container CPU resources for the available CPU cycles.
            It does not guarantee or reserve any specific CPU access.
            Specification from https://docs.docker.com/config/containers/resource_constraints/
        :return:
        """
        try:
            container = self.__docker_client.containers.get(container_name)
            container.update(cpu_shares=cpu_shares)
            self.status.set_container(container_name)
            self.status.get_container(container_name).set_cpu_shares(cpu_shares)
        except docker.errors.NotFound:
            logging.warning(container_name + ": not found on this host")
        except docker.errors.APIError as err:
            logging.warning("Failed to update " + container_name, err)

    def connect(self, docker_network, container_name):
        """
        Connect the container to specified network.
        :param docker_network: default is bridge
        :param container_name:
        :return:
        """
        try:
            network = self.__docker_client.networks.get(docker_network)
            network.connect(container=container_name)
            self.status.get_container(container_name).set_connection_status(
                docker_network, "connected")
        except docker.errors.NotFound:
            logging.warning(docker_network + ": not found")
        except docker.errors.APIError as err:
            logging.warning("Failed to connect " + container_name + " to " + docker_network, err)

    def disconnect(self, docker_network, container_name):
        """
        Disconnect the container from specified network.
        :param docker_network: default is bridge
        :param container_name:
        :return:
        """
        try:
            network = self.__docker_client.networks.get(docker_network)
            network.disconnect(container=container_name)
            self.status.get_container(container_name).set_connection_status(
                docker_network, "disconnected")
        except docker.errors.NotFound:
            logging.warning(docker_network + ": not found")
        except docker.errors.APIError as err:
            logging.warning("Failed to disconnect " + container_name + " from " + docker_network, err)

    def networks(self):
        for network in self.__docker_client.networks.list():
            print(network.name + ':')
            for container in network.containers:
                print(container.name)

    def stop_all_containers(self):
        for container in self.__docker_client.containers.list():
            container.stop()


class Tc(object):
    def __init__(self, status, name='tc'):
        self.name = name
        self.status = status

    def interface(self, interface, **kwargs):
        """
        Add interface configuration.
        :param interface:
        :param kwargs:

        Args:
            bandwidth (str): network bandwidth rate [bit per second]. the minimum
                bandwidth rate is 8 bps. valid units are either: bps,
                bit/s, [kK]bps, [kK]bit/s, [kK]ibps, [kK]ibit/s,
                [mM]bps, [mM]bit/s, [mM]ibps, [mM]ibit/s, [gG]bps,
                [gG]bit/s, [gG]ibps, [gG]ibit/s, [tT]bps, [tT]bit/s,
                [tT]ibps, [tT]ibit/s. e.g. tcset eth0 --rate 10Mbps
            delay (str): round trip network delay. the valid range is from 0ms
                to 60min. valid time units are: d/day/days,
                h/hour/hours, m/min/mins/minute/minutes,
                s/sec/secs/second/seconds,
                ms/msec/msecs/millisecond/milliseconds,
                us/usec/usecs/microsecond/microseconds. if no unit
                string found, considered milliseconds as the time
                unit. default "0ms"
            loss (str): round trip packet loss rate [%]. the valid range is
                from 0 to 100. default "0"

        :return:
        """
        bandwidth = kwargs.pop('bandwidth', None)
        delay = kwargs.pop('delay', None)
        loss = kwargs.pop('loss', None)

        self.status.set_interface(interface)
        interface_args = ["tcset", interface]
        if bandwidth:
            interface_args.extend(["--rate", bandwidth])
            self.status.get_interface().set_bandwidth(bandwidth)
        if delay:
            interface_args.extend(["--delay", delay])
            self.status.get_interface().set_latency(delay)
        if loss:
            interface_args.extend(["--loss", loss])
            self.status.get_interface().set_packet_loss(loss)

        # add overwrite flag to be able to update existing rules.
        interface_args.append("--overwrite")
        try:
            # print the executed command arguments
            print(" ".join(interface_args))
            logging.debug(" ".join(interface_args))
            if len(interface_args) > 3:
                subprocess.run(interface_args, check=True)
            else:
                print("command not executed insufficient arguments")
        except subprocess.CalledProcessError as err:
            logging.error(err)

    # TODO: There seems to be an issue with the "--change" flag. It overrides the whole rule instead of updating one
    #  field.
    def update_bandwidth(self, interface, bandwidth):
        """
        Configure the available bandwidth for the default docker0 interface.

        :param interface:
        :param bandwidth:
        :return:
        """
        subprocess.run(["tcset", interface, "--rate", bandwidth, "--change"], check=True)

    def show_rules(self, interface):
        print(subprocess.run(["tcshow", interface], check=True))

    def reset_interface(self, interface):
        try:
            subprocess.run(["tcdel", interface, "--all"], check=True)
        except subprocess.CalledProcessError:
            # TODO: add explanation on why we pass the error here.
            pass

    def disable(self, interface):
        """
        Disable interface. Requires root permission.
        :param interface:
        :return:
        """
        try:
            subprocess.run(["ip", "link", "set", interface, "down"], check=True)
            self.status.get_interface().set_active('false')
        except subprocess.CalledProcessError:
            logging.warning("Insufficient permissions")

    def enable(self, interface):
        """
        Enable interface. Requires root permission.

        :param interface:
        :return:
        """
        try:
            subprocess.run(["ip", "link", "set", interface, "up"], check=True)
            self.status.get_interface().set_active('true')
        except subprocess.CalledProcessError:
            logging.warning("Insufficient permissions")


class Agent(object):

    def __init__(self, name='agent'):
        self.status = AgentStatus()
        self.name = name
        self.docker = Docker(self.status)
        self.tc = Tc(self.status)


class WebServerHandler(BaseHTTPRequestHandler):
    _agent = Agent()
    _stage_report = {}
    _last_scheduled_timestamp = None

    @staticmethod
    def _update_report(stage_id):
        WebServerHandler._stage_report[str(stage_id)] = WebServerHandler._agent.status.to_json()

    def do_POST(self):
        if len(WebServerHandler._stage_report) == 0:
            print("Set stage 0 report")
            WebServerHandler._stage_report["0"] = WebServerHandler._agent.status.to_json()
        self.send_response(200)
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']

        if content_type != 'application/json':
            print("Wrong content type,json expected!")
            return

        body = self.rfile.read(content_length)
        response = BytesIO()
        response.write(b'Received: ' + body + b'\n')
        self.end_headers()

        content_string = body.decode('utf-8')
        content_json_array = json.loads(content_string)

        scheduler = sched.scheduler(time.time, time.sleep)

        for event in content_json_array:
            stage_id = event['id']
            scheduled_time = int(event['timestamp']) / 1000.0
            scheduler.enterabs(scheduled_time, 0, lambda: do_action(self.path, WebServerHandler._agent, event))
            scheduler.enterabs(scheduled_time + 1, 0, lambda :self._update_report(stage_id))


        threading.Thread(target=scheduler.run).start()

    def do_GET(self):
        print(WebServerHandler._stage_report)
        match = re.match(r'/reports/(.+)', self.path)
        if match:
            self.send_response(200)
            self.end_headers()
            stage_id = match.group(1)
            self.wfile.write(WebServerHandler._stage_report[stage_id].encode())
        else:
            self.send_error(404)
            self.end_headers()


def do_action(path, agent, content_json_array):
    content_dict = content_json_array['data']

    if path == "/application":
        modify_application(agent, content_dict)

    if path == "/interface":
        modify_interface(agent, content_dict)


def modify_application(agent, content_dict):
    """
    Apply modifications to specified application from scheduled event.
    :param agent:
    :param content_dict:
    :return:
    """

    if 'cpu' in content_dict:
        agent.docker.update_cpu_shares(content_dict['name'], content_dict['cpu'])

    if 'memory' in content_dict:
        agent.docker.update_memory_limit(content_dict['name'], content_dict['memory'])


def modify_interface(agent, content_dict):
    """
    Apply modifications to specified interface from scheduled event.
    :param agent:
    :param content_dict:
    :return:
    """
    agent.tc.interface(content_dict['id'], **content_dict)

    if content_dict.get('active', None):
        agent.tc.enable(content_dict['id'])
    else:
        agent.tc.disable(content_dict['id'])

def main():
    port = 20200
    server = HTTPServer(('', port), WebServerHandler)
    print("Web server is running on port {}".format(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()


if __name__ == '__main__':
    main()
