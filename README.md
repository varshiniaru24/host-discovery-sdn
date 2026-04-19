# Host Discovery Service — SDN Mininet Project

**Course:** UE24CS252B — Computer Networks  
**Name:** Varshini A  
**SRN:** PES1UG24CS517  
**Section:** I  

---

## Problem Statement

**Problem #7 — Host Discovery Service**

In traditional networks, network administrators have no real-time visibility  
into which hosts are connected to the network. This project implements an  
SDN-based Host Discovery Service using Mininet and POX (OpenFlow controller)  
that automatically detects hosts as they join the network, maintains a  
real-time database of host information, and displays live updates.  

This demonstrates core SDN concepts: controller-switch interaction,  
packet_in event handling, and match-action flow rule logic with dynamic flow installation.  

---

## Tools & Technologies

- Mininet (network emulator)  
- POX (OpenFlow SDN controller)  
- Open vSwitch  
- Wireshark (traffic capture)  
- iperf (performance testing)  
- Python 3.10  
- Ubuntu 22.04 (UTM VM on macOS)  

---

## Topology

- 1 Switch (s1)  
- 4 Hosts (h1, h2, h3, h4)  
- All hosts connected to s1  
- POX controller running on 127.0.0.1 port 6633  

---

## Design Justification

A **single switch star topology** was chosen because:  

- It simplifies host discovery by funneling all traffic through one switch  
- All packet_in events arrive at one controller connection point  
- Easy to scale (add more hosts) without changing controller logic  
- Ideal for demonstrating host join detection in a controlled environment  

**POX** was chosen because it is lightweight, Python-based,  
and provides a simple event-driven API for handling OpenFlow packet_in events.  

---

## Setup & Execution Steps

### 1. Install dependencies
```bash
sudo apt update
sudo apt install mininet -y
git clone https://github.com/noxrepo/pox
```

### 2. Add controller file
```bash
nano ~/pox/ext/host_discovery.py
# Paste the updated host_discovery.py contents and save
```

### 3. Add topology file
```bash
nano ~/topology.py
# Paste the topology.py contents and save
```

### 4. Start POX controller (Terminal 1)
```bash
cd ~/pox
python3 pox.py host_discovery
```

### 5. Start Mininet topology (Terminal 2)
```bash
sudo mn -c && sudo python3 ~/topology.py
```

### 6. Run tests inside Mininet CLI
```bash
mininet> pingall
mininet> h1 ping -c 5 h2
mininet> h3 ping -c 5 h4
mininet> iperf h1 h2
mininet> sh ovs-ofctl dump-flows s1
```

---

## Expected Output

- POX terminal prints each host discovered with MAC, IP, Switch, Port and Time  
- pingall shows 0% packet loss across all 4 hosts  
- All 4 hosts appear in the host database with incrementing count (1 → 2 → 3 → 4)  
- IPs are dynamically updated once ARP exchange completes  
- Flow table shows dynamically installed entries with priority=10, idle_timeout=30, hard_timeout=60  

---

## Test Scenarios

### Scenario 1 — Host Join Detection

Running `pingall` triggers all 4 hosts to send packets to the controller.  
The controller logs each host with its full details on first contact.  
IPs are updated dynamically once ARP packets are processed.

**Result:** All 4 hosts logged with MAC, IP, Switch, Port and Time. 0% packet loss.

---

### Scenario 2 — Dynamic Update & Flow Installation

Running `h3 ping -c 5 h4` after initial discovery shows the controller  
handling subsequent traffic.

**Result:**
- Host database updates correctly
- Flow rules installed in switch with priority=10, idle_timeout=30s, hard_timeout=60s
- First packet handled by controller (45.6ms), subsequent packets forwarded
  directly by switch (~0.04ms), confirming flow rule installation works correctly

---

## Performance Observation & Analysis

### Latency (ping)
- h1 → h2: min/avg/max/mdev = 0.037/9.426/46.845/18.709 ms
- h3 → h4: min/avg/max/mdev = 0.042/9.155/45.599/18.221 ms
- The first ping is always significantly slower (46.8ms, 45.6ms) because the
  packet goes to the controller via packet_in — the controller processes it
  and installs a flow rule before forwarding. All subsequent packets are
  forwarded directly by the switch using the installed flow rule, dropping
  latency to under 0.05ms. This controller-bypass behavior is the core
  benefit of SDN flow rules.

### Throughput (iperf)
- h1 ↔ h2: 107 Gbits/sec (both directions)
- Very high throughput is expected in a virtual environment — after the first
  packet, the switch forwards all traffic locally without involving the
  controller, so there is no per-packet overhead.

### Flow Table (ovs-ofctl dump-flows s1)
- Flow rules installed with priority=10, idle_timeout=30, hard_timeout=60
- Each rule matches on dl_dst (destination MAC) and outputs to a specific
  port, confirming match-action logic is working correctly
- Rules with idle_timeout=30s expire automatically after inactivity,
  demonstrating dynamic flow lifecycle management — this is why fewer rules
  appear in the flow table when queried after traffic has settled

### Packet Counts
- n_packets and n_bytes visible per rule in flow table output
- Confirms traffic is being forwarded through installed flow rules

---

## Validation & Regression Testing

- Re-ran `pingall` — no duplicate entries in host database
- Restarted controller — hosts rediscovered correctly
- Verified host count increments correctly: 1 → 2 → 3 → 4
- Confirmed flow rules installed dynamically with priority=10, idle_timeout=30, hard_timeout=60
- Confirmed 0% packet loss across all test runs (12/12 received)
- Confirmed IP update mechanism works — IPs populated after ARP exchange completes

---

## Proof of Execution

### Host Discovery Logs (POX Terminal)
![Host Discovery](Screenshot%202026-04-19%20at%2010.25.06%20PM.png)

### Pingall Result
![Pingall](Screenshot%202026-04-19%20at%2010.29.15%20PM.png)

### Scenario 1 — h1 ping h2
![Scenario1](Screenshot%202026-04-19%20at%2010.29.55%20PM.png)

### Scenario 2 — h3 ping h4
![Scenario2](Screenshot%202026-04-19%20at%2010.30.27%20PM.png)

### iperf Throughput
![iperf](Screenshot%202026-04-19%20at%2010.30.57%20PM.png)

### Flow Table (ovs-ofctl dump-flows s1)
Flow rules show priority=10, idle_timeout=30, hard_timeout=60 confirming
correct flow rule installation with match-action logic.  
![FlowTable](Screenshot%202026-04-19%20at%2010.31.36%20PM.png)

### Wireshark Capture
ICMP and ARP traffic captured on h1-eth0 confirming correct packet flow
through the SDN network.  
![Wireshark](Screenshot%202026-04-15%20at%206.43.11%20PM.png)

---

## References

1. Mininet Overview — https://mininet.org/overview/
2. Mininet Walkthrough — https://mininet.org/walkthrough/
3. POX Controller — https://github.com/noxrepo/pox
4. OpenFlow — https://opennetworking.org/sdn-resources/openflow/
5. Mininet GitHub — https://github.com/mininet/mininet/wiki/Documentation
