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
with open("app.html", "w") as f:
    f.write("""
<html>
<head>
 <style>
      body {
        background-color: #f4f4f4;
        height: calc(100%);
      }
      .container {
        display: flex;
        height: calc(100% - 70px);
        flex-direction: row;
      }
      .container div:first-child {
        display: flex;
        flex-direction: column;
        align-items: top;
      }
      .box {
        width: 80%;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
        margin: 10px;
        display: none;
      }
      .active {
        color: var(--primary-color);
        background-color: white;
      }
      .inactive {
        border: 2px solid red;
        background-color: white;
      }
      h2 {
        text-align: center;
      }
      ul {
        list-style-type: none;
        padding: 0;
      }
      header {
        text-align: center;
        padding: 10px;
        background-color: #333;
        color: white;
      }

      .button {
        width: 100%;
        background-color: var(--primary-color);
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        margin: 5px;
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
      }
    </style>
    <link rel="stylesheet" href="css/style.css" />
    <link rel="stylesheet" href="css/navbar.css" />
  
</head>
<body>
<nav class="navbar">
      <div class="nav-brand">NetManager</div>
      <ul class="nav-links">
        <li><a href="index.html" class="active">Home</a></li>
        <li><a href="app.html">App</a></li>
        <li><a href="logs.html">Logs</a></li>
        <li><a href="features.html">Features</a></li>
        <li><a href="about.html">About</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul>
    </nav>
  
<div class='container'>
    <aside class="sidebar">
        <div class="logo">NetManager</div>
        <nav>
          <ul>
            <li>
              <button class="button active" onclick="showLocalInfo()">
                Local Info
              </button>
            </li>
            <li>
              <button class="button" onclick="showActiveIPs()">Active</button>
            </li>
            <li>
              <button class="button" onclick="showInactiveIPs()">
                Inactive
              </button>
            </li>
            <li>
              <button class="button" onclick="showRDPUsers()">RDP</button>
            </li>
            <li>
              <button class="button" onclick="showUptimeInfo()">Uptime</button>
            </li>
            <li>
              <button class="button" onclick="showServicesAndPorts()">
                Services/Ports
              </button>
            </li>
          </ul>
        </nav>
        <div class="sidebar-footer">
          <a href="index.html">Back to Home</a>
        </div>
      </aside>
    
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
    showLocalInfo();
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
 <style>
      .app-container {
        display: flex;
        min-height: 100vh;
      }
      .sidebar {
        width: 250px;
        color: white;
        padding: 1rem;
        display: flex;
        flex-direction: column;
      }
      .logo {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1rem;
        color: #2563eb;
      }

      .sidebar nav {
        flex: 1;
      }

      .sidebar ul {
        list-style: none;
        padding: 0;
      }

      .sidebar a {
        color: white;
        text-decoration: none;
        padding: 0.75rem 1rem;
        display: block;
        margin: 0.25rem 0;
        border-radius: 4px;
      }

      .sidebar a:hover,
      .sidebar a.active {
        background: #2563eb;
      }

      .sidebar-footer {
        padding: 1rem;
        border-top: 1px solid #333;
      }

      .sidebar-footer a {
        color: #666;
      }

      .main-content {
        flex: 1;
        background: #f1f5f9;
      }

      header {
        background: white;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }

      #menuToggle {
        display: none;
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
      }

      .content {
        padding: 2rem;
      }

      @media (max-width: 768px) {
        .sidebar {
          position: fixed;
          left: -250px;
          top: 0;
          bottom: 0;
          transition: 0.3s;
          z-index: 1000;
        }

        .sidebar.active {
          left: 0;
        }

        #menuToggle {
          display: block;
        }
      }
    </style>

    
</body>
</html>
    """)

print("HTML file with complete information generated successfully.")
