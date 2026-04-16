# ============================================================
# Host Discovery Service with Flow Rule Installation (SDN)
# ============================================================
# This POX controller:
# 1. Detects hosts dynamically (MAC, IP, switch, port)
# 2. Maintains a host database
# 3. Implements learning switch logic
# 4. Installs flow rules (match-action) in switch
# ============================================================

from pox.core import core
from pox.lib.revent import *
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import time

log = core.getLogger()

class HostDiscovery(EventMixin):

    def __init__(self):
        # Dictionary to store discovered hosts:
        # MAC -> {ip, switch, port, time}
        self.host_db = {}

        # MAC learning table: MAC -> port
        self.mac_to_port = {}

        # Register for OpenFlow events
        self.listenTo(core.openflow)

        log.info("=== Host Discovery + Learning Switch Started ===")

    def _handle_PacketIn(self, event):
        """
        Handles packets sent from switch to controller.
        Implements:
        - Host discovery
        - MAC learning
        - Flow rule installation
        """

        packet = event.parsed
        if not packet.parsed:
            return

        # Extract packet details
        src_mac = str(packet.src)
        dst_mac = str(packet.dst)
        dpid    = dpidToStr(event.dpid)
        in_port = event.port

        # --------------------------------------------------
        # 1. HOST DISCOVERY (NEW HOST DETECTION)
        # --------------------------------------------------
        if src_mac not in self.host_db:
            src_ip = "Unknown"

            # Extract IP from IPv4 or ARP packet
            ip  = packet.find('ipv4')
            arp = packet.find('arp')

            if ip:
                src_ip = str(ip.srcip)
            elif arp:
                src_ip = str(arp.protosrc)

            # Store host details
            self.host_db[src_mac] = {
                'ip':     src_ip,
                'switch': dpid,
                'port':   in_port,
                'time':   time.strftime('%H:%M:%S')
            }

            # Log discovery
            log.info("=== NEW HOST DISCOVERED ===")
            log.info("  MAC    : %s", src_mac)
            log.info("  IP     : %s", src_ip)
            log.info("  Switch : %s", dpid)
            log.info("  Port   : %s", in_port)
            log.info("  Time   : %s", self.host_db[src_mac]['time'])
            log.info("  Total hosts: %d", len(self.host_db))
            log.info("===========================")

        # --------------------------------------------------
        # 2. MAC LEARNING (LIKE LEARNING SWITCH)
        # --------------------------------------------------
        # Learn source MAC → port mapping
        self.mac_to_port[src_mac] = in_port

        # --------------------------------------------------
        # 3. FORWARDING DECISION (MATCH-ACTION)
        # --------------------------------------------------
        if dst_mac in self.mac_to_port:
            # Known destination → forward to specific port
            out_port = self.mac_to_port[dst_mac]
        else:
            # Unknown destination → flood
            out_port = of.OFPP_FLOOD

        # --------------------------------------------------
        # 4. INSTALL FLOW RULE (FLOW_MOD)
        # --------------------------------------------------
        if out_port != of.OFPP_FLOOD:
            # Create flow rule
            flow_mod = of.ofp_flow_mod()
            flow_mod.match.dl_dst = packet.dst   # Match destination MAC
            flow_mod.actions.append(of.ofp_action_output(port=out_port))

            # Optional: idle timeout (removes rule after inactivity)
            flow_mod.idle_timeout = 30

            # Send rule to switch
            event.connection.send(flow_mod)

        # --------------------------------------------------
        # 5. SEND CURRENT PACKET (PACKET_OUT)
        # --------------------------------------------------
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=out_port))

        event.connection.send(msg)


def launch():
    """
    Entry point for POX controller
    """
    core.registerNew(HostDiscovery)
