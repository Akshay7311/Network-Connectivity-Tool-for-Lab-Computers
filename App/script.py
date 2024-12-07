import nmap
from scapy.all import ARP, Ether, srp, get_if_addr, conf
import json

def get_local_ip():
    local_ip = get_if_addr(conf.iface)
    return local_ip

local_ip = get_local_ip()
local_ip_with_port = local_ip + "/24"
print(f"Local IP address: {local_ip}, {local_ip_with_port}")


nm = nmap.PortScanner()
nm.scan(hosts=local_ip_with_port, arguments='-sn')

for host in nm.all_hosts():
    print(f"IP: {host}, MAC: {nm[host]['addresses'].get('mac', 'N/A')}")




def scan(ip_range):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=False)[0]
    devices = [{'ip': r.psrc, 'mac': r.hwsrc} for _, r in result]
    return devices

devices = scan(local_ip_with_port)
for device in devices:
    print(device)



scan_data = nm.scan(hosts=local_ip_with_port, arguments='-sn')
with open('scan_logs.json', 'w') as f:
    json.dump(scan_data, f)