# Host Discovery Service — SDN Mininet Project
**Course:** UE24CS252B — Computer Networks
Name - VARSHINI A , 
SRN - PES1UG24CS517 , 
SECTION - I
---

## Problem Statement
Implement an SDN-based Host Discovery Service using Mininet and POX controller that:
- Automatically detects hosts joining the network
- Maintains a real-time host database (MAC, IP, Switch, Port)
- Displays host details dynamically as they join
- Updates the database live

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
```

### 3. Start POX controller (Terminal 1)
```bash
cd ~/pox
python3 pox.py host_discovery
```

### 4. Start Mininet topology (Terminal 2)
```bash
sudo mn -c && sudo python3 ~/topology.py
```

### 5. Test
```bash
mininet> pingall
mininet> h1 ping -c 5 h2
mininet> iperf h1 h2
```

---

## Expected Output
- POX terminal shows each host discovered with MAC, IP, Switch, Port, Time
- pingall shows 0% packet loss
- All 4 hosts appear in the host database

---

## Test Scenarios

### Scenario 1 — Host Join Detection
Running `pingall` triggers all 4 hosts to be discovered simultaneously.
**Result:** All hosts logged with full details, 0% packet loss.

### Scenario 2 — Dynamic Update
Running `h3 ping -c 5 h4` after initial discovery shows the controller
dynamically updating as new traffic is observed.
**Result:** Host database updates in real time.

---

## Performance Observation
- **Latency:** Measured using ping — sub-millisecond between hosts
- **Throughput:** Measured using iperf
- **Flow table:** Updated dynamically on each new host discovery

---

## Proof of Execution

### Host Discovery Logs (POX Terminal)
![Host Discovery](Screenshot%202026-04-15%20at%206.39.58%20PM.png)

### Pingall Result
![Pingall](Screenshot%202026-04-15%20at%206.40.37%20PM.png)

### Topology Running
![Topology](Screenshot%202026-04-15%20at%206.40.58%20PM.png)

### Scenario 1 - h1 ping h2
![Scenario1](Screenshot%202026-04-15%20at%206.41.15%20PM.png)

### Scenario 2 - h3 ping h4
![Scenario2](Screenshot%202026-04-15%20at%206.41.44%20PM.png)

### iperf Throughput
![iperf](Screenshot%202026-04-15%20at%206.42.41%20PM.png)

### Wireshark Capture
![Wireshark](Screenshot%202026-04-15%20at%206.43.03%20PM.png)

### Flow Table
![FlowTable](Screenshot%202026-04-15%20at%206.43.11%20PM.png)

---

## References
1. Mininet - https://mininet.org/overview/
2. POX Controller - https://github.com/noxrepo/pox
3. OpenFlow - https://opennetworking.org/sdn-resources/openflow/
4. Mininet Walkthrough - https://mininet.org/walkthrough/
