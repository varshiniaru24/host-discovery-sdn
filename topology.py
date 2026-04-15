from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class CustomTopo(Topo):
    def build(self):
        # Add switch
        s1 = self.addSwitch('s1')

        # Add 4 hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')

        # Connect all hosts to switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)

def run():
    topo = CustomTopo()
    net = Mininet(topo=topo,
                  controller=RemoteController('c0', ip='127.0.0.1', port=6633),
                  switch=OVSSwitch)
    net.start()
    print("Network started!")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
