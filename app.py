
import os
import sys
import uuid
import time
import json
import shutil
import psutil
import threading
import subprocess
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# ==========================================
# 🚀 CORE SYSTEM CONFIGURATION
# ==========================================
app = Flask(__name__)
# Allowing all origins to fix any CORS related issues with the frontend
CORS(app, resources={r"/*": {"origins": "*"}})

WORKSPACE_DIR = os.path.join(os.getcwd(), "bot_workspaces")
BACKUP_DIR = os.path.join(os.getcwd(), "bot_backups")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

active_processes = {}
bot_configs = {}
db_client = None
system_boot_time = time.time()

# ==========================================
# 🔥 FIREBASE DATABASE LINK (PERSISTENT STORAGE)
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

try:
    cred = credentials.Certificate(firebase_service_account)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db_client = firestore.client()
    print("[SYSTEM] Firebase Datastore Successfully Synchronized.")
except Exception as e:
    print(f"[ERROR] Firebase Connection Failed: {e}")

# ==========================================
# 🛡️ ADVANCED PROCESS MANAGEMENT & MEMORY CLEANUP
# ==========================================
def kill_process_tree(pid, including_parent=True):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        gone, alive = psutil.wait_procs(children, timeout=3)
        for p in alive:
            p.kill()
        if including_parent:
            parent.terminate()
            parent.wait(3)
            if parent.is_running():
                parent.kill()
    except Exception as e:
        print(f"[WARN] Process kill exception: {e}")

def write_log(bot_dir, text_content):
    log_path = os.path.join(bot_dir, "console.log")
    try:
        with open(log_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"[{timestamp}] {text_content}\n")
            log_file.flush()
    except Exception:
        pass

# ==========================================
# ⚙️ MAIN BOT ORCHESTRATOR ENGINE
# ==========================================
def orchestrate_bot_process(bot_id):
    bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
    settings = bot_configs.get(bot_id, {"auto_restart": True})
    crash_retry_counter = 0

    while True:
        try:
            write_log(bot_dir, "🚀 SYSTEM_BOOT: Initializing Container Environment...")
            
            runtime_start = time.time()
            libs_dir = os.path.join(bot_dir, "libs")
            os.makedirs(libs_dir, exist_ok=True)
            
            # Handling Requirements
            req_path = os.path.join(bot_dir, "requirements.txt")
            if os.path.exists(req_path):
                with open(req_path, "r", encoding="utf-8") as f:
                    packages = f.read().strip()
                if packages:
                    write_log(bot_dir, "📦 [PKG_MANAGER] Found requirements.txt. Installing dependencies...")
                    log_file_obj = open(os.path.join(bot_dir, "console.log"), "a", encoding="utf-8")
                    
                    install_task = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", "-t", libs_dir, "-r", req_path], 
                        stdout=log_file_obj, 
                        stderr=subprocess.STDOUT
                    )
                    log_file_obj.close()
                    
                    if install_task.returncode == 0:
                        write_log(bot_dir, "✅ [PKG_MANAGER] All dependencies installed successfully.")
                    else:
                        write_log(bot_dir, "❌ [PKG_MANAGER] WARNING: Some dependencies failed to install.")

            # Setting up execution environment to use local libs
            custom_env = os.environ.copy()
            if "PYTHONPATH" in custom_env:
                custom_env["PYTHONPATH"] = f"{libs_dir}{os.pathsep}{custom_env['PYTHONPATH']}"
            else:
                custom_env["PYTHONPATH"] = libs_dir

            write_log(bot_dir, "🔥 [EXECUTION] Launching main script (bot.py)...")
            log_file_obj = open(os.path.join(bot_dir, "console.log"), "a", encoding="utf-8")
            
            # Run Bot
            execution_task = subprocess.Popen(
                [sys.executable, "-u", "bot.py"], 
                stdout=log_file_obj, 
                stderr=subprocess.STDOUT, 
                cwd=bot_dir,
                env=custom_env
            )
            
            active_processes[bot_id] = execution_task
            
            # Update DB Status
            if db_client:
                try:
                    db_client.collection("bot_instances").document(bot_id).update({"status": "running"})
                except:
                    pass
            
            # Wait for bot to finish or crash
            execution_task.wait() 
            log_file_obj.close()
            
            measured_duration = time.time() - runtime_start
            
            if bot_id in active_processes:
                del active_processes[bot_id]
            
            # Handle Termination or Crash
            if not settings.get("auto_restart", True):
                write_log(bot_dir, "⏹️ [TERMINATED] Process ended. Auto-restart is currently disabled.")
                break
            
            if execution_task.returncode == 0:
                write_log(bot_dir, "✅ [EXIT] Process completed gracefully with Exit Code 0.")
                break 
                
            # Crash Recovery Logic
            crash_retry_counter += 1
            write_log(bot_dir, f"🚨 [FATAL ERROR] Process crashed abnormally (Exit Code: {execution_task.returncode}).")
            
            if measured_duration < 3:
                write_log(bot_dir, "⚠️ [CRITICAL] App crashed immediately. Check your code for syntax errors.")
                
            write_log(bot_dir, f"🔄 [RECOVERY] Attempting auto-restart in 5 seconds (Attempt {crash_retry_counter})...")
            time.sleep(5)

        except Exception as general_error:
            write_log(bot_dir, f"💥 [SYSTEM FAILURE] Pipeline Exception: {str(general_error)}")
            write_log(bot_dir, traceback.format_exc())
            break
            
    # Cleanup after loop ends
    if bot_id in active_processes:
        del active_processes[bot_id]
    if db_client:
        try:
            db_client.collection("bot_instances").document(bot_id).update({"status": "stopped"})
        except:
            pass

def sync_bots_from_database():
    """Restores bots if Render server restarts"""
    if not db_client:
        return
    try:
        bots = db_client.collection("bot_instances").stream()
        restored_count = 0
        for doc in bots:
            bot_id = doc.id
            data = doc.to_dict()
            bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
            os.makedirs(bot_dir, exist_ok=True)
            
            bot_configs[bot_id] = data.get("settings", {"auto_restart": True})
            files_dict = data.get("files", {})
            
            # Restore files
            for filename, filecontent in files_dict.items():
                with open(os.path.join(bot_dir, filename), "w", encoding="utf-8") as f:
                    f.write(filecontent)
                    
            if not os.path.exists(os.path.join(bot_dir, "console.log")):
                with open(os.path.join(bot_dir, "console.log"), "w", encoding="utf-8") as f:
                    f.write("[SYSTEM] Node synchronized from Cloud Database.\n")
                    
            # Restart if it was supposed to be running
            threading.Thread(target=orchestrate_bot_process, args=(bot_id,), daemon=True).start()
            restored_count += 1
        print(f"[SYSTEM] Successfully restored {restored_count} bots from Firebase.")
    except Exception as e:
        print(f"[ERROR] Database sync failed: {e}")

# ==========================================
# 🌐 API ROUTING (COMMUNICATION WITH PHP FRONTEND)
# ==========================================

@app.route('/', methods=['GET'])
def server_root_check():
    return jsonify({
        "status": "online",
        "uptime_seconds": round(time.time() - system_boot_time, 2),
        "cpu_usage": psutil.cpu_percent(),
        "ram_usage": psutil.virtual_memory().percent,
        "active_nodes": len(active_processes)
    })

@app.route('/api/deploy', methods=['POST'])
def receive_deployment_manifest():
    try:
        payload = request.json
        bot_name = payload.get('bot_name')
        files_cluster = payload.get('files', {}) 
        settings = payload.get('settings', {"auto_restart": True})
        
        # Validation
        if not bot_name:
            return jsonify({"success": False, "error": "Project Name is required."}), 400
        if 'bot.py' not in files_cluster or not files_cluster['bot.py'].strip():
            return jsonify({"success": False, "error": "bot.py file is missing or empty."}), 400

        bot_id = str(uuid.uuid4().hex)[:12]
        bot_configs[bot_id] = settings
        
        bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
        os.makedirs(bot_dir, exist_ok=True)
            
        # Write Files
        for target_filename, code_payload in files_cluster.items():
            sanitized_path = os.path.basename(target_filename) 
            with open(os.path.join(bot_dir, sanitized_path), "w", encoding="utf-8") as storage_target:
                storage_target.write(code_payload)
                
        # Init Log
        with open(os.path.join(bot_dir, "console.log"), "w", encoding="utf-8") as initial_log:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            initial_log.write(f"[{timestamp}] [DEPLOY] Generating container for '{bot_name}'...\n")
                
        # Save to DB
        if db_client:
            try:
                meta_document = {
                    "bot_name": bot_name,
                    "status": "starting",
                    "settings": settings,
                    "files": files_cluster,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                db_client.collection("bot_instances").document(bot_id).set(meta_document)
            except Exception as e:
                print(f"[DB ERROR] {e}")
        
        # Start Process
        threading.Thread(target=orchestrate_bot_process, args=(bot_id,), daemon=True).start()
        return jsonify({"success": True, "bot_id": bot_id, "message": "Deployment Successful"})

    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

@app.route('/api/stats/<bot_id>', methods=['GET'])
def calculate_resource_allocation(bot_id):
    if bot_id in active_processes:
        target_process = active_processes[bot_id]
        try:
            if target_process.poll() is None:
                parent = psutil.Process(target_process.pid)
                total_ram = parent.memory_info().rss
                children = parent.children(recursive=True)
                for child in children:
                    total_ram += child.memory_info().rss
                
                cpu_metric = parent.cpu_percent(interval=0.1)
                ram_megabytes = total_ram / (1024 * 1024)
                return jsonify({"success": True, "cpu": round(cpu_metric, 1), "ram": round(ram_megabytes, 2)})
        except Exception:
            pass
    return jsonify({"success": False, "cpu": 0.0, "ram": 0.0})

@app.route('/api/instances', methods=['GET'])
def stream_instances_matrix():
    instances_data_map = {}
    if not db_client:
        return jsonify({"success": False, "error": "Database disconnected."})
        
    try:
        for document in db_client.collection("bot_instances").stream():
            doc_dict = document.to_dict()
            bot_id = document.id
            real_status = "stopped"
            
            # Verify real status from RAM
            if bot_id in active_processes and active_processes[bot_id].poll() is None:
                real_status = "running"
                
            instances_data_map[bot_id] = {
                "bot_name": doc_dict.get("bot_name", "Unknown Bot"),
                "status": real_status
            }
            
            # Sync DB if mismatch
            if real_status != doc_dict.get("status"):
                db_client.collection("bot_instances").document(bot_id).update({"status": real_status})
                
        return jsonify({"success": True, "data": instances_data_map})
    except Exception as e:
         return jsonify({"success": False, "error": str(e)})

@app.route('/api/action/<action_type>/<bot_id>', methods=['POST'])
def enforce_node_actions(action_type, bot_id):
    try:
        if action_type in ["stop", "restart", "delete"]:
            if bot_id in active_processes:
                target_proc = active_processes[bot_id]
                if target_proc.poll() is None:
                    kill_process_tree(target_proc.pid)
                del active_processes[bot_id]
                
        if action_type == "restart":
            if db_client:
                 db_client.collection("bot_instances").document(bot_id).update({"status": "starting"})
            threading.Thread(target=orchestrate_bot_process, args=(bot_id,), daemon=True).start()
            
        if action_type == "delete":
            if db_client: 
                db_client.collection("bot_instances").document(bot_id).delete()
            bot_target_dir = os.path.join(WORKSPACE_DIR, bot_id)
            if os.path.exists(bot_target_dir): 
                try: shutil.rmtree(bot_target_dir)
                except: pass
                
        return jsonify({"success": True, "message": f"Action {action_type} executed."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/logs/<bot_id>', methods=['GET'])
def extract_live_console_logs(bot_id):
    target_log_matrix = os.path.join(WORKSPACE_DIR, bot_id, "console.log")
    if os.path.exists(target_log_matrix):
        try:
            with open(target_log_matrix, "r", encoding="utf-8") as stream_source:
                # Read last 50KB to avoid memory overload in browser
                stream_source.seek(0, os.SEEK_END)
                file_size = stream_source.tell()
                read_size = min(50000, file_size)
                stream_source.seek(file_size - read_size)
                log_data_buffer = stream_source.read()
                return jsonify({"success": True, "logs": log_data_buffer}) 
        except Exception:
            pass
    return jsonify({"success": False, "logs": "No logs generated yet or file locked."})

if __name__ == '__main__':
    print("[SYSTEM] Starting PyEngine Backend Service...")
    sync_bots_from_database()
    target_binding_port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=target_binding_port, threaded=True)


