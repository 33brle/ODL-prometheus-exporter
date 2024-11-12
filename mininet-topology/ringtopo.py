from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
import sys

def ring_topology(controller_ip, controller_port, num_hosts):
    """
    Create a ring topology in Mininet with a remote SDN controller.

    Args:
        controller_ip (str): The IP address of the SDN controller.
        controller_port (int): The port number of the SDN controller.
        num_hosts (int): The number of hosts to create.
    """
    # Create the Mininet instance
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)

    # Add the remote controller with the supplied IP and port
    c0 = net.addController('c0', controller=RemoteController, ip=controller_ip, port=controller_port)

    # Create switches with OpenFlow13 protocol
    switches = []
    for i in range(1, num_hosts + 1):
        switch = net.addSwitch(f's{i}', protocols='OpenFlow13')
        switches.append(switch)

    # Create hosts and connect them to switches
    for i in range(1, num_hosts + 1):
        host = net.addHost(f'h{i}')
        net.addLink(host, switches[i - 1])

    # Connect switches in a ring
    for i in range(len(switches)):
        net.addLink(switches[i], switches[(i + 1) % len(switches)])

    # Start the network
    net.build()
    c0.start()
    for switch in switches:
        switch.start([c0])

    # Start CLI
    CLI(net)

    # Stop the network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    if len(sys.argv) != 4:
        print("Usage: sudo python3 ring_topology.py <controller-ip> <controller-port> <num-hosts>")
        sys.exit(1)

    # Retrieve arguments
    controller_ip = sys.argv[1]
    controller_port = int(sys.argv[2])
    num_hosts = int(sys.argv[3])

    # Create the ring topology
    ring_topology(controller_ip, controller_port, num_hosts)
