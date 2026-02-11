#!/usr/bin/env python3
# siem_dashboard.py
import time
import os
import sys

# Màu sắc
R = '\033[91m' # Red (Alert)
G = '\033[92m' # Green (Safe)
Y = '\033[93m' # Yellow (Warning)
C = '\033[96m' # Cyan
W = '\033[0m'  # White

def clear():
    os.system('clear')

def analyze_log_line(line, server_name):
    """Phân tích log để tìm dấu hiệu tấn công"""
    # Pattern nhận diện tấn công (Signature based detection)
    alerts = []
    
    if "cmd.exe" in line or "/bin/sh" in line or "whoami" in line:
        alerts.append(f"{R}[CRITICAL] RCE ATTEMPT DETECTED (Command Injection){W}")
    if "SELECT" in line or "UNION" in line or "%27" in line:
        alerts.append(f"{R}[HIGH] SQL INJECTION DETECTED{W}")
    if "404" in line:
        alerts.append(f"{Y}[INFO] 404 Not Found (Possible Scanning){W}")
    if "confidential" in line:
        alerts.append(f"{R}[CRITICAL] DATA EXFILTRATION ATTEMPT (Sensitive File){W}")
        
    return alerts

def tail_logs():
    files = {
        'PC-B (Web App)': '/tmp/lab_logs/pc_b_access.log',
        'PC-C (File Srv)': '/tmp/lab_logs/pc_c_access.log'
    }
    
    # Mở file
    f_handles = {}
    for name, path in files.items():
        try:
            f = open(path, 'r')
            f.seek(0, 2) # Nhảy đến cuối file
            f_handles[name] = f
        except:
            pass

    print(f"{C}Initializing Micro-SIEM v2.0... Monitoring Logs...{W}")
    print(f"{Y}Waiting for traffic...{W}\n")

    try:
        while True:
            has_data = False
            for name, f in f_handles.items():
                line = f.readline()
                if line:
                    has_data = True
                    # Làm sạch dòng log
                    log_clean = line.strip().split(']')[-1].strip() # Bỏ timestamp python
                    
                    # Phân tích
                    alerts = analyze_log_line(log_clean, name)
                    
                    # In ra màn hình
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"{C}[{timestamp}] SOURCE: {name}{W}")
                    print(f"   LOG: {log_clean}")
                    
                    if alerts:
                        for alert in alerts:
                            print(f"   ALERT: {alert}")
                    else:
                        print(f"   STATUS: {G}Clean Traffic{W}")
                    print("-" * 50)
            
            if not has_data:
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\nSIEM Stopped.")

if __name__ == '__main__':
    if not os.path.exists('/tmp/lab_logs/pc_b_access.log'):
        print(f"{R}Error: Logs not found. Please run infrastructure.py first.{W}")
    else:
        tail_logs()