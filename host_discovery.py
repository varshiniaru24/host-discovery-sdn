from pox.core import core
from pox.lib.revent import *
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import time

log = core.getLogger()

class HostDiscovery(EventMixin):
    def __init__(self):
        self.host_db = {}
        self.listenTo(core.openflow)
        log.info("=== Host Discovery Service Started ===")

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        src_mac = str(packet.src)
        dpid    = dpidToStr(event.dpid)
        in_port = event.port

        if src_mac not in self.host_db:
            src_ip = "Unknown"
            ip  = packet.find('ipv4')
            arp = packet.find('arp')
            if ip:
                src_ip = str(ip.srcip)
            elif arp:
                src_ip = str(arp.protosrc)

            self.host_db[src_mac] = {
                'ip':     src_ip,
                'switch': dpid,
                'port':   in_port,
                'time':   time.strftime('%H:%M:%S')
            }

            log.info("=== NEW HOST DISCOVERED ===")
            log.info("  MAC    : %s", src_mac)
            log.info("  IP     : %s", src_ip)
            log.info("  Switch : %s", dpid)
            log.info("  Port   : %s", in_port)
            log.info("  Time   : %s", self.host_db[src_mac]['time'])
            log.info("  Total hosts in DB: %d", len(self.host_db))
            log.info("===========================")

        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.data = event.ofp
        event.connection.send(msg)

def launch():
    core.registerNew(HostDiscovery)
