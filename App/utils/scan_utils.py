import nmap
import psutil
import platform
import logging
import time
from datetime import timedelta,datetime
import subprocess
import re
from config import databases
import uuid
import os


# Configure logging
logging.basicConfig(
    filename="network_scan.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

database_id = os.getenv('DATABASE_ID')
scan_result_collection_id = os.getenv('SCAN_RESULT_COLLECTION_ID')
log_result_collection_id = os.getenv('LOG_RESULT_COLLECTION_ID')


# Helper function: Network scanning
def scan_network(target="192.168.1.0/24"):
    scanner = nmap.PortScanner()
    scanner.scan(hosts=target, arguments='-sn')
    results = []
    for host in scanner.all_hosts():
        results.append({
            "ip": host,
            "mac": scanner[host]['addresses'].get('mac', 'N/A')
        })
    return results

# Helper function: Scan open ports
def scan_ports_with_subprocess(target="192.168.1.0/24", ports="3389"):
    try:
        nmap_output = subprocess.check_output(["nmap", "-v", target], universal_newlines=True)
        results = []
        current_ip = None
        open_ports = []

        for line in nmap_output.splitlines():
            # Match IP addresses in Nmap output
            ip_match = re.match(r"Nmap scan report for (.*)", line)
            port_match = re.match(r"(\d+/tcp)\s+(open)\s+.*", line)
            host_down_match = re.match(r".*\[host down\]", line)

            # Handle IP match
            if ip_match:
                if current_ip:
                    # Only add if host is not down
                    if "host down" not in current_ip.lower():
                        results.append({"ip": current_ip, "open_ports": open_ports})

                current_ip = ip_match.group(1)
                open_ports = []

            # Handle port match
            elif port_match:
                open_ports.append(port_match.group(1))

            # Handle host down match
            elif host_down_match:
                current_ip = f"{current_ip} [host down]"

        # Append last IP entry
        if current_ip and "host down" not in current_ip.lower():
            results.append({"ip": current_ip, "open_ports": open_ports})

        # Create document ID
        
        # Store scan results in Appwrite database
        for result in results:
            document_id = str(uuid.uuid4())
            # Ensure the result structure matches the expected schema
            document_data = {
                "ip": result["ip"],
                "open_ports": result["open_ports"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            databases.create_document(
                database_id=database_id,
                document_id=document_id,
                collection_id=scan_result_collection_id,  # Your Appwrite collection ID
                data=document_data,
            )

        for result in results:
            logging.info(f"Scanning {result['ip']}, Open Ports: {result['open_ports']}")

        return results
    except Exception as e:
        logging.error(f"Error scanning with subprocess: {str(e)}")
        return []

def get_uptime():
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
        return f"Error: {str(e)}"

def get_os_info():
    return {
        "system": platform.system(),
        "version": platform.version(),
        "release": platform.release()
    }

def log_scan_results(results):
    for result in results:
        try:
            # Prepare the log entry
            log_entry = f"Device found: IP={result['ip']}, MAC={result['mac']}"
            logging.info(log_entry)
            
            # Define document ID (this can be auto-generated or a specific value)
            document_id = str(uuid.uuid4())
            
            # Create the document in Appwrite
            databases.create_document(
                document_id=document_id,
                database_id=database_id,   # Example database_id (change as needed)
                collection_id=log_result_collection_id,          # Your Appwrite collection ID
                data={
                    'log': log_entry,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
             
            )
            logging.info(f"Document created for IP: {result['ip']}")

        except Exception as e:
            # Catch any errors that occur during the document creation
            logging.error(f"Error creating document for IP: {result['ip']}, Error: {str(e)}")
