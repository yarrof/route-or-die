#!/usr/bin/python
from ipaddress import IPv4Network
from itertools import chain
from mininet.cli import CLI
from mininet.log import setLogLevel, info, output
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from re import match
from sys import argv, maxint
import argparse
import random


class NoIPv6Node(Node):
    def config(self, **params):
        super(NoIPv6Node, self).config(**params)
        self.cmd("sysctl net.ipv6.conf.all.disable_ipv6=1")
        self.cmd("sysctl net.ipv6.conf.default.disable_ipv6 = 1")

    def terminate(self):
        self.cmd("sysctl net.ipv6.conf.all.disable_ipv6=0")
        self.cmd("sysctl net.ipv6.conf.default.disable_ipv6=0")
        super(NoIPv6Node, self).terminate()


class LinuxRouter(NoIPv6Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    @staticmethod
    def get_subnets(networks, prefix, number):
        results = []
        for network in networks:
            for subnet in random.sample(
                list(network.subnets(new_prefix=prefix)), number
            ):
                results.append(subnet)
        return random.sample(results, number)

    def __init__(self):
        self.next_net_id = 1
        self.wan_subnet_pool = self.get_subnets([privnet_a, privnet_b], 16, 5)
        self.lan_subnet_pool = self.get_subnets([privnet_c], 24, 5)
        self.host_pool = {}
        self.all_subnets = {}
        self.all_hosts = {}
        super(NetworkTopo, self).__init__()

    def build(self, **_opts):
        r1 = self.define_network(3)
        r2 = self.define_network(1)
        r3 = self.define_network(2)
        r4 = self.define_network(2)
        r5 = self.define_network(2)

        self.define_link(r1, r2, 1)
        self.define_link(r1, r3, 2)
        self.define_link(r2, r3, 3)
        self.define_link(r2, r4, 4)
        self.define_link(r4, r5, 5)

    def define_network(self, hosts_num):
        net_id, subnet, hosts = self.make_net(self.lan_subnet_pool)
        router_ip = hosts.pop(0)
        router = self.addHost(
            "r" + net_id,
            cls=LinuxRouter,
            ip=str(router_ip) + "/" + str(subnet.prefixlen),
        )
        switch = self.addSwitch("s" + str(net_id))
        self.addLink(switch, router)
        for n in range(1, hosts_num + 1):
            host_id, host_ip = self.make_host(net_id, n)
            host = self.addHost(
                name="h" + host_id,
                cls=NoIPv6Node,
                ip=str(host_ip) + "/" + str(subnet.prefixlen),
                defaultRoute="via " + str(router_ip),
            )
            self.addLink(host, switch)
        return router

    def define_link(self, router_a, router_b, network_id):
        net_id, subnet, hosts = self.make_net(self.wan_subnet_pool)
        self.addLink(
            router_a,
            router_b,
            intfName1=self.next_intf(router_a),
            intfName2=self.next_intf(router_b),
            params1={"ip": str(hosts.pop(0)) + "/" + str(subnet.prefixlen)},
            params2={"ip": str(hosts.pop(0)) + "/" + str(subnet.prefixlen)},
        )

    def make_net(self, subnet_pool):
        net_id = str(self.next_net_id)
        self.next_net_id += 1
        subnet = subnet_pool.pop(random.randrange(len(subnet_pool)))
        hosts = list(subnet.hosts())
        self.host_pool[net_id] = hosts
        self.all_subnets[net_id] = subnet
        return net_id, subnet, hosts

    def make_host(self, net_id, n):
        host_id = net_id + str(n)
        hosts = self.host_pool[net_id]
        host = hosts.pop(random.randrange(len(hosts)))
        if net_id not in self.all_hosts:
            self.all_hosts[net_id] = {}
        self.all_hosts[net_id][host_id] = host
        return host_id, host

    def all_intfs(self):
        "Collects all network interface names for all router nodes."
        all_intfs = {}
        for r in self.nodes():
            if r[0] != "r":
                continue
            intfs = [r + "-eth0"]
            for left, right in self.links():
                if left[0] != "r" or right[0] != "r":
                    continue
                if left != r and right != r:
                    continue
                link_info = self.linkInfo(left, right)
                for key in link_info:
                    if not key.startswith("intfName"):
                        continue
                    intf = link_info[key]
                    if intf.startswith(r + "-"):
                        intfs.append(intf)
            intfs.sort()
            all_intfs[r] = intfs
        return all_intfs

    def next_intf(self, r):
        "Determines the next available network interface name for the 'r' router node."
        intfs = self.all_intfs()
        last_intf = intfs[r][-1]
        idx = last_intf.index("-") + len("eth")
        last_num = int(last_intf[idx + 1 :])
        return r + "-eth" + str(last_num + 1)

    def define_routing(self, router, other_routers):
        default_router = other_routers[0]
        other_routers = other_routers[1:]


def run_commands(net, task):
    ini = "task{}.ini".format(task)
    output("*** Running commands from: {}\n".format(ini))
    with open(ini) as f:
        lines = f.readlines()
    for line in lines:
        if match(r"^\s*(?:(?:#|;).*)?$", line):
            continue
        line = line.strip()
        parts = line.split(None, 1)
        target = parts[0]
        output("{} -> {}\n".format(target, line[len(target) + 1:]))
        if target not in net:
            output("No such node: {}\n".format(target))
        else:
            command = parts[1] if len(parts) == 2 else None
            output("{}".format(net[target].cmd(command)))


def seed(value):
    output("*** Using seed: {}".format(value) + "\n")
    random.seed(value)


def test(net, task):
    txt = "test{}.txt".format(task)
    output("*** Running tests from: {}\n".format(txt))
    hosts = []
    with open(txt) as f:
        for line in f.readlines():
            line = line.strip()
            for host in line.split():
                host = host.strip()
                hosts.append(host)
    net.ping([h for h in net.hosts if h.name in hosts])


def run():
    def task_type(x):
        x = int(x)
        if x < 1 or x > 6:
            raise argparse.ArgumentTypeError("must be between 1 and 6")
        return x

    def seed_type(x):
        x = int(x)
        if x == maxint:
            # Ssshhh! Secret!
            return x
        if x < 1000 or x > 9999:
            raise argparse.ArgumentTypeError("must be between 1000 and 9999")
        return x

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=seed_type, default=random.randint(1000, 9999))
    parser.add_argument("--task", type=task_type)
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        setLogLevel("info")
    seed(args.seed)
    topo = NetworkTopo()
    net = Mininet(topo=topo)
    if args.task:
        run_commands(net, args.task)
    net.start()
    if args.test:
        test(net, args.task)
    else:
        CLI(net)
    net.stop()


# https://en.wikipedia.org/wiki/Private_network#Private_IPv4_addresses
privnet_a = IPv4Network(u"10.0.0.0/8")
privnet_b = IPv4Network(u"172.0.0.0/12")
privnet_c = IPv4Network(u"192.168.0.0/16")


if __name__ == "__main__":
    run()
