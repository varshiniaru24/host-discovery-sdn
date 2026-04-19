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
        # 1. EXTRACT IP FROM PACKET (IPv4 or ARP)
        # --------------------------------------------------
        # IP extraction is done before host check so that
        # even on first packet, we capture the IP if available.
        # ARP packets arrive before IPv4, so IP may initially
        # be Unknown and gets updated on the next packet.
        ip  = packet.find('ipv4')
        arp = packet.find('arp')
        src_ip = "Unknown"

        if ip:
            # Extract source IP from IPv4 packet
            src_ip = str(ip.srcip)
        elif arp:
            # Extract source IP from ARP packet
            src_ip = str(arp.protosrc)

        # --------------------------------------------------
        # 2. HOST DISCOVERY (NEW HOST DETECTION)
        # --------------------------------------------------
        if src_mac not in self.host_db:
            # New host detected — store in database
            self.host_db[src_mac] = {
                'ip':     src_ip,
                'switch': dpid,
                'port':   in_port,
                'time':   time.strftime('%H:%M:%S')
            }

            # Log discovery details
            log.info("=== NEW HOST DISCOVERED ===")
            log.info("  MAC    : %s", src_mac)
            log.info("  IP     : %s", src_ip)
            log.info("  Switch : %s", dpid)
            log.info("  Port   : %s", in_port)
            log.info("  Time   : %s", self.host_db[src_mac]['time'])
            log.info("  Total hosts: %d", len(self.host_db))
            log.info("===========================")

        elif src_ip != "Unknown" and self.host_db[src_mac]['ip'] == "Unknown":
            # Host already known but IP was not captured yet.
            # Update IP once it becomes available (e.g. after ARP resolves).
            self.host_db[src_mac]['ip'] = src_ip
            log.info("  IP updated for %s -> %s", src_mac, src_ip)

        # --------------------------------------------------
        # 3. MAC LEARNING (LIKE LEARNING SWITCH)
        # --------------------------------------------------
        # Learn source MAC → port mapping
        # This allows future packets to be forwarded directly
        # without flooding the network
        self.mac_to_port[src_mac] = in_port

        # --------------------------------------------------
        # 4. FORWARDING DECISION (MATCH-ACTION)
        # --------------------------------------------------
        if dst_mac in self.mac_to_port:
            # Known destination → forward to specific port
            out_port = self.mac_to_port[dst_mac]
        else:
            # Unknown destination → flood to all ports
            out_port = of.OFPP_FLOOD

        # --------------------------------------------------
        # 5. INSTALL FLOW RULE (FLOW_MOD)
        # --------------------------------------------------
        if out_port != of.OFPP_FLOOD:
            # Create flow rule only for known destinations
            flow_mod = of.ofp_flow_mod()

            # Match on destination MAC address
            flow_mod.match.dl_dst = packet.dst

            # Action: output to the learned port
            flow_mod.actions.append(of.ofp_action_output(port=out_port))

            # idle_timeout: remove rule after 30s of inactivity
            flow_mod.idle_timeout = 30

            # hard_timeout: remove rule after 60s regardless of activity
            flow_mod.hard_timeout = 60

            # priority: higher value = higher precedence over default rules
            flow_mod.priority = 10

            # Send flow rule to switch
            event.connection.send(flow_mod)

        # --------------------------------------------------
        # 6. SEND CURRENT PACKET (PACKET_OUT)
        # --------------------------------------------------
        # Forward the current packet immediately while flow rule
        # is being installed, so no packet is dropped
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=out_port))

        event.connection.send(msg)


def launch():
    """
    Entry point for POX controller.
    Called by POX when module is loaded via:
    python3 pox.py host_discovery
    """
    core.registerNew(HostDiscovery)
