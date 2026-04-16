# ============================================================
# Custom Mininet Topology for Host Discovery SDN Project
# ============================================================
# Topology:
# 1 Switch (s1)
# 4 Hosts (h1, h2, h3, h4)
# All hosts connected to single switch (star topology)
# ============================================================

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class CustomTopo(Topo):

    def build(self):
        """
        Build star topology:
        1 switch connected to 4 hosts
        """

        # Add switch
        s1 = self.addSwitch('s1')

        # Add hosts with IP addresses
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')

        # Connect hosts to switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)


def run():
    """
    Start Mininet network with remote POX controller
    """

    topo = CustomTopo()

    net = Mininet(
        topo=topo,
        controller=RemoteController('c0', ip='127.0.0.1', port=6633),
        switch=OVSSwitch
    )

    net.start()

    print("=== Network Started ===")
    print("Run commands like: pingall, iperf, etc.")

    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
