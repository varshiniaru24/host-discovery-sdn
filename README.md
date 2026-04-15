# Host Discovery Service — SDN Mininet Project

**Course:** UE24CS252B — Computer Networks
**Name:** Varshini A
**SRN:** PES1UG24CS517
**Section:** I

---

## Problem Statement

**Problem #17 — Host Discovery Service**

In traditional networks, network administrators have no real-time visibility
into which hosts are connected to the network. This project implements an
SDN-based Host Discovery Service using Mininet and POX (OpenFlow controller)
that automatically detects hosts as they join the network, maintains a
real-time database of host information, and displays live updates.

This demonstrates core SDN concepts: controller-switch interaction,
packet_in event handling, and match-action flow rule logic.

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

**POX** was chosen over Ryu because it is fully compatible with Python 3.10
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
# Paste the host_discovery.py contents and save
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

---

## Test Scenarios

### Scenario 1 — Host Join Detection
Running `pingall` triggers all 4 hosts to send packets to the controller.
The controller logs each host with its full details on first contact.
**Result:** All 4 hosts logged with MAC, IP, Switch, Port and Time. 0% packet loss.

### Scenario 2 — Dynamic Update
Running `h3 ping -c 5 h4` after initial discovery shows the controller
handling subsequent traffic. After h3 pings h4, both hosts appear in the
controller log with their MAC, port and switch details.
**Result:** Host database updates correctly with each new packet_in event.

---

## Performance Observation

- **Latency:** Measured using ping — sub-millisecond RTT between all hosts
- **Throughput:** Measured using iperf between h1 and h2
- **Flow table:** Checked using `ovs-ofctl dump-flows s1` after pingall
- **Packet counts:** Visible in POX logs — total hosts tracked per event

---

## Validation & Regression Testing

- Re-ran `pingall` after initial discovery — no duplicate entries added to
  host DB (confirms MAC deduplication logic works correctly)
- Restarted controller and re-ran topology — all hosts rediscovered correctly
- Verified host count increments correctly: 1 → 2 → 3 → 4
- Confirmed 0% packet loss across all test runs

---

## Proof of Execution

### Host Discovery Logs (POX Terminal)
![Host Discovery](Screenshot%202026-04-15%20at%206.39.58%20PM.png)

### Pingall Result
![Pingall](Screenshot%202026-04-15%20at%206.40.37%20PM.png)

### Topology Running
![Topology](Screenshot%202026-04-15%20at%206.40.58%20PM.png)

### Scenario 1 — h1 ping h2
![Scenario1](Screenshot%202026-04-15%20at%206.41.15%20PM.png)

### Scenario 2 — h3 ping h4
![Scenario2](Screenshot%202026-04-15%20at%206.41.44%20PM.png)

### iperf Throughput
![iperf](Screenshot%202026-04-15%20at%206.42.41%20PM.png)

### Wireshark Capture
![Wireshark](Screenshot%202026-04-15%20at%206.43.03%20PM.png)

### Flow Table (ovs-ofctl dump-flows s1)
Empty flow table because POX is just flooding, not installing flow rules
![FlowTable](WhatsApp%Image%2026-04-15%at%23.52.39.jpeg)

---

## References

1. Mininet Overview — https://mininet.org/overview/
2. Mininet Walkthrough — https://mininet.org/walkthrough/
3. POX Controller — https://github.com/noxrepo/pox
4. OpenFlow — https://opennetworking.org/sdn-resources/openflow/
5. Mininet GitHub — https://github.com/mininet/mininet/wiki/Documentation
