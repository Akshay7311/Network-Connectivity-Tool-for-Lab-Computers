from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.scan_utils import scan_network, scan_ports_with_subprocess, get_uptime, get_os_info, log_scan_results
from datetime import datetime
from config import databases
import os
from dotenv import load_dotenv

load_dotenv()


# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)
database_id = os.getenv('DATABASE_ID')
scan_result_collection_id = os.getenv('SCAN_RESULT_COLLECTION_ID')
log_result_collection_id = os.getenv('LOG_RESULT_COLLECTION_ID')

# API endpoint: Scan network
@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.json
        target = data.get('target', '192.168.1.0/24')
        session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Perform scan
        devices = scan_network(target)
        log_scan_results(devices)

        os_info = get_os_info()
        uptime = get_uptime()

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
        data = request.json
        target = data.get('target', '192.168.1.0/24')

        ports_results = scan_ports_with_subprocess(target)

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


# APPWRITE 
@app.route('/get_scan_results', methods=['GET'])
def get_scan_results():
    try:
        # Fetch scan results from Appwrite
        documents = databases.list_documents(collection_id=scan_result_collection_id, database_id=database_id)
        return jsonify({"results": documents['documents']}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_logs', methods=['GET'])
def get_logs():
    try:
        # Fetch logs from Appwrite
        documents = databases.list_documents(collection_id=log_result_collection_id, database_id=database_id)
        return jsonify({"logs": documents['documents']}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500    



# Run the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)