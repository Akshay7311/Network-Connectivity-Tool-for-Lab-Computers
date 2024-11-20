import os
import subprocess

ip_range = "192.168.1.0/24"

nmap_output = subprocess.check_output([r"C:\Program Files (x86)\Nmap/nmap.exe", "-sn", ip_range])

active_ips = []
inactive_ips = []

for line in nmap_output.decode("utf-8").splitlines():
    if "Nmap scan report for" in line:
        ip = line.split()[-1]
        active_ips.append(ip)

for i in range(1, 255):
    ip = f"192.168.1.{i}"
    if ip not in active_ips:
        inactive_ips.append(ip)

rdp_users = {}
uptime_info = {}

for ip in active_ips:
    try:
        rdp_output = subprocess.check_output([r"C:\Program Files (x86)\Nmap/nmap.exe", "-p", "3389", ip])
        if "open" in rdp_output.decode("utf-8"):
            rdp_users[ip] = "RDP is open"

        os_output = subprocess.check_output([r"C:\Program Files (x86)\Nmap/nmap.exe", "-O", "-v", ip])
        for line in os_output.decode("utf-8").splitlines():
            if "Uptime guess" in line:
                uptime_info[ip] = line.strip()
                print(uptime_info)
                break
    except subprocess.CalledProcessError:
        pass

with open("active_ips.txt", "w") as f:
    for ip in active_ips:
        f.write(ip + "\n")

with open("inactive_ips.txt", "w") as f:
    for ip in inactive_ips:
        f.write(ip + "\n")

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
<div class='container'>
    <button class='button' onclick='showActiveIPs()'>Active</button>
    <button class='button' onclick='showInactiveIPs()'>Inactive</button>
    <button class='button' onclick='showRDPUsers()'>RDP</button>
    <button class='button' onclick='showUptimeInfo()'>Uptime</button>
    <button class='button' onclick='runNmap()'>Run</button>
    
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
</div>
<footer>Network Connectivity Tool</footer>
<script>
    function showActiveIPs() {
        document.getElementById('active-ips').style.display = 'block';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'none';
    }
    
    function showInactiveIPs() {
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'block';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'none';
    }
    
    function showRDPUsers() {
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'block';
        document.getElementById('uptime-info').style.display = 'none';
    }

    function showUptimeInfo() {
        document.getElementById('active-ips').style.display = 'none';
        document.getElementById('inactive-ips').style.display = 'none';
        document.getElementById('rdp-users').style.display = 'none';
        document.getElementById('uptime-info').style.display = 'block';
    }

    function runNmap() {
        location.reload();
    }

    showActiveIPs();
</script>
</body>
</html>
    """)

print("HTML file with uptime guesses generated successfully.")
