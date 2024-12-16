from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_network():
    net = Mininet(controller=None, switch=OVSSwitch)

    print("Adding controllers")
    controller1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633)
    controller2 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=6634)

    print("Adding switches")
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')

    print("Adding hosts")
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')

    print("Creating links")
    net.addLink(h1, s1)
    net.addLink(s1, s2)
    net.addLink(s2, h2)

    print("Starting network")
    net.start()

    print("Configuring switches with controllers")
    s1.start([controller1, controller2])
    s2.start([controller1, controller2])

    print("Running CLI")
    CLI(net)

    print("Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
