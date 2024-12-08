import nmap
import psutil
import platform
import logging
import time
from datetime import timedelta,datetime
import subprocess
import re
from config import databases,account
import uuid
import os
from appwrite.query import Query



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
def scan_ports_with_subprocess(target="192.168.1.0/24", ports="3389", user_id=None):
    try:
        # Validate user ID
        # if not user_id:
        #     error_message = "User ID not provided. Authentication required to save scan results."
        #     logging.error(error_message)
        #     return {"error": error_message}

        # Run the Nmap scan
        nmap_output = subprocess.check_output(["nmap", "-v", target], universal_newlines=True)
        results = []
        current_ip = None
        open_ports = []

        # Parse Nmap output for open ports
        for line in nmap_output.splitlines():
            ip_match = re.match(r"Nmap scan report for (.*)", line)
            port_match = re.match(r"(\d+/tcp)\s+(open)\s+.*", line)
            host_down_match = re.match(r".*\[host down\]", line)

            if ip_match:
                if current_ip:
                    if "host down" not in current_ip.lower():
                        results.append({"ip": current_ip, "open_ports": open_ports})
                current_ip = ip_match.group(1)
                open_ports = []

            elif port_match:
                open_ports.append(port_match.group(1))

            elif host_down_match:
                current_ip = f"{current_ip} [host down]"

        if current_ip and "host down" not in current_ip.lower():
            results.append({"ip": current_ip, "open_ports": open_ports})

        # Now fetch system info for each IP address using get_system_info
        for result in results:
            ip = result['ip']
            system_info = get_system_info(ip)
            result['system_info'] = system_info
            

        # Save or update results in Appwrite
        for result in results:
            existing_document = None
            try:
                # Query for existing document
                documents = databases.list_documents(
                    database_id=database_id,
                    collection_id=scan_result_collection_id,
                    queries=[Query.equal("ip", result["ip"])],
                    # queries=[Query.equal("ip", result["ip"]), Query.equal("user_id", user_id)],
                )
                if documents["total"] > 0:
                    existing_document = documents["documents"][0]
            except Exception as e:
                logging.error(f"Error checking existing document for IP {result['ip']}: {str(e)}")

            # Document data for saving
            document_data = {
                "ip": result["ip"],
                "open_ports": result["open_ports"],
                "system_info": result["system_info"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": user_id,
            }

            try:
                if existing_document:
                    document_id = existing_document["$id"]
                    databases.update_document(
                        database_id=database_id,
                        collection_id=scan_result_collection_id,
                        document_id=document_id,
                        data=document_data,
                    )
                    logging.info(f"Updated scan result for IP {result['ip']}")
                else:
                    document_id = str(uuid.uuid4())
                    databases.create_document(
                        database_id=database_id,
                        document_id=document_id,
                        collection_id=scan_result_collection_id,
                        data=document_data,
                    )
                    logging.info(f"Created new scan result for IP {result['ip']}")
            except Exception as e:
                logging.error(f"Error saving scan result for IP {result['ip']}: {str(e)}")

        # Log the results
        for result in results:
            logging.info(f"Scanning {result['ip']}, Open Ports: {result['open_ports']}, System Info: {result['system_info']}")

        return results

    except subprocess.CalledProcessError as e:
        logging.error(f"Nmap command failed: {e.output}")
        return {"error": f"Nmap scan failed: {str(e)}"}

    except Exception as e:
        logging.error(f"Error scanning with subprocess: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}
     
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

def log_scan_results(results, user_id=None):
    """
    Logs scan results and saves them to Appwrite.

    Args:
        results (list): List of scan results with IP and MAC addresses.
        user_id (str): ID of the user performing the scan.
    """
    try:
        # Validate user ID
        # if not user_id:
        #     error_message = "User ID not provided. Authentication required to save logs."
        #     logging.error(error_message)
        #     return {"error": error_message}

        for result in results:
            try:
                # Prepare the log entry
                log_entry = f"Device found: IP={result.get('ip')}, MAC={result.get('mac') or None}, "
                logging.info(log_entry)

                # Define document ID (auto-generated UUID)
                document_id = str(uuid.uuid4())

                # Create the document in Appwrite
                databases.create_document(
                    document_id=document_id,
                    database_id=database_id,
                    collection_id=log_result_collection_id,
                    data={
                        "log": log_entry,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user_id": user_id,
                    },
                )
                logging.info(f"Document created for IP: {result.get('ip')}")

            except Exception as e:
                # Catch any errors that occur during document creation
                logging.error(
                    f"Error creating document for IP: {result.get('ip')}, Error: {str(e)}"
                )

        return {"message": "Logs saved successfully."}

    except Exception as e:
        logging.error(f"Error logging scan results: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

# Get System Info for Specific IP address
def get_system_info(target_ip):
    try:
        # Run Nmap with OS detection and service/version detection
        nmap_output = subprocess.check_output(
            ["nmap", "-O", "-sV", target_ip],
            universal_newlines=True
        )

        # Initialize system info dictionary
        system_info = {
            "hostname": None,
            "os": None,
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "open",
            "open_ports": []
        }

        # Parse hostname
        hostname_match = re.search(r"Nmap scan report for (.+)", nmap_output)
        if hostname_match:
            system_info["hostname"] = hostname_match.group(1)

        # Parse OS information
        os_match = re.search(r"Running: (.+)", nmap_output)
        if os_match:
            system_info["os"] = os_match.group(1)

        # Parse open ports
        port_matches = re.findall(r"(\d+)/tcp\s+open\s+(\S+)\s+(.+)", nmap_output)
        for port, service, version in port_matches:
            system_info["open_ports"].append({
                "port": port,
                "service": service,
                "version": version,
                "state": "open"
            })

        logging.info(f"System info for {target_ip}: {system_info}")
        return system_info

    except Exception as e:
        logging.error(f"Error retrieving system info for {target_ip}: {str(e)}")
        return {"error": str(e)}


# TO Scan Vulnerabilities in IP
def scan_vulnerabilities(target="192.168.1.0/24"):
    try:
        command = ["nmap", "-sV", "--script", "vuln", target]
        # Run Nmap with `vulners` and other scripts
        nmap_output = subprocess.run(command, capture_output=True, text=True)

        # Access stdout
        output_lines = nmap_output.stdout.splitlines()

        results = []
        current_ip = None
        vulnerabilities = []

        for line in output_lines:
            # Match IP address
            ip_match = re.match(r"Nmap scan report for (.*)", line)
            # Match vulnerabilities (e.g., CVE entries)
            vuln_match = re.match(r"\|\s+VULNERABLE:\s+(.*)", line)
            cve_match = re.search(r"ID:\s+(CVE-\d+-\d+)", line)
            # Match additional vulnerability descriptions
            desc_match = re.match(r"\|\s+(.*)", line)

            if ip_match:
                # Save the previous IP's data
                if current_ip and vulnerabilities:
                    results.append({"ip": current_ip, "vulnerabilities": vulnerabilities})
                # Start new IP entry
                current_ip = ip_match.group(1)
                vulnerabilities = []

            elif vuln_match:
                # Capture the name of a vulnerability
                vulnerabilities.append({"name": vuln_match.group(1), "cves": []})

            elif cve_match and vulnerabilities:
                # Append CVE to the last vulnerability entry
                vulnerabilities[-1]["cves"].append(cve_match.group(1))

            elif desc_match and vulnerabilities:
                # Append descriptive information to the last vulnerability entry
                if "description" not in vulnerabilities[-1]:
                    vulnerabilities[-1]["description"] = desc_match.group(1)
                else:
                    vulnerabilities[-1]["description"] += " " + desc_match.group(1)

        # Add the last IP's vulnerabilities
        if current_ip and vulnerabilities:
            results.append({"ip": current_ip, "vulnerabilities": vulnerabilities})

        # Log results
        for result in results:
            logging.info(f"Vulnerabilities for {result['ip']}: {result['vulnerabilities']}")

        return results

    except Exception as e:
        logging.error(f"Error during vulnerability scanning: {str(e)}")
        return []


def scan_combined(target_ip,user_id=None):
    try:
        # Perform port scanning
        ports_results = scan_ports_with_subprocess(target=target_ip, user_id=user_id)

        # Perform vulnerability scanning
        # vulnerabilities = scan_vulnerabilities(target=target_ip)

        # Fetch system info
        system_info = get_system_info(target_ip)

        # Combine results
        combined_results = {
            "ip": target_ip,
            "ports": ports_results,
            # "vulnerabilities": vulnerabilities,
            "system_info": system_info,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Store in Appwrite
        # document_id = str(uuid.uuid4())
        # databases.create_document(
        #     database_id=database_id,
        #     collection_id="6755334d002b8b1b69b9",
        #     document_id=document_id,
        #     data=combined_results
        # )

        logging.info(f"Scan results stored for {target_ip}")
        return combined_results

    except Exception as e:
        logging.error(f"Error during combined scan for {target_ip}: {str(e)}")
        return {"error": str(e)}
