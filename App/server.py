from flask import Flask, request, jsonify
from flask_cors import CORS
import nmap
import psutil
import platform
import logging
import time
from datetime import datetime, timedelta
import subprocess
import re


# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    filename="network_scan.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Helper function: Network scanning
def scan_network(target="192.168.1.0/24"):
    scanner = nmap.PortScanner()
    scanner.scan(hosts=target, arguments='-sn')  # Ping scan for active hosts
    results = []
    for host in scanner.all_hosts():
        results.append({
            "ip": host,
            "mac": scanner[host]['addresses'].get('mac', 'N/A')
        })
    return results

# Helper function: Scan open ports (all ports)
def scan_ports(target="192.168.1.0/24", ports="3389"):
    scanner = nmap.PortScanner()
    scanner.scan(hosts=target, arguments=f"-p {ports}")  # Scan all ports
    results = []
    for host in scanner.all_hosts():
        if scanner[host].state() == "up":
            open_ports = [
                port for port in scanner[host]['tcp']
                if scanner[host]['tcp'][port]['state'] == 'open'
            ]
            results.append({
                "ip": host,
                "open_ports": open_ports
            })
            # Log the progress as scanning is happening
            log_message = f"Scanning {host}, Open Ports: {open_ports}"
            logging.info(log_message)
    return results

# Function to scan ports using subprocess and parse nmap output
def scan_ports_with_subprocess(target="192.168.1.0/24", ports="3389"):
    try:
        # Run the nmap scan with subprocess
        nmap_output = subprocess.check_output(["nmap", "-v", target], universal_newlines=True)
        
        # Parse the output using regex to extract open ports
        results = []
        current_ip = None
        open_ports = []

        # Regex pattern to extract IPs and open ports
        for line in nmap_output.splitlines():
            ip_match = re.match(r"Nmap scan report for (.*)", line)
            port_match = re.match(r"(\d+/tcp)\s+(open)\s+.*", line)
            host_down_match = re.match(r".*\[host down\]", line)  # Match the 'host down' message

            if ip_match:
                # New IP found, check if it was marked as down
                if current_ip:
                    # If the previous IP was not "down", add it to results
                    if "host down" not in current_ip.lower():
                        results.append({"ip": current_ip, "open_ports": open_ports})

                # Start new IP block
                current_ip = ip_match.group(1)
                open_ports = []  # Reset open ports for new IP

            elif port_match:
                # If an open port is found, add it to the list of open ports
                open_ports.append(port_match.group(1))

            elif host_down_match:
                # If host is down, mark it and skip appending
                current_ip = f"{current_ip} [host down]"

        # Append the last IP if it was not marked down
        if current_ip and "host down" not in current_ip.lower():
            results.append({"ip": current_ip, "open_ports": open_ports})

        # Log the progress as scanning happens
        for result in results:
            logging.info(f"Scanning {result['ip']}, Open Ports: {result['open_ports']}")

        return results

    except Exception as e:
        logging.error(f"Error scanning with subprocess: {str(e)}")
        return []

# Helper function: Get system uptime
def get_uptime():
    try:
        boot_time = psutil.boot_time()
        current_time = time.time()
        
        uptime_seconds = current_time - boot_time
        uptime = timedelta(seconds=uptime_seconds)

        # Format the uptime into days, hours, minutes, and seconds
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        return uptime_str
    except Exception as e:
        return f"Error: {str(e)}"
    
    

# Helper function: Get OS info
def get_os_info():
    return {
        "system": platform.system(),
        "version": platform.version(),
        "release": platform.release()
    }

# Helper function: Log scan results
def log_scan_results(results):
    for result in results:
        logging.info(f"Device found: IP={result['ip']}, MAC={result['mac']}")

# API endpoint: Scan network
@app.route('/scan', methods=['POST'])
def scan():
    try:
        # Parse target network from request
        data = request.json
        target = data.get('target', '192.168.1.0/24')

        # Record session start time
        session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Perform scan
        devices = scan_network(target)
        log_scan_results(devices)  # Log the results

        # Get system info (uptime, OS info)
        os_info = get_os_info()
        uptime = get_uptime()

        # Return detailed results including session info
        return jsonify({
            "message": "Scan completed",
            "session_start": session_start_time,
            "devices": devices,
            "uptime": uptime,
            "os_info": os_info
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint: Scan ports
@app.route('/scan_ports', methods=['POST'])
def scan_rdp_ports():
    try:
        # Parse target network from request
        data = request.json
        target = data.get('target', '192.168.1.0/24')

        # Perform port scan for all open ports
        ports_results = scan_ports_with_subprocess(target)
        # ports_results = scan_ports(target)

        # Return results of port scan
        return jsonify({
            "message": "Port scan completed",
            "results": ports_results
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint: System info
@app.route('/system_info', methods=['GET'])
def system_info():
    try:
        os_info = get_os_info()
        uptime = get_uptime()
        return jsonify({"os_info": os_info, "uptime": uptime}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint: Fetch logs
@app.route('/logs', methods=['GET'])
def fetch_logs():
    try:
        with open("network_scan.log", "r") as log_file:
            logs = log_file.readlines()
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
