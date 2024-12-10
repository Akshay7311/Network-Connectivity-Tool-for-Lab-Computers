import os
import platform
import subprocess
import psutil
import time
import logging
from datetime import timedelta, datetime

# Set up logging
logging.basicConfig(
    filename="scan_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

ip_range = "192.168.1.1/24"

logging.info("Starting network scan for range: %s", ip_range)

nmap_output = subprocess.check_output([r"C:\Program Files (x86)\Nmap/nmap.exe", "-sn", ip_range])

logging.info("Nmap scan completed for IP range.")

# Function to get the local machine's uptime using psutil
def get_local_uptime():
    try:
        boot_time = psutil.boot_time()
        current_time = time.time()
        uptime_seconds = current_time - boot_time
        uptime = timedelta(seconds=uptime_seconds)

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        return uptime_str
    except Exception as e:
        logging.error("Error fetching local uptime: %s", str(e))
        return f"Error: {str(e)}"

# Function to get local OS information
def get_os_info():
    try:
        system = platform.system()
        release = platform.release()
        version = platform.version()
        os_info = f"System: {system}<br>Release: {release}<br>Version: {version}"
        return os_info
    except Exception as e:
        logging.error("Error fetching OS information: %s", str(e))
        return f"Error: {str(e)}"

active_ips = []
inactive_ips = []
rdp_users = {}
uptime_info = {}
services_and_ports = {}
local_uptime = get_local_uptime()
os_info = get_os_info()

# Parse the Nmap output to identify active IPs
for line in nmap_output.decode("utf-8").splitlines():
    if "Nmap scan report for" in line:
        ip = line.split()[-1]
        active_ips.append(ip)
        logging.info("Active IP detected: %s", ip)

# Identify inactive IPs
for i in range(1, 255):
    ip = f"192.168.1.{i}"
    if ip not in active_ips:
        inactive_ips.append(ip)

# Gather RDP, uptime, and service/port information for active IPs
for ip in active_ips:
    try:
        logging.info("Scanning IP: %s", ip)
        rdp_output = subprocess.check_output([r"C:\Program Files (x86)\Nmap/nmap.exe", "-p", "3389", ip])
        if "open" in rdp_output.decode("utf-8"):
            rdp_users[ip] = "RDP is open"
        else:
            rdp_users[ip] = "RDP is not open"

        os_output = subprocess.check_output([r"C:\Program Files (x86)\Nmap/nmap.exe", "-O", "-v", ip])
        ports_output = subprocess.check_output([r"C:\Program Files (x86)\Nmap/nmap.exe", "-sV", ip])

        # Extract uptime information
        for line in os_output.decode("utf-8").splitlines():
            if "Uptime guess" in line:
                uptime_info[ip] = line.strip()
                logging.info("Uptime information found for %s: %s", ip, line.strip())
                break

        # Extract services and ports information
        services_and_ports[ip] = []
        for line in ports_output.decode("utf-8").splitlines():
            if "/tcp" in line and "open" in line:
                services_and_ports[ip].append(line.strip())
                logging.info("Service/Port info for %s: %s", ip, line.strip())

    except subprocess.CalledProcessError as e:
        logging.error("Error scanning IP %s: %s", ip, str(e))
        pass

# Generate the HTML report
with open("index.html", "w") as f:
    f.write("""
<html>
<head>
<style>
    body { font-family: Arial, sans-serif; background-color: #f4f4f4; }
    .container { display: flex; flex-direction: column; align-items: center; }
    .box { width: 80%; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); margin: 10px; display: none; }
    .active { border: 2px solid green; background-color: white; }
    .inactive { border: 2px solid red; background-color: white; }
    h2 { text-align: center; }
    ul { list-style-type: none; padding: 0; }
    header { text-align: center; padding: 10px; background-color: #333; color: white; }
    footer { text-align: center; padding: 10px; background-color: #333; color: white; }
    .button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
    .button:hover { background-color: #3e8e41; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
</style>
</head>
<body>
<header><h1 style='text-align:center;'>Network Connectivity Tool</h1></header>
   <ul
      style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
      "
    >
      <li>
        <a
          style="
            text-decoration: none;
            color: #fff;
            background-color: #333;
            padding: 0.5rem 1rem;
            border-radius: 12px;
          "
          href="index.html"
          >Home</a
        >
      </li>
      <li>
        <a
          style="
            text-decoration: none;
            color: #fff;
            background-color: #333;
            padding: 0.5rem 1rem;
            border-radius: 12px;
          "
          href="logs.html"
          >Logs</a
        >
      </li>
    </ul>
<div class='container'>
    <button class='button' onclick='showLocalInfo()'>Local Info</button>
    <button class='button' onclick='showActiveIPs()'>Active</button>
    <button class='button' onclick='showInactiveIPs()'>Inactive</button>
    <button class='button' onclick='showRDPUsers()'>RDP</button>
    <button class='button' onclick='showUptimeInfo()'>Uptime</button>
    <button class='button' onclick='showServicesAndPorts()'>Services/Ports</button>
    
    <div id='local-info' class='box'><h2>Local System Information</h2>
        <div><strong>OS Information:</strong><br>""" + os_info + """</div>
        <div><strong>Uptime:</strong><br>""" + local_uptime + """</div>
    </div>

    <div id='active-ips' class='box active'><h2>Active IP Addresses</h2><div class='grid'>
    """)
    
    for ip in active_ips:
        f.write(f"<div>{ip}</div>")

    f.write("""
    </div></div>
    
    <div id='inactive-ips' class='box inactive'><h2>Inactive IP Addresses</h2><div class='grid'>
    """)

    for ip in inactive_ips:
        f.write(f"<div>{ip}</div>")

    f.write("""
    </div></div>
    
    <div id='rdp-users' class='box'><h2>RDP Users</h2><div class='grid'>
    """)

    for ip, status in rdp_users.items():
        f.write(f"<div>{ip}: {status}</div>")

    f.write("""
    </div></div>

    <div id='uptime-info' class='box'><h2>Uptime Information</h2><div class='grid'>
    """)

    for ip, uptime in uptime_info.items():
        f.write(f"<div>{ip}: {uptime}</div>")

    f.write("""
    </div></div>

    <div id='services-and-ports' class='box'><h2>Open Ports and Services</h2><div class='grid'>
    """)

    for ip, services in services_and_ports.items():
        f.write(f"<div><strong>{ip}:</strong><br>" + "<br>".join(services) + "</div>")

    f.write("""
    </div></div>
</div>
<footer>Network Connectivity Tool</footer>
<script>
    function showLocalInfo() {
        document.getElementById('local-info').style.display = 'block';
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'none';
        document.getElementById('services-and-ports').style.display = 'none';
    }
    function showActiveIPs() {
        document.getElementById('local-info').style.display = 'none';
        document.getElementById('active-ips').style.display = 'block';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'none';
        document.getElementById('services-and-ports').style.display = 'none';
    }
    function showInactiveIPs() {
        document.getElementById('local-info').style.display = 'none';
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'block';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'none';
        document.getElementById('services-and-ports').style.display = 'none';
    }
    function showRDPUsers() {
        document.getElementById('local-info').style.display = 'none';
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'block';
        document.getElementById('uptime-info').style.display = 'none';
        document.getElementById('services-and-ports').style.display = 'none';
    }
    function showUptimeInfo() {
        document.getElementById('local-info').style.display = 'none';
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'block';
        document.getElementById('services-and-ports').style.display = 'none';
    }
    function showServicesAndPorts() {
        document.getElementById('local-info').style.display = 'none';
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'none';
        document.getElementById('services-and-ports').style.display = 'block';
    }
</script>
</body>
</html>
    """)

print("HTML file with complete information generated successfully.")
