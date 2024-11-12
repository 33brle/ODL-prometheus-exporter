#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import sys

def fat_tree_topology(controller_ip, controller_port, k=4):
    """
    Creates a fat-tree topology with parameter k.
    
    Args:
        controller_ip (str): IP address of the SDN controller.
        controller_port (int): Port number of the SDN controller.
        k (int): Parameter defining the size of the fat-tree (must be even).
    """

    if k % 2 != 0:
        print("k must be an even integer")
        sys.exit(1)

    net = Mininet(controller=None, switch=OVSKernelSwitch, autoSetMacs=True)

    # Add the remote controller
    c0 = net.addController('c0', controller=RemoteController, ip=controller_ip, port=controller_port)

    # Lists to hold switches and hosts
    core_switches = []
    agg_switches = []
    edge_switches = []
    hosts = []

    def set_switch_protocols(switch):
        """Set the switch to use only OpenFlow13."""
        switch.cmd('ovs-vsctl set bridge {} protocols=OpenFlow13'.format(switch.name))
        switch.cmd('ovs-vsctl set bridge {} other-config:enable-flush=true'.format(switch.name))

    # Calculate the number of pods
    pods = k

    # Create Core Switches
    for i in range((k // 2) ** 2):
        switch_name = f'c{i + 1}'
        dpid = '00{:02x}'.format(i + 1).zfill(16)
        switch = net.addSwitch(switch_name, dpid=dpid, protocols='OpenFlow13')
        core_switches.append(switch)
        info(f"Added Core Switch {switch_name}\n")
        set_switch_protocols(switch)

    # Create Aggregation and Edge Switches
    for pod in range(pods):
        agg = []
        edge = []

        # Aggregation Switches
        for i in range(k // 2):
            switch_name = f'a{pod + 1}_{i + 1}'
            dpid = '01{:02x}{:02x}'.format(pod + 1, i + 1).zfill(16)
            switch = net.addSwitch(switch_name, dpid=dpid, protocols='OpenFlow13')
            agg.append(switch)
            info(f"Added Aggregation Switch {switch_name}\n")
            set_switch_protocols(switch)
        agg_switches.append(agg)

        # Edge Switches
        for i in range(k // 2):
            switch_name = f'e{pod + 1}_{i + 1}'
            dpid = '02{:02x}{:02x}'.format(pod + 1, i + 1).zfill(16)
            switch = net.addSwitch(switch_name, dpid=dpid, protocols='OpenFlow13')
            edge.append(switch)
            info(f"Added Edge Switch {switch_name}\n")
            set_switch_protocols(switch)
        edge_switches.append(edge)

        # Connect Edge Switches to Hosts
        for edge_switch in edge:
            for h in range(2):  # Number of hosts per edge switch
                host_name = f'h{edge_switch.name}_{h + 1}'
                host = net.addHost(host_name)
                net.addLink(host, edge_switch)
                hosts.append(host)
                info(f"Added Host {host_name} connected to {edge_switch.name}\n")

    # Connect Aggregation Switches to Edge Switches
    for pod in range(pods):
        for agg_switch in agg_switches[pod]:
            for edge_switch in edge_switches[pod]:
                net.addLink(agg_switch, edge_switch)
                info(f"Linked {agg_switch.name} to {edge_switch.name}\n")

    # Connect Core Switches to Aggregation Switches
    for i, core_switch in enumerate(core_switches):
        for pod in range(pods):
            agg_switch = agg_switches[pod][i // (k // 2)]
            net.addLink(core_switch, agg_switch)
            info(f"Linked Core {core_switch.name} to Aggregation {agg_switch.name}\n")

    # Build and start the network
    net.build()
    c0.start()
    for switch in net.switches:
        switch.start([c0])

    # Wait for switches to connect
    net.waitConnected()

    # Start the CLI
    CLI(net)

    # Stop the network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    if len(sys.argv) != 4:
        print("Usage: sudo python3 fat_tree_topology.py <controller-ip> <controller-port> <k>")
        sys.exit(1)

    # Retrieve arguments
    controller_ip = sys.argv[1]
    controller_port = int(sys.argv[2])
    k = int(sys.argv[3])

    # Create the fat-tree topology
    fat_tree_topology(controller_ip, controller_port, k)
