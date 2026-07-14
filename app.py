
import os
import uuid
import threading
import subprocess
import time
import shutil
import sys
import psutil # pip install psutil
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
# যেকোনো ডোমেইন থেকে অ্যাক্সেস অ্যালাউ করার জন্য (CORS)
CORS(app)

# ==========================================
# আপনার দেওয়া অরিজিনাল ফায়ারবেস সেটআপ 
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
    print("✅ Firebase Connected Pro Version!")
except Exception as e:
    print(f"❌ Firebase Error: {e}")

WORKSPACE_DIR = os.path.join(os.getcwd(), "bot_workspaces")
BACKUP_DIR = os.path.join(os.getcwd(), "bot_backups")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

active_processes = {} # { bot_id: subprocess object }
bot_configs = {}      # { bot_id: settings }

# ==========================================
# Pro Bot Execution Engine (Rollback & Auto-Restart)
# ==========================================
def run_bot_instance(bot_id):
    bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
    log_path = os.path.join(bot_dir, "console.log")
    
    settings = bot_configs.get(bot_id, {"auto_restart": True})
    retry_count = 0

    while True: # Auto-restart Loop
        try:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n[{time.strftime('%H:%M:%S')}] 🚀 Bot Engine Started...\n")
                log_file.flush()
                
                start_time = time.time()
                
                # Requirements Install Process
                req_path = os.path.join(bot_dir, "requirements.txt")
                if os.path.exists(req_path):
                    with open(req_path, "r") as f:
                        reqs = f.read().strip()
                    if reqs:
                        log_file.write("📦 Installing dependencies from requirements.txt...\n")
                        log_file.flush()
                        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path], stdout=log_file, stderr=subprocess.STDOUT)
                        log_file.write("✅ Dependencies installation complete.\n")
                        log_file.flush()
                
                # Run the Bot
                log_file.write("🔥 Starting bot.py...\n")
                log_file.flush()
                
                process = subprocess.Popen(
                    [sys.executable, "-u", "bot.py"], 
                    stdout=log_file, 
                    stderr=subprocess.STDOUT, 
                    cwd=bot_dir
                )
                
                active_processes[bot_id] = process
                if db_client:
                    db_client.collection("bot_instances").document(bot_id).update({"status": "running"})
                
                process.wait() # Wait for process to end/crash
                run_duration = time.time() - start_time
                
                # --- ROLLBACK SYSTEM ---
                if process.returncode != 0 and run_duration < 10:
                    # যদি ১০ সেকেন্ডের আগেই ক্র্যাশ করে, তবে রোলব্যাক করবে
                    log_file.write(f"\n🚨 CRASH DETECTED ({round(run_duration,1)}s). Attempting Rollback...\n")
                    backup_dir = os.path.join(BACKUP_DIR, bot_id)
                    if os.path.exists(backup_dir):
                        try:
                            shutil.rmtree(bot_dir)
                            shutil.copytree(backup_dir, bot_dir)
                            log_file.write("🔄 Rollback Successful! Restored previous working version.\n")
                        except Exception as e:
                            log_file.write(f"❌ Rollback failed: {e}\n")
                    else:
                        log_file.write("❌ No backup found to rollback.\n")
                        break # No backup, stop trying
                
                # --- AUTO RESTART CHECK ---
                if not settings.get("auto_restart", True):
                    log_file.write("\n⏹️ Auto-restart is disabled. Stopping naturally.\n")
                    break
                
                if process.returncode == 0:
                    log_file.write("\n✅ Bot exited gracefully with code 0.\n")
                    break # Natural exit, don't restart
                    
                retry_count += 1
                log_file.write(f"\n⚠️ Bot Crashed! Auto-restarting in 5 seconds... (Retry {retry_count})\n")
                time.sleep(5)

        except Exception as e:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n💥 SYSTEM FATAL ERROR: {e}\n")
            break
            
    # Loop ended - Cleanup
    if bot_id in active_processes:
        del active_processes[bot_id]
    if db_client:
        db_client.collection("bot_instances").document(bot_id).update({"status": "stopped"})

# ==========================================
# Scheduler System (Background Thread)
# ==========================================
def cron_scheduler():
    while True:
        try:
            if db_client:
                docs = db_client.collection("bot_instances").where("status", "==", "scheduled").stream()
                for doc in docs:
                    bot_id = doc.id
                    # For a real cron job, you'd parse cron syntax here
                    if bot_id not in active_processes:
                        threading.Thread(target=run_bot_instance, args=(bot_id,)).start()
        except Exception:
            pass
        time.sleep(60)

threading.Thread(target=cron_scheduler, daemon=True).start()

# ==========================================
# API Routes
# ==========================================
@app.route('/api/deploy', methods=['POST'])
def deploy_new_bot():
    payload = request.json
    bot_name = payload.get('bot_name')
    files_dict = payload.get('files', {}) # Multiple files support
    settings = payload.get('settings', {"auto_restart": True})
    cron = payload.get('cron', '')
    
    bot_id = str(uuid.uuid4().hex)[:10]
    bot_configs[bot_id] = settings
    
    bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
    backup_dir = os.path.join(BACKUP_DIR, bot_id)
    
    # Create Backup of old version if updating
    if os.path.exists(bot_dir):
        if os.path.exists(backup_dir): 
            try: shutil.rmtree(backup_dir)
            except: pass
        try: shutil.copytree(bot_dir, backup_dir)
        except: pass
    else:
        os.makedirs(bot_dir, exist_ok=True)
        
    # Write Multiple Files from Monaco Editor
    for filename, content in files_dict.items():
        # Prevent path traversal attacks
        safe_filename = os.path.basename(filename) 
        with open(os.path.join(bot_dir, safe_filename), "w", encoding="utf-8") as f:
            f.write(content)
            
    # Clear old log
    with open(os.path.join(bot_dir, "console.log"), "w", encoding="utf-8") as f:
        f.write("System initializing files...\n")
            
    if db_client:
        metadata = {
            "bot_name": bot_name,
            "status": "deploying",
            "cron": cron,
            "settings": settings
        }
        db_client.collection("bot_instances").document(bot_id).set(metadata)
    
    # Start thread
    threading.Thread(target=run_bot_instance, args=(bot_id,)).start()
    return jsonify({"success": True, "bot_id": bot_id})

@app.route('/api/stats/<bot_id>', methods=['GET'])
def get_stats(bot_id):
    if bot_id in active_processes:
        process = active_processes[bot_id]
        try:
            # Check if process is still running
            if process.poll() is None:
                p = psutil.Process(process.pid)
                cpu = p.cpu_percent(interval=0.1)
                ram = p.memory_info().rss / (1024 * 1024) # Convert to MB
                return jsonify({"success": True, "cpu": round(cpu, 1), "ram": round(ram, 1)})
        except psutil.NoSuchProcess:
            pass
    return jsonify({"success": False, "cpu": 0, "ram": 0})

@app.route('/api/instances', methods=['GET'])
def get_instances():
    if not db_client: return jsonify({"success": False})
    instances = {}
    for doc in db_client.collection("bot_instances").stream():
        data = doc.to_dict()
        instances[doc.id] = {"bot_name": data.get("bot_name"), "status": data.get("status")}
    return jsonify({"success": True, "data": instances})

@app.route('/api/action/<action_type>/<bot_id>', methods=['POST'])
def handle_action(action_type, bot_id):
    if action_type in ["stop", "restart", "delete"]:
        if bot_id in active_processes:
            process = active_processes[bot_id]
            if process.poll() is None: # If process is alive
                process.terminate()
            
    if action_type == "restart":
        threading.Thread(target=run_bot_instance, args=(bot_id,)).start()
        
    if action_type == "delete":
        if db_client: 
            db_client.collection("bot_instances").document(bot_id).delete()
        bot_dir = os.path.join(WORKSPACE_DIR, bot_id)
        if os.path.exists(bot_dir): 
            try: shutil.rmtree(bot_dir)
            except: pass
        
    return jsonify({"success": True})

@app.route('/api/logs/<bot_id>', methods=['GET'])
def get_logs(bot_id):
    log_path = os.path.join(WORKSPACE_DIR, bot_id, "console.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                # Read last 15000 characters safely
                content = f.read()
                return jsonify({"success": True, "logs": content[-15000:]}) 
        except:
            return jsonify({"success": False, "logs": "Error reading logs."})
    return jsonify({"success": False, "logs": "No logs generated yet."})

if __name__ == '__main__':
    # Ensure psutil is installed properly
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)


