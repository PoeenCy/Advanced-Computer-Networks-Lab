#!/usr/bin/env python3
# infrastructure.py
import os
from mininet.net import Mininet
from mininet.node import OVSSwitch, Host
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import time

def setup_network():
    # Dọn dẹp
    os.system('sudo mn -c > /dev/null 2>&1')
    os.system('mkdir -p /tmp/lab_logs')  # Tạo thư mục log
    os.system('rm -f /tmp/lab_logs/*.log') # Xóa log cũ
    
    net = Mininet(switch=OVSSwitch, link=TCLink, controller=None)
    
    info('*** Creating Infrastructure...\n')
    s1 = net.addSwitch('s1', failMode='secure')
    r1 = net.addHost('r1', ip='10.1.1.1/24')
    
    # PC-A: Máy nhân viên Kế toán (Bị nhiễm Malware do mở email Phishing)
    pc_a = net.addHost('pc_a', ip='10.1.1.5/24')
    
    # PC-B: Web App Nội bộ (Legacy App - Có lỗ hổng RCE)
    pc_b = net.addHost('pc_b', ip='10.1.1.6/24')
    
    # PC-C: File Server chứa bảng lương
    pc_c = net.addHost('pc_c', ip='10.1.1.100/24')
    
    net.addLink(r1, s1)
    net.addLink(pc_a, s1)
    net.addLink(pc_b, s1)
    net.addLink(pc_c, s1)
    
    net.start()
    
    # Cấu hình IP Forwarding cho Router
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    info('*** Starting Application Servers with Logging...\n')
    
    # PC-B: Chạy Web Server và ghi log truy cập vào file shared
    # Giả lập Web App quản lý nhân sự
    # PC-B: Chạy Web Server từ folder resources
    # Giả lập Web App quản lý nhân sự
    # Lưu ý: Script chạy tại scripts/, resources nằm tại ../resources
    pc_b.cmd('cd ../resources && python3 -u -m http.server 80 > /tmp/lab_logs/pc_b_access.log 2>&1 &')
    
    # PC-C: File Server
    pc_c.cmd('cd ../resources && python3 -u -m http.server 443 > /tmp/lab_logs/pc_c_access.log 2>&1 &')

    # Mặc định áp dụng mạng phẳng (Allow All)
    s1.cmd('ovs-ofctl del-flows s1')
    s1.cmd('ovs-ofctl add-flow s1 action=NORMAL')

    info('*** INFRASTRUCTURE READY. LOGS ARE BEING WRITTEN TO /tmp/lab_logs/ ***\n')
    info('*** DO NOT CLOSE THIS TERMINAL ***\n')
    
    # Giữ mạng chạy
    while True:
        time.sleep(1)

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()