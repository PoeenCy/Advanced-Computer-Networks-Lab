#!/usr/bin/env python3
import os
import sys

def apply_rules():
    print(">>> Applying Micro-segmentation Rules (Zero Trust)...")
    # Xóa rule cũ
    os.system('sudo ovs-ofctl del-flows s1')
    
    # 1. ARP (Cho phép tìm MAC)
    os.system('sudo ovs-ofctl add-flow s1 priority=100,dl_type=0x0806,actions=NORMAL')
    
    # 2. CHẶN Lateral Movement (PC-A -> PC-B)
    # Chặn IP Source 10.1.1.5 đến Dest 10.1.1.6
    os.system('sudo ovs-ofctl add-flow s1 priority=90,dl_type=0x0800,nw_src=10.1.1.5,nw_dst=10.1.1.6,actions=drop')
    
    # 3. Cho phép PC-A truy cập Server PC-C (Business allowed)
    os.system('sudo ovs-ofctl add-flow s1 priority=80,dl_type=0x0800,nw_src=10.1.1.5,nw_dst=10.1.1.100,tp_dst=443,nw_proto=6,actions=NORMAL')
    os.system('sudo ovs-ofctl add-flow s1 priority=80,dl_type=0x0800,nw_src=10.1.1.100,tp_src=443,nw_proto=6,actions=NORMAL')
    
    # 4. Drop all others (Zero Trust)
    os.system('sudo ovs-ofctl add-flow s1 priority=1,actions=drop')
    
    print(">>> SECURED! PC-A is now isolated from PC-B.")

def remove_rules():
    print(">>> Removing Security (Flat Network)...")
    os.system('sudo ovs-ofctl del-flows s1')
    os.system('sudo ovs-ofctl add-flow s1 action=NORMAL')
    print(">>> UNSAFE! Network is flat.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 apply_security.py [on|off]")
    elif sys.argv[1] == "on":
        apply_rules()
    elif sys.argv[1] == "off":
        remove_rules()