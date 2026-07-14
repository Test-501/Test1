
import os
import uuid
import threading
import subprocess
import time
import shutil
import sys
import psutil
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
# Enable Global Resource Policy Allocation (CORS Handling)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# Firebase Structural Management Connection
# ==========================================
firebase_service_account = {
  "type": "service_account",
  "project_id": "test1-b9469",
  "private_key_id": "83a6f9f182491046dfa93b048a43281799cb1881",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDBKmtSWzf1zVhw\naG0tiO+aOTvLVHTLXacxFRS8cF58+R6E06gRNN7kpRF8QR+sthF0ohBrNr06nfiZ\nXaoe1y2WXZqdgy1DH12IGiM5/v+s93/QQsQUPj4W6f6+lLy14EGMRjg7ty0uRR93\nVqQ7RYQOJ1j8X0mo5XHpycD9mJTxrBNBv3iyoXTkyQYi6mbG9egKgqxY+8VJGxSP\nGuTpX1YQ1uiqCwtbDcmfCCOcEaAeZapdAwHRMqdM6Z7f5+qieLj+AlZARq559yxk\nQsNI+BxR7ezWUMmdjmyCXN48KYjod47LkinFuVmUIqkuOZPNlkeWUJsQAAHyi2qv\n5Iy2zp/vAgMBAAECggEAEXgropQbWICMugXHsfGLcdAxRy9JLMc4gqjcajpjYTwK\ndYrKzVuRuO3wyeL94VnJ9Flf0MJvlKiKvhwJcaaWOd4XSJ1/b22bwN5URz93kgYE\nKiqPnyEN7naVEllTQ8OXSf9jwIrNbDzWHq3YRn//9GO8mX5oo/y0M6eKa6Tr+3sj\nFt+rlVo/V6uwFKtWgVnHDwIeu4DPq0heM+85EQQvexPRLbB9sAxp4pP3POOf88LE\n7OUFHgcmvqRKcsRT+y9YFaZEgarbM/DW8zh7DB92yZGXqpmRsWHwR18H5IkWCrK+\n7AMm+yQaJrdm6Ax5CDZ+ONDLYXdDibiZq+w8DNEu8QKBgQDyjFmL4h4tMP0sKL1G\nP2ZtTJ93mqIEIcTFF9J1HYUrgXnGBF95oXq4hjLh3HNF7qZVYQuLKYE6KY1xuzqXndjqpA37jj3p0zJW/mNKVcSoSykyt5TQh8uLogmY174PAf8tssETmwz1ZR9SlaVDJ\njXuEm8ag89DInNt7qIo5NF9/mQKBgQDL4PI8lubZ6U9h4zkgf/JJFHroe4JC5h2I\n8REFZ1VJIPOmJTsfrJzJs2GNjpn0G1Rbx6nNr2mxplxCQwHzAUCOUOHyHD6Ec6F7\n0q0GeAaUZCcWl5B71CZ/lLQ3ae7LvnYSso69ytlpx/u07IsaTJB8FkSD9+ANc742\nnmZgxGvwxwKBgQCzRfmJ4v/a9zKpyRLdMU9Lyi60AJ9v3mXKJ+lulvsvROv06JaJ\nGEnUyZwiRQcO0W4v/SLDIVJa4wug3HpaKRECi4rmN86TNgQZMaO0wYgPi2dRwO/f\nh98fbAKQKxB+3/ZDx6Wlyvk1XFpYSJdl4iVBxsHxhUT0grvXkqNX1NYhQQKBgAHQ\nS3dchEs19x3QzqZKXRZnVzyQNLVxpJueQV+B7tFKuMAmnqMGfxKQRPLkbNwuDg8O\n9KS+xbrt1u5D+FV4EmHxuEDWHXxCJxKZ6i4fjTduuKZLzN49IeaKpRvFFnm7hQNf\nkUOA9XQqckPGwuoF+lcQP6XI47Za7DtCJ3j+5lLrAoGBANmZQAizRQTwFp2KvQPL\nzvUisRvs5Jms9Ur7Zq4oC9TZfbIJvHfZzTujroeYBmFEL4MFL1c2ql9/pKGVCQu1\nWp74hSRIs12xHcLuvR16HYD5YzllP8RPVxM8ymAlS/fPBCsQ10550hczY2ewM91L\nWVdnHAI4eJqGJCAQRdoAI37i\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@test1-b9469.iam.gserviceaccount.com",
  "client_id": "107162408337891769572",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40test1-b9469.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

db_client = None
try:
    cred = credentials.Certificate(firebase_service_account)
    firebase_admin.initialize_app(cred)
    db_client = firestore.client()
    print("✅ Firebase Datastore Synchronized!")
except Exception as e:
    print(f"❌ Firebase Link Interrupted: {e}")

WORKSPACE_DIR = os.path.join(os.getcwd(), "bot_workspaces")
BACKUP_DIR = os.path.join(os.getcwd(), "bot_backups")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

active_processes = {} # Structures: { bot_id: SubprocessObject }
bot_configs = {}      # Structures: { bot_id: configurationDict }

# ==========================================
# Real-Time Operational Process Pipeline
# ==========================================
def orchestrate_bot_process(bot_id):
    bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
    log_path = os.path.join(bot_dir, "console.log")
    
    settings = bot_configs.get(bot_id, {"auto_restart": True})
    crash_retry_counter = 0

    while True:
        try:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🛠️ Initializing Process Node Subsystem...\n")
                log_file.flush()
                
                runtime_start_checkpoint = time.time()
                
                # Dependencies Verification & Real-time Installation logs output
                req_path = os.path.join(bot_dir, "requirements.txt")
                if os.path.exists(req_path):
                    with open(req_path, "r", encoding="utf-8") as f:
                        packages_list = f.read().strip()
                    if packages_list:
                        log_file.write("📦 Found custom dependencies. Executing dynamic package installation...\n")
                        log_file.flush()
                        
                        installation_task = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "-r", req_path], 
                            stdout=log_file, 
                            stderr=subprocess.STDOUT
                        )
                        
                        if installation_task.returncode == 0:
                            log_file.write("✅ Package configuration completely resolved.\n")
                        else:
                            log_file.write("❌ Critical package install error detected.\n")
                        log_file.flush()
                
                # Executing primary target process with live log output
                log_file.write("🔥 Booting operational execution tree from 'bot.py'...\n")
                log_file.flush()
                
                execution_task = subprocess.Popen(
                    [sys.executable, "-u", "bot.py"], 
                    stdout=log_file, 
                    stderr=subprocess.STDOUT, 
                    cwd=bot_dir
                )
                
                active_processes[bot_id] = execution_task
                if db_client:
                    db_client.collection("bot_instances").document(bot_id).update({"status": "running"})
                
                execution_task.wait() # Hold worker context open while thread runs
                measured_operational_duration = time.time() - runtime_start_checkpoint
                
                # Dynamic Fail-safe Rollback Implementation
                if execution_task.returncode != 0 and measured_operational_duration < 10:
                    log_file.write(f"\n🚨 SYSTEM ANOMALY: Process crashed prematurely in {round(measured_operational_duration, 1)} seconds.\n")
                    log_file.write("🔄 Rolling back workspace data parameters to target recovery checkpoint...\n")
                    log_file.flush()
                    
                    backup_dir = os.path.join(BACKUP_DIR, bot_id)
                    if os.path.exists(backup_dir):
                        try:
                            shutil.rmtree(bot_dir)
                            shutil.copytree(backup_dir, bot_dir)
                            log_file.write("✅ Workspace structural parameters successfully rolled back to stable storage node. Process execution aborted.\n")
                        except Exception as path_err:
                            log_file.write(f"❌ Structural roll back transaction execution failed: {path_err}\n")
                    else:
                        log_file.write("❌ Safe roll back process denied: Verification recovery backup node doesn't exist.\n")
                    log_file.flush()
                    break 
                
                # Processing Auto-Restart Conditional Logic Verification
                if not settings.get("auto_restart", True):
                    log_file.write("\n⏹️ Auto-restart configuration flag set to false. Context closed naturally.\n")
                    break
                
                if execution_task.returncode == 0:
                    log_file.write("\n✅ Operational routine finished executing gracefully (Exit Code 0).\n")
                    break 
                    
                crash_retry_counter += 1
                log_file.write(f"\n⚠️ Process engine error crash detected. Attempting automated recovery sequence in 5s... (Sequence: {crash_retry_counter})\n")
                log_file.flush()
                time.sleep(5)

        except Exception as crash_exception:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n💥 CORRUPT APPLICATION PIPELINE EXCEPTION: {crash_exception}\n")
            break
            
    if bot_id in active_processes:
        del active_processes[bot_id]
    if db_client:
        db_client.collection("bot_instances").document(bot_id).update({"status": "stopped"})

# ==========================================
# REST API Interface Routing
# ==========================================

@app.route('/', methods=['GET'])
def server_root_check():
    return """
    <html>
        <body style="background:#0b0f19; color:#38bdf8; font-family:monospace; padding:100px; text-align:center;">
            <div style="border:1px solid #242f47; display:inline-block; padding:30px; border-radius:12px; background:#151b2c;">
                <h1 style="color:#10b981; margin-bottom:10px;">✅ PyEngine Node Cluster Online</h1>
                <p style="color:#94a3b8; font-size:14px;">The API backend service link endpoint is operating securely.</p>
            </div>
        </body>
    </html>
    """

@app.route('/api/deploy', methods=['POST'])
def receive_deployment_manifest():
    payload = request.json
    bot_name = payload.get('bot_name')
    files_cluster = payload.get('files', {}) 
    settings = payload.get('settings', {"auto_restart": True})
    
    bot_id = str(uuid.uuid4().hex)[:10]
    bot_configs[bot_id] = settings
    
    bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
    backup_dir = os.path.join(BACKUP_DIR, bot_id)
    
    # Save structural configuration state data for dynamic recovery loops
    if os.path.exists(bot_dir):
        if os.path.exists(backup_dir): 
            try: shutil.rmtree(backup_dir)
            except: pass
        try: shutil.copytree(bot_dir, backup_dir)
        except: pass
    else:
        os.makedirs(bot_dir, exist_ok=True)
        
    # Write structural file allocations directly onto localized disk matrices
    for target_filename, code_payload in files_cluster.items():
        if not code_payload.strip() and target_filename != "bot.py":
            continue
        sanitized_path = os.path.basename(target_filename) 
        with open(os.path.join(bot_dir, sanitized_path), "w", encoding="utf-8") as storage_target:
            storage_target.write(code_payload)
            
    # Purge historical log context traces
    with open(os.path.join(bot_dir, "console.log"), "w", encoding="utf-8") as initial_log:
        initial_log.write(f"📝 Dynamic deployment pipeline successfully initialized for '{bot_name}'.\n")
            
    if db_client:
        meta_document = {
            "bot_name": bot_name,
            "status": "running",
            "settings": settings
        }
        db_client.collection("bot_instances").document(bot_id).set(meta_document)
    
    # Fire processing runtime thread asynchronously
    threading.Thread(target=orchestrate_bot_process, args=(bot_id,)).start()
    return jsonify({"success": True, "bot_id": bot_id})

@app.route('/api/stats/<bot_id>', methods=['GET'])
def calculate_resource_allocation(bot_id):
    if bot_id in active_processes:
        target_process = active_processes[bot_id]
        try:
            if target_process.poll() is None:
                process_tracker = psutil.Process(target_process.pid)
                cpu_metric = process_tracker.cpu_percent(interval=0.05)
                ram_bytes = process_tracker.memory_info().rss
                ram_megabytes = ram_bytes / (1024 * 1024)
                return jsonify({"success": True, "cpu": round(cpu_metric, 1), "ram": round(ram_megabytes, 1)})
        except:
            pass
    return jsonify({"success": False, "cpu": 0.0, "ram": 0.0})

@app.route('/api/instances', methods=['GET'])
def stream_instances_matrix():
    instances_data_map = {}
    if not db_client:
        return jsonify({"success": True, "data": {}})
    try:
        for document in db_client.collection("bot_instances").stream():
            doc_dict = document.to_dict()
            instances_data_map[document.id] = {
                "bot_name": doc_dict.get("bot_name"),
                "status": doc_dict.get("status")
            }
    except Exception as data_err:
        print(f"Matrix parsing issue: {data_err}")
    return jsonify({"success": True, "data": instances_data_map})

@app.route('/api/action/<action_type>/<bot_id>', methods=['POST'])
def enforce_node_actions(action_type, bot_id):
    if action_type in ["stop", "restart", "delete"]:
        if bot_id in active_processes:
            active_worker = active_processes[bot_id]
            if active_worker.poll() is None:
                active_worker.terminate()
            
    if action_type == "restart":
        threading.Thread(target=orchestrate_bot_process, args=(bot_id,)).start()
        
    if action_type == "delete":
        if db_client: 
            db_client.collection("bot_instances").document(bot_id).delete()
        bot_target_dir = os.path.join(WORKSPACE_DIR, bot_id)
        if os.path.exists(bot_target_dir): 
            try: shutil.rmtree(bot_target_dir)
            except: pass
        
    return jsonify({"success": True})

@app.route('/api/logs/<bot_id>', methods=['GET'])
def extract_live_console_logs(bot_id):
    target_log_matrix = os.path.join(WORKSPACE_DIR, bot_id, "console.log")
    if os.path.exists(target_log_matrix):
        try:
            with open(target_log_matrix, "r", encoding="utf-8") as stream_source:
                log_data_buffer = stream_source.read()
                # Return tail block segment smoothly to conserve interface processing limits
                return jsonify({"success": True, "logs": log_data_buffer[-20000:]}) 
        except:
            return jsonify({"success": False, "logs": "File execution stream lock error."})
    return jsonify({"success": False, "logs": "Pipeline streaming offline..."})

if __name__ == '__main__':
    target_binding_port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=target_binding_port, threaded=True)


