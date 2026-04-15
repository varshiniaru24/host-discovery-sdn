from pox.core import core
from pox.lib.revent import *
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import time

log = core.getLogger()

class HostDiscovery(EventMixin):
    def __init__(self):
        # Dictionary to store discovered hosts: MAC -> {ip, switch, port, time}
        self.host_db = {}
        # Register to listen for OpenFlow events
        self.listenTo(core.openflow)
        log.info("=== Host Discovery Service Started ===")

    def _handle_PacketIn(self, event):
        # Called every time a packet arrives at the controller
        packet = event.parsed
        if not packet.parsed:
            return

        src_mac = str(packet.src)   # Source MAC address of the host
        dpid    = dpidToStr(event.dpid)  # Switch ID
        in_port = event.port        # Port the packet came in on

        # Only process if this is a new host (not seen before)
        if src_mac not in self.host_db:
            src_ip = "Unknown"

            # Try to extract IP from IPv4 or ARP packet
            ip  = packet.find('ipv4')
            arp = packet.find('arp')
            if ip:
                src_ip = str(ip.srcip)
            elif arp:
                src_ip = str(arp.protosrc)

            # Store host info in database
            self.host_db[src_mac] = {
                'ip':     src_ip,
                'switch': dpid,
                'port':   in_port,
                'time':   time.strftime('%H:%M:%S')
            }

            # Log the discovered host details
            log.info("=== NEW HOST DISCOVERED ===")
            log.info("  MAC    : %s", src_mac)
            log.info("  IP     : %s", src_ip)
            log.info("  Switch : %s", dpid)
            log.info("  Port   : %s", in_port)
            log.info("  Time   : %s", self.host_db[src_mac]['time'])
            log.info("  Total hosts in DB: %d", len(self.host_db))
            log.info("===========================")

        # Flood packet out all ports so network communication still works
        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.data = event.ofp
        event.connection.send(msg)

def launch():
    # Entry point — registers HostDiscovery with POX core
    core.registerNew(HostDiscovery)
