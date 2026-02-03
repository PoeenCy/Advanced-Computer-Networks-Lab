#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BÀI TẬP THỰC HÀNH SỐ 1
THIẾT KẾ VÀ TRIỂN KHAI ACL TRONG MÔ HÌNH MẠNG 3 LỚP CÓ DMZ (MININET)

Mô hình mạng:
- Core Layer: Router r1
- Distribution Layer: Switch s1, s2
- Access Layer: Switch s3, s4
- Hosts: giangvien1, giangvien2, admin1, admin2, sinhvien1, sinhvien2
- DMZ: webserver
- Outside: internet
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import os
import time
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

class NetworkTopology:
    """Quản lý cấu hình mạng 3 lớp với DMZ"""
    
    def __init__(self):
        self.net = None
        
        # Cấu hình IP cho các VLAN
        self.vlans = {
            10: {'network': '10.1.1.0/24', 'gateway': '10.1.1.1'},  # Sinh viên
            20: {'network': '10.1.2.0/24', 'gateway': '10.1.2.1'},  # Giảng viên
            99: {'network': '172.16.10.0/24', 'gateway': '172.16.10.1'}  # DMZ
        }
        
        # Cấu hình Outside network
        self.outside_network = '203.0.113.0/24'
        self.outside_gateway = '203.0.113.1'
        
    def cleanup_mininet(self):
        """Dọn dẹp Mininet trước khi chạy"""
        info('*** Đang dọn dẹp Mininet...\n')
        os.system('sudo mn -c')
        time.sleep(2)
        
    def create_topology(self):
        """Tạo topology mạng 3 lớp"""
        info('*** Tạo topology mạng\n')
        self.net = Mininet(switch=OVSSwitch, link=TCLink, build=False)
        
        # ============ CORE LAYER ============
        info('*** Tạo Core Layer (Router)\n')
        r1 = self.net.addHost('r1', ip=None)  # Router sẽ có nhiều interface
        
        # ============ DISTRIBUTION LAYER ============
        info('*** Tạo Distribution Layer (Switches)\n')
        s1 = self.net.addSwitch('s1', failMode='standalone')
        s2 = self.net.addSwitch('s2', failMode='standalone')
        
        # ============ ACCESS LAYER ============
        info('*** Tạo Access Layer (Switches)\n')
        s3 = self.net.addSwitch('s3', failMode='standalone')
        s4 = self.net.addSwitch('s4', failMode='standalone')
        
        # ============ HOSTS - VLAN 20 (Giảng viên) ============
        info('*** Tạo hosts VLAN 20 (Giảng viên)\n')
        giangvien1 = self.net.addHost('giangvien1', ip='10.1.2.10/24', 
                                      defaultRoute='via 10.1.2.1')
        giangvien2 = self.net.addHost('giangvien2', ip='10.1.2.20/24', 
                                      defaultRoute='via 10.1.2.1')
        admin1 = self.net.addHost('admin1', ip='10.1.2.50/24', 
                                  defaultRoute='via 10.1.2.1')
        admin2 = self.net.addHost('admin2', ip='10.1.2.51/24', 
                                  defaultRoute='via 10.1.2.1')
        
        # ============ HOSTS - VLAN 10 (Sinh viên) ============
        info('*** Tạo hosts VLAN 10 (Sinh viên)\n')
        sinhvien1 = self.net.addHost('sinhvien1', ip='10.1.1.10/24', 
                                     defaultRoute='via 10.1.1.1')
        sinhvien2 = self.net.addHost('sinhvien2', ip='10.1.1.20/24', 
                                     defaultRoute='via 10.1.1.1')
        
        # ============ DMZ - VLAN 99 ============
        info('*** Tạo DMZ (Web Server)\n')
        webserver = self.net.addHost('webserver', ip='172.16.10.100/24', 
                                     defaultRoute='via 172.16.10.1')
        
        # ============ OUTSIDE (Internet) ============
        info('*** Tạo Outside (Internet giả lập)\n')
        internet = self.net.addHost('internet', ip='203.0.113.10/24', 
                                    defaultRoute='via 203.0.113.1')
        
        # ============ LINKS ============
        info('*** Tạo các kết nối\n')
        
        # Router r1 kết nối với Distribution switches
        self.net.addLink(r1, s1)  # r1-eth0 - s1 (Internal VLANs)
        self.net.addLink(r1, s2)  # r1-eth1 - s2 (Distribution right)
        
        # Router r1 kết nối trực tiếp với webserver (DMZ - VLAN 99)
        self.net.addLink(r1, webserver)  # r1-eth2 - webserver (DMZ)
        
        # Router r1 kết nối với Outside
        self.net.addLink(r1, internet)  # r1-eth3 - internet (direct)
        
        # Distribution to Access layer
        self.net.addLink(s1, s3)  # s1 to s3 (VLAN 20)
        self.net.addLink(s2, s4)  # s2 to s4 (VLAN 10)
        
        # Access layer s3 to hosts (VLAN 20 - Giảng viên)
        self.net.addLink(s3, giangvien1)
        self.net.addLink(s3, giangvien2)
        self.net.addLink(s3, admin1)
        self.net.addLink(s3, admin2)
        
        # Access layer s4 to hosts (VLAN 10 - Sinh viên)
        self.net.addLink(s4, sinhvien1)
        self.net.addLink(s4, sinhvien2)
        
        return self.net
        
    def configure_vlans(self):
        """Cấu hình VLAN trên các switch"""
        info('*** Cấu hình VLANs\n')
        
        # Lấy các node
        s1 = self.net.get('s1')
        s2 = self.net.get('s2')
        s3 = self.net.get('s3')
        s4 = self.net.get('s4')
        
        # ============ Switch s1 (Distribution - Left side for VLAN 20) ============
        # Trunk port đến router r1 (allow VLAN 20)
        s1.cmd('ovs-vsctl set port s1-eth1 trunks=20')
        
        # Trunk port đến s3 (Access switch VLAN 20)
        s1.cmd('ovs-vsctl set port s1-eth2 trunks=20')  # to s3
        
        # ============ Switch s2 (Distribution - Right side for VLAN 10) ============
        # Trunk port đến router r1 (allow VLAN 10)
        s2.cmd('ovs-vsctl set port s2-eth1 trunks=10')
        
        # Trunk port đến s4 (Access switch VLAN 10)
        s2.cmd('ovs-vsctl set port s2-eth2 trunks=10')  # to s4
        
        # ============ Switch s3 (Access - VLAN 20 Giảng viên) ============
        # Trunk port đến s1
        s3.cmd('ovs-vsctl set port s3-eth1 trunks=20')
        
        # Access ports cho hosts VLAN 20
        s3.cmd('ovs-vsctl set port s3-eth2 tag=20')  # giangvien1
        s3.cmd('ovs-vsctl set port s3-eth3 tag=20')  # giangvien2
        s3.cmd('ovs-vsctl set port s3-eth4 tag=20')  # admin1
        s3.cmd('ovs-vsctl set port s3-eth5 tag=20')  # admin2
        
        # ============ Switch s4 (Access - VLAN 10 Sinh viên) ============
        # Trunk port đến s2
        s4.cmd('ovs-vsctl set port s4-eth1 trunks=10')
        
        # Access ports cho hosts VLAN 10
        s4.cmd('ovs-vsctl set port s4-eth2 tag=10')  # sinhvien1
        s4.cmd('ovs-vsctl set port s4-eth3 tag=10')  # sinhvien2
        
        info('*** VLANs đã được cấu hình\n')
        
    def configure_router_on_stick(self):
        """Cấu hình Router on a Stick cho inter-VLAN routing"""
        info('*** Cấu hình Router on a Stick\n')
        
        r1 = self.net.get('r1')
        
        # Enable IP forwarding
        r1.cmd('sysctl -w net.ipv4.ip_forward=1')
        
        # VLAN 20 - Giảng viên trên r1-eth0 (kết nối với s1)
        r1.cmd('ip link add link r1-eth0 name r1-eth0.20 type vlan id 20')
        r1.cmd('ip addr add 10.1.2.1/24 dev r1-eth0.20')
        r1.cmd('ip link set dev r1-eth0.20 up')
        r1.cmd('ip link set dev r1-eth0 up')
        
        # VLAN 10 - Sinh viên trên r1-eth1 (kết nối với s2)
        r1.cmd('ip link add link r1-eth1 name r1-eth1.10 type vlan id 10')
        r1.cmd('ip addr add 10.1.1.1/24 dev r1-eth1.10')
        r1.cmd('ip link set dev r1-eth1.10 up')
        r1.cmd('ip link set dev r1-eth1 up')
        
        # DMZ - VLAN 99 trên r1-eth2 (kết nối trực tiếp với webserver)
        r1.cmd('ip addr add 172.16.10.1/24 dev r1-eth2')
        r1.cmd('ip link set dev r1-eth2 up')
        
        # Outside network trên r1-eth3 (kết nối với internet)
        r1.cmd('ip addr add 203.0.113.1/24 dev r1-eth3')
        r1.cmd('ip link set dev r1-eth3 up')
        
        info('*** Router on a Stick đã được cấu hình\n')
        
    def configure_acl(self):
        """Cấu hình ACL (Access Control List) bằng iptables"""
        info('*** Cấu hình ACL với iptables\n')
        
        r1 = self.net.get('r1')
        
        # Xóa các rule cũ
        r1.cmd('iptables -F')
        r1.cmd('iptables -X')
        r1.cmd('iptables -t nat -F')
        r1.cmd('iptables -t nat -X')
        
        # Set default policy
        r1.cmd('iptables -P INPUT ACCEPT')
        r1.cmd('iptables -P FORWARD DROP')  # Drop all forward by default
        r1.cmd('iptables -P OUTPUT ACCEPT')
        
        # ============ CHÍNH SÁCH 1: SECURITY (Bảo mật) ============
        info('  - Applying Security Policy\n')
        
        # Cho phép traffic đã established/related
        r1.cmd('iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT')
        
        # Cho phép Internet (203.0.113.0/24) truy cập DMZ Web Server (172.16.10.100) 
        # qua HTTP (80) và HTTPS (443)
        r1.cmd('iptables -A FORWARD -s 203.0.113.0/24 -d 172.16.10.100 -p tcp --dport 80 -j ACCEPT')
        r1.cmd('iptables -A FORWARD -s 203.0.113.0/24 -d 172.16.10.100 -p tcp --dport 443 -j ACCEPT')
        
        # Chặn Internet truy cập Inside networks (VLAN 10 và 20)
        r1.cmd('iptables -A FORWARD -s 203.0.113.0/24 -d 10.1.1.0/24 -j DROP')
        r1.cmd('iptables -A FORWARD -s 203.0.113.0/24 -d 10.1.2.0/24 -j DROP')
        
        # Cho phép Inside -> Internet (outbound)
        r1.cmd('iptables -A FORWARD -s 10.1.1.0/24 -d 203.0.113.0/24 -j ACCEPT')
        r1.cmd('iptables -A FORWARD -s 10.1.2.0/24 -d 203.0.113.0/24 -j ACCEPT')
        
        # ============ CHÍNH SÁCH 2: PRIVACY (Riêng tư) ============
        info('  - Applying Privacy Policy\n')
        
        # Chặn VLAN 10 (Sinh viên) truy cập VLAN 20 (Giảng viên)
        r1.cmd('iptables -A FORWARD -s 10.1.1.0/24 -d 10.1.2.0/24 -j DROP')
        
        # Cho phép VLAN 10 (Sinh viên) truy cập DMZ
        r1.cmd('iptables -A FORWARD -s 10.1.1.0/24 -d 172.16.10.0/24 -j ACCEPT')
        
        # Cho phép VLAN 20 (Giảng viên) truy cập VLAN 10
        r1.cmd('iptables -A FORWARD -s 10.1.2.0/24 -d 10.1.1.0/24 -j ACCEPT')
        
        # Cho phép VLAN 20 truy cập DMZ
        r1.cmd('iptables -A FORWARD -s 10.1.2.0/24 -d 172.16.10.0/24 -j ACCEPT')
        
        # Cho phép DMZ phản hồi về Inside
        r1.cmd('iptables -A FORWARD -s 172.16.10.0/24 -d 10.1.1.0/24 -j ACCEPT')
        r1.cmd('iptables -A FORWARD -s 172.16.10.0/24 -d 10.1.2.0/24 -j ACCEPT')
        
        # ============ CHÍNH SÁCH 3: MANAGEMENT (Quản trị) ============
        info('  - Applying Management Policy\n')
        
        # Cho phép loopback
        r1.cmd('iptables -A INPUT -i lo -j ACCEPT')
        
        # Cho phép established connections
        r1.cmd('iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT')
        
        # Chỉ cho phép admin1 (10.1.2.50) SSH đến router
        r1.cmd('iptables -A INPUT -s 10.1.2.50 -p tcp --dport 22 -j ACCEPT')
        r1.cmd('iptables -A INPUT -p tcp --dport 22 -j DROP')
        
        # Cho phép ICMP (ping) cho troubleshooting
        r1.cmd('iptables -A FORWARD -p icmp -j ACCEPT')
        r1.cmd('iptables -A INPUT -p icmp -j ACCEPT')
        
        info('*** ACL đã được cấu hình\n')
        
    def setup_webserver(self):
        """Cài đặt web server đơn giản trên DMZ"""
        info('*** Setting up Web Server in DMZ\n')
        webserver = self.net.get('webserver')
        
        # Tạo file index.html
        webserver.cmd('echo "<html><body><h1>Welcome to DMZ Web Server</h1><p>IP: 172.16.10.100</p></body></html>" > /tmp/index.html')
        
        # Start simple HTTP server trên port 80 (chạy background)
        webserver.cmd('cd /tmp && python3 -m http.server 80 &')
        
        info('*** Web Server is running on http://172.16.10.100\n')
        
    def build_network(self):
        """Build toàn bộ network"""
        info('*** Starting network\n')
        self.net.build()
        self.net.start()
        
        # Cấu hình VLANs
        self.configure_vlans()
        
        # Cấu hình Router on a Stick
        self.configure_router_on_stick()
        
        # Cấu hình ACL
        self.configure_acl()
        
        # Setup Web Server
        self.setup_webserver()
        
        info('*** Network is ready!\n')
        
    def show_configuration(self):
        """Hiển thị cấu hình hiện tại"""
        print("\n" + "="*70)
        print("CẤU HÌNH MẠNG HIỆN TẠI")
        print("="*70)
        
        print("\n[VLAN Configuration]")
        print("  VLAN 10 (Sinh viên):  10.1.1.0/24  - Gateway: 10.1.1.1")
        print("  VLAN 20 (Giảng viên): 10.1.2.0/24  - Gateway: 10.1.2.1")
        print("  VLAN 99 (DMZ):        172.16.10.0/24 - Gateway: 172.16.10.1")
        print("  Outside:              203.0.113.0/24 - Gateway: 203.0.113.1")
        
        print("\n[Hosts]")
        print("  VLAN 20: giangvien1(10.1.2.10), giangvien2(10.1.2.20)")
        print("           admin1(10.1.2.50), admin2(10.1.2.51)")
        print("  VLAN 10: sinhvien1(10.1.1.10), sinhvien2(10.1.1.20)")
        print("  DMZ:     webserver(172.16.10.100)")
        print("  Outside: internet(203.0.113.10)")
        
        print("\n[ACL Policies]")
        print("  Security:   Internet → DMZ (HTTP/HTTPS) ✓")
        print("              Internet → Inside ✗")
        print("  Privacy:    VLAN 10 → VLAN 20 ✗")
        print("              VLAN 10 → DMZ ✓")
        print("  Management: Only admin1 can SSH to router")
        
        print("="*70 + "\n")

    def visualize_topology(self, save_path='network_topology.png'):
        """Vẽ sơ đồ mạng bằng networkx và matplotlib"""
        info('*** Đang vẽ sơ đồ mạng...\n')
        
        # Tạo đồ thị
        G = nx.Graph()
        
        # Định nghĩa các node và phân loại
        routers = ['r1']
        distribution_switches = ['s1', 's2']
        access_switches = ['s3', 's4']
        vlan20_hosts = ['giangvien1', 'giangvien2', 'admin1', 'admin2']
        vlan10_hosts = ['sinhvien1', 'sinhvien2']
        dmz_hosts = ['webserver']
        outside_hosts = ['internet']
        
        # Thêm tất cả các node
        all_nodes = (routers + distribution_switches + access_switches + 
                    vlan20_hosts + vlan10_hosts + dmz_hosts + outside_hosts)
        G.add_nodes_from(all_nodes)
        
        # Thêm các edge (links)
        edges = [
            # Router to distribution switches
            ('r1', 's1'), ('r1', 's2'),
            # Router directly to webserver (DMZ)
            ('r1', 'webserver'),
            # Router to outside
            ('r1', 'internet'),
            # Distribution to access
            ('s1', 's3'),  # s1 to s3 (VLAN 20)
            ('s2', 's4'),  # s2 to s4 (VLAN 10)
            # Access s3 to VLAN 20 hosts
            ('s3', 'giangvien1'), ('s3', 'giangvien2'),
            ('s3', 'admin1'), ('s3', 'admin2'),
            # Access s4 to VLAN 10 hosts
            ('s4', 'sinhvien1'), ('s4', 'sinhvien2'),
        ]
        G.add_edges_from(edges)
        
        # Tạo figure với kích thước lớn hơn
        plt.figure(figsize=(16, 12))
        ax = plt.gca()
        
        # Định nghĩa vị trí cho các node (hierarchical layout)
        pos = {}
        
        # Layer 1: Outside (top)
        pos['internet'] = (7, 10)
        
        # Layer 2: Router (core)
        pos['r1'] = (7, 8)
        
        # Layer 2.5: DMZ webserver (bên phải router, cùng tầng)
        pos['webserver'] = (10, 8)
        
        # Layer 3: Distribution switches (s1 bên trái, s2 bên phải)
        pos['s1'] = (3, 6)
        pos['s2'] = (11, 6)
        
        # Layer 4: Access switches
        pos['s3'] = (3, 4)   # Dưới s1
        pos['s4'] = (11, 4)  # Dưới s2
        
        # Layer 5: End hosts
        # VLAN 20 (left side - under s3)
        pos['giangvien1'] = (1, 2)
        pos['giangvien2'] = (2.5, 2)
        pos['admin1'] = (4, 2)
        pos['admin2'] = (5.5, 2)
        
        # VLAN 10 (right side - under s4)
        pos['sinhvien1'] = (9.5, 2)
        pos['sinhvien2'] = (12.5, 2)
        
        # Định nghĩa màu sắc cho các node
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            if node in routers:
                node_colors.append('#FF6B6B')  # Red for router
                node_sizes.append(3000)
            elif node in distribution_switches:
                node_colors.append('#4ECDC4')  # Teal for distribution
                node_sizes.append(2500)
            elif node in access_switches:
                node_colors.append('#45B7D1')  # Blue for access
                node_sizes.append(2500)
            elif node in vlan20_hosts:
                node_colors.append('#96CEB4')  # Green for VLAN 20
                node_sizes.append(2000)
            elif node in vlan10_hosts:
                node_colors.append('#FFEAA7')  # Yellow for VLAN 10
                node_sizes.append(2000)
            elif node in dmz_hosts:
                node_colors.append('#DFE6E9')  # Gray for DMZ
                node_sizes.append(2000)
            elif node in outside_hosts:
                node_colors.append('#FFA07A')  # Light salmon for outside
                node_sizes.append(2000)
        
        # Vẽ các edge với màu và độ dày khác nhau
        edge_colors = []
        edge_widths = []
        
        for edge in G.edges():
            if 'r1' in edge:
                edge_colors.append('#FF6B6B')
                edge_widths.append(3)
            elif 's1' in edge or 's2' in edge:
                edge_colors.append('#4ECDC4')
                edge_widths.append(2.5)
            else:
                edge_colors.append('#95A5A6')
                edge_widths.append(2)
        
        # Vẽ edges
        nx.draw_networkx_edges(G, pos, 
                              edge_color=edge_colors, 
                              width=edge_widths, 
                              alpha=0.6)
        
        # Vẽ nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors, 
                              node_size=node_sizes,
                              alpha=0.9,
                              edgecolors='black',
                              linewidths=2)
        
        # Vẽ labels với font lớn hơn
        labels = {}
        for node in G.nodes():
            if node in routers:
                labels[node] = f'{node}\n(Router)'
            elif node in distribution_switches:
                labels[node] = f'{node}\n(Distribution)'
            elif node in access_switches:
                labels[node] = f'{node}\n(Access)'
            elif node in vlan20_hosts:
                if 'admin' in node:
                    labels[node] = f'{node}\n(VLAN 20\nAdmin)'
                else:
                    labels[node] = f'{node}\n(VLAN 20)'
            elif node in vlan10_hosts:
                labels[node] = f'{node}\n(VLAN 10)'
            elif node in dmz_hosts:
                labels[node] = f'{node}\n(DMZ)'
            elif node in outside_hosts:
                labels[node] = f'{node}\n(Outside)'
        
        nx.draw_networkx_labels(G, pos, labels, 
                               font_size=9, 
                               font_weight='bold',
                               font_family='sans-serif')
        
        # Thêm tiêu đề
        plt.title('Mô Hình Mạng 3 Lớp với DMZ\nCore - Distribution - Access', 
                 fontsize=18, fontweight='bold', pad=20)
        
        # Thêm chú thích (legend)
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#FF6B6B', markersize=12, 
                      label='Router (Core Layer)', markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#4ECDC4', markersize=12, 
                      label='Distribution Switch', markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#45B7D1', markersize=12, 
                      label='Access Switch', markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#96CEB4', markersize=12, 
                      label='VLAN 20 (Giảng viên)', markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#FFEAA7', markersize=12, 
                      label='VLAN 10 (Sinh viên)', markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#DFE6E9', markersize=12, 
                      label='DMZ', markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#FFA07A', markersize=12, 
                      label='Outside (Internet)', markeredgecolor='black', markeredgewidth=2),
        ]
        
        plt.legend(handles=legend_elements, loc='upper left', 
                  fontsize=10, framealpha=0.9, edgecolor='black')
        
        # Thêm thông tin VLAN
        vlan_info = (
            'VLAN Information:\n'
            'VLAN 10: 10.1.1.0/24 (Sinh viên)\n'
            'VLAN 20: 10.1.2.0/24 (Giảng viên)\n'
            'VLAN 99: 172.16.10.0/24 (DMZ)\n'
            'Outside: 203.0.113.0/24'
        )
        plt.text(0.02, 0.02, vlan_info, 
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Tắt trục
        plt.axis('off')
        
        # Tight layout
        plt.tight_layout()
        
        # Lưu file
        plt.savefig(save_path, format='png', dpi=300, bbox_inches='tight')
        info(f'*** Sơ đồ mạng đã được lưu tại: {save_path}\n')
        
        plt.close()
        
        return save_path


class TestMenu:
    """Menu kiểm tra mạng từ cơ bản đến nâng cao"""
    
    def __init__(self, net):
        self.net = net
        
    def run(self):
        """Chạy menu test"""
        while True:
            self.show_menu()
            choice = input("\nChọn chức năng (0-9): ").strip()
            
            if choice == '0':
                print("Thoát menu test.")
                break
            elif choice == '1':
                self.basic_tests()
            elif choice == '2':
                self.vlan_tests()
            elif choice == '3':
                self.routing_tests()
            elif choice == '4':
                self.acl_security_tests()
            elif choice == '5':
                self.acl_privacy_tests()
            elif choice == '6':
                self.acl_management_tests()
            elif choice == '7':
                self.service_tests()
            elif choice == '8':
                self.advanced_tests()
            elif choice == '9':
                self.show_rules()
            else:
                print("Lựa chọn không hợp lệ!")
                
    def show_menu(self):
        """Hiển thị menu"""
        print("\n" + "="*70)
        print(" MENU KIỂM TRA MẠNG ".center(70, "="))
        print("="*70)
        print("  [1] Basic Tests - Kiểm tra kết nối cơ bản")
        print("  [2] VLAN Tests - Kiểm tra cấu hình VLAN")
        print("  [3] Routing Tests - Kiểm tra định tuyến")
        print("  [4] ACL Security Tests - Kiểm tra chính sách bảo mật")
        print("  [5] ACL Privacy Tests - Kiểm tra chính sách riêng tư")
        print("  [6] ACL Management Tests - Kiểm tra chính sách quản trị")
        print("  [7] Service Tests - Kiểm tra dịch vụ (HTTP, SSH)")
        print("  [8] Advanced Tests - Kiểm tra nâng cao")
        print("  [9] Show Rules - Hiển thị iptables rules")
        print("  [0] Exit - Thoát")
        print("="*70)
        
    def basic_tests(self):
        """Kiểm tra kết nối cơ bản"""
        print("\n" + "-"*70)
        print(" BASIC CONNECTIVITY TESTS ".center(70, "-"))
        print("-"*70)
        
        print("\n[Test 1.1] Ping Gateway từ mỗi host\n")
        hosts = ['giangvien1', 'sinhvien1', 'webserver']
        gateways = ['10.1.2.1', '10.1.1.1', '172.16.10.1']
        
        for host, gw in zip(hosts, gateways):
            print(f">>> {host} ping -c 3 {gw}")
            h = self.net.get(host)
            result = h.cmd(f'ping -c 3 {gw}')
            print(result)
            
        print("\n[Test 1.2] Ping giữa các host trong cùng VLAN\n")
        print(">>> giangvien1 (VLAN 20) ping -c 3 giangvien2")
        gv1 = self.net.get('giangvien1')
        result = gv1.cmd('ping -c 3 10.1.2.20')
        print(result)
        
        print(">>> sinhvien1 (VLAN 10) ping -c 3 sinhvien2")
        sv1 = self.net.get('sinhvien1')
        result = sv1.cmd('ping -c 3 10.1.1.20')
        print(result)
        
        print("\n[Test 1.3] Ping Internet từ Inside\n")
        print(">>> giangvien1 ping -c 3 internet (203.0.113.10)")
        result = gv1.cmd('ping -c 3 203.0.113.10')
        print(result)
        
        input("\nNhấn Enter để tiếp tục...")
        
    def vlan_tests(self):
        """Kiểm tra VLAN"""
        print("\n" + "-"*70)
        print(" VLAN ISOLATION TESTS ".center(70, "-"))
        print("-"*70)
        
        sv1 = self.net.get('sinhvien1')
        gv1 = self.net.get('giangvien1')
        
        print("\n[Test 2.1] Kiểm tra cô lập VLAN 10 và VLAN 20 (SHOULD BE BLOCKED)\n")
        print(">>> sinhvien1 (VLAN 10) ping -c 3 -W 2 giangvien1 (10.1.2.10)")
        result = sv1.cmd('ping -c 3 -W 2 10.1.2.10')
        print(result)
            
        print("\n[Test 2.2] Kiểm tra VLAN 10 có thể truy cập DMZ (SHOULD BE ALLOWED)\n")
        print(">>> sinhvien1 (VLAN 10) ping -c 3 webserver (172.16.10.100)")
        result = sv1.cmd('ping -c 3 172.16.10.100')
        print(result)
        
        print("\n[Test 2.3] Kiểm tra VLAN 20 có thể truy cập VLAN 10 (SHOULD BE ALLOWED)\n")
        print(">>> giangvien1 (VLAN 20) ping -c 3 sinhvien1 (10.1.1.10)")
        result = gv1.cmd('ping -c 3 10.1.1.10')
        print(result)
        
        input("\nNhấn Enter để tiếp tục...")
        
    def routing_tests(self):
        """Kiểm tra routing"""
        print("\n" + "-"*70)
        print(" ROUTING TESTS ".center(70, "-"))
        print("-"*70)
        
        print("\n[Test 3.1] Bảng định tuyến của Router")
        r1 = self.net.get('r1')
        result = r1.cmd('ip route show')
        print(result)
        
        print("\n[Test 3.2] Traceroute từ VLAN 10 đến DMZ")
        sv1 = self.net.get('sinhvien1')
        result = sv1.cmd('traceroute -n -m 5 -w 1 172.16.10.100')
        print(result)
        
        print("\n[Test 3.3] Traceroute từ VLAN 20 đến Internet")
        gv1 = self.net.get('giangvien1')
        result = gv1.cmd('traceroute -n -m 5 -w 1 203.0.113.10')
        print(result)
        
        input("\nNhấn Enter để tiếp tục...")
        
    def acl_security_tests(self):
        """Kiểm tra ACL Security Policy"""
        print("\n" + "-"*70)
        print(" ACL SECURITY POLICY TESTS ".center(70, "-"))
        print("-"*70)
        
        internet = self.net.get('internet')
        gv1 = self.net.get('giangvien1')
        
        print("\n[Test 4.1] Internet → DMZ Web Server (port 80) - SHOULD ALLOW\n")
        print(">>> internet curl http://172.16.10.100")
        result = internet.cmd('curl -s -m 3 http://172.16.10.100')
        print(result if result.strip() else "(No response)")
        
        print("\n[Test 4.2] Internet → Inside VLAN 20 - SHOULD BLOCK\n")
        print(">>> internet ping -c 3 -W 2 giangvien1 (10.1.2.10)")
        result = internet.cmd('ping -c 3 -W 2 10.1.2.10')
        print(result)
            
        print("\n[Test 4.3] Internet → Inside VLAN 10 - SHOULD BLOCK\n")
        print(">>> internet ping -c 3 -W 2 sinhvien1 (10.1.1.10)")
        result = internet.cmd('ping -c 3 -W 2 10.1.1.10')
        print(result)
            
        print("\n[Test 4.4] Inside → Internet - SHOULD ALLOW\n")
        print(">>> giangvien1 ping -c 3 internet (203.0.113.10)")
        result = gv1.cmd('ping -c 3 203.0.113.10')
        print(result)
        
        input("\nNhấn Enter để tiếp tục...")
        
    def acl_privacy_tests(self):
        """Kiểm tra ACL Privacy Policy"""
        print("\n" + "-"*70)
        print(" ACL PRIVACY POLICY TESTS ".center(70, "-"))
        print("-"*70)
        
        sv1 = self.net.get('sinhvien1')
        gv1 = self.net.get('giangvien1')
        
        print("\n[Test 5.1] VLAN 10 → VLAN 20 - SHOULD BLOCK\n")
        print(">>> sinhvien1 ping -c 3 -W 2 giangvien1 (10.1.2.10)")
        result = sv1.cmd('ping -c 3 -W 2 10.1.2.10')
        print(result)
            
        print("\n[Test 5.2] VLAN 10 → DMZ - SHOULD ALLOW\n")
        print(">>> sinhvien1 ping -c 3 webserver (172.16.10.100)")
        result = sv1.cmd('ping -c 3 172.16.10.100')
        print(result)
        
        print("\n[Test 5.3] VLAN 10 → DMZ HTTP - SHOULD ALLOW\n")
        print(">>> sinhvien1 curl http://172.16.10.100")
        result = sv1.cmd('curl -s -m 3 http://172.16.10.100')
        print(result if result.strip() else "(No response)")
            
        print("\n[Test 5.4] VLAN 20 → VLAN 10 - SHOULD ALLOW\n")
        print(">>> giangvien1 ping -c 3 sinhvien1 (10.1.1.10)")
        result = gv1.cmd('ping -c 3 10.1.1.10')
        print(result)
        
        input("\nNhấn Enter để tiếp tục...")
        
    def acl_management_tests(self):
        """Kiểm tra ACL Management Policy"""
        print("\n" + "-"*70)
        print(" ACL MANAGEMENT POLICY TESTS ".center(70, "-"))
        print("-"*70)
        
        admin1 = self.net.get('admin1')
        sv1 = self.net.get('sinhvien1')
        gv1 = self.net.get('giangvien1')
        r1 = self.net.get('r1')
        
        # Start SSH server trên router
        print("\nChuẩn bị SSH service trên router...")
        
        # Kiểm tra và start SSH daemon
        r1.cmd('mkdir -p /var/run/sshd')
        r1.cmd('chmod 755 /var/run/sshd')
        
        # Try to start SSH daemon (may not work in Mininet, that's OK)
        r1.cmd('/usr/sbin/sshd -o ListenAddress=0.0.0.0 2>/dev/null &')
        time.sleep(1)
        
        # Fallback: Start a simple TCP listener on port 22 để test ACL
        # (vì SSH thật có thể không hoạt động trong Mininet host)
        print("Starting TCP listener on port 22 for testing...")
        r1.cmd('nc -l -p 22 -k 2>/dev/null &')
        time.sleep(1)
        
        print("Service started.\n")
        
        print("[Test 6.1] SSH từ admin1 (10.1.2.50) - SHOULD ALLOW\n")
        print(">>> admin1 nc -zv -w 2 10.1.2.1 22")
        result = admin1.cmd('nc -zv -w 2 10.1.2.1 22 2>&1')
        print(result if result.strip() else "(Connection attempt)")
        
        # Kiểm tra kết quả
        if "succeeded" in result or "open" in result:
            print("✅ PASS: Connection succeeded (allowed by ACL)")
        elif "refused" in result:
            print("⚠️  Connection refused (ACL allowed, but service issue)")
        else:
            print("❌ FAIL: Connection blocked or timed out")
            
        print("\n[Test 6.2] SSH từ sinhvien1 - SHOULD BLOCK\n")
        print(">>> sinhvien1 nc -zv -w 2 10.1.1.1 22")
        result = sv1.cmd('nc -zv -w 2 10.1.1.1 22 2>&1')
        print(result if result.strip() else "(Connection timeout - blocked by firewall)")
        
        if "timed out" in result or result.strip() == "":
            print("✅ PASS: Connection blocked (as expected)")
        else:
            print("❌ FAIL: Connection should be blocked")
            
        print("\n[Test 6.3] SSH từ giangvien1 (không phải admin) - SHOULD BLOCK\n")
        print(">>> giangvien1 nc -zv -w 2 10.1.2.1 22")
        result = gv1.cmd('nc -zv -w 2 10.1.2.1 22 2>&1')
        print(result if result.strip() else "(Connection timeout - blocked by firewall)")
        
        if "timed out" in result or result.strip() == "":
            print("✅ PASS: Connection blocked (as expected)")
        else:
            print("❌ FAIL: Connection should be blocked")
        
        # Cleanup
        r1.cmd('killall nc 2>/dev/null')
        r1.cmd('killall sshd 2>/dev/null')
            
        input("\nNhấn Enter để tiếp tục...")
        
    def service_tests(self):
        """Kiểm tra các dịch vụ"""
        print("\n" + "-"*70)
        print(" SERVICE TESTS ".center(70, "-"))
        print("-"*70)
        
        sv1 = self.net.get('sinhvien1')
        gv1 = self.net.get('giangvien1')
        internet = self.net.get('internet')
        webserver = self.net.get('webserver')
        
        print("\n[Test 7.1] HTTP Server từ VLAN 10\n")
        print(">>> sinhvien1 curl http://172.16.10.100")
        result = sv1.cmd('curl -s -m 3 http://172.16.10.100')
        print(result if result.strip() else "(No response)")
        
        print("\n[Test 7.2] HTTP Server từ VLAN 20\n")
        print(">>> giangvien1 curl http://172.16.10.100")
        result = gv1.cmd('curl -s -m 3 http://172.16.10.100')
        print(result if result.strip() else "(No response)")
        
        print("\n[Test 7.3] HTTP Server từ Internet (Outside)\n")
        print(">>> internet curl http://172.16.10.100")
        result = internet.cmd('curl -s -m 3 http://172.16.10.100')
        print(result if result.strip() else "(No response)")
        
        print("\n[Test 7.4] Xem nội dung file index.html trên webserver\n")
        print(">>> webserver cat /tmp/index.html")
        result = webserver.cmd('cat /tmp/index.html')
        print(result)
        
        input("\nNhấn Enter để tiếp tục...")
        
    def advanced_tests(self):
        """Kiểm tra nâng cao"""
        print("\n" + "-"*70)
        print(" ADVANCED TESTS ".center(70, "-"))
        print("-"*70)
        
        print("\n[Test 8.1] Latency Test (RTT)")
        sv1 = self.net.get('sinhvien1')
        print("  sinhvien1 → webserver")
        result = sv1.cmd('ping -c 5 172.16.10.100 | tail -1')
        print(f"  {result}")
        
        print("\n[Test 8.2] Bandwidth Test với iperf (cần iperf)")
        print("  Checking if iperf is available...")
        webserver = self.net.get('webserver')
        check = webserver.cmd('which iperf 2>/dev/null')
        if check.strip():
            print("  Starting iperf server on webserver...")
            webserver.cmd('iperf -s &')
            time.sleep(1)
            print("  Running iperf client from sinhvien1...")
            result = sv1.cmd('iperf -c 172.16.10.100 -t 3')
            print(result[-200:])
            webserver.cmd('killall iperf')
        else:
            print("  iperf not installed - skipping bandwidth test")
            
        print("\n[Test 8.3] Concurrent Connections Test")
        print("  Testing multiple simultaneous pings...")
        sv1 = self.net.get('sinhvien1')
        gv1 = self.net.get('giangvien1')
        
        import subprocess
        import threading
        
        results = []
        
        def ping_test(host, target, results_list):
            h = self.net.get(host)
            result = h.cmd(f'ping -c 3 -W 1 {target}')
            success = "1 received" in result or "2 received" in result or "3 received" in result
            results_list.append((host, target, success))
            
        threads = []
        t1 = threading.Thread(target=ping_test, args=('sinhvien1', '172.16.10.100', results))
        t2 = threading.Thread(target=ping_test, args=('giangvien1', '172.16.10.100', results))
        threads.extend([t1, t2])
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        for host, target, success in results:
            status = "✓" if success else "✗"
            print(f"  {status} {host} → {target}")
            
        input("\nNhấn Enter để tiếp tục...")
        
    def show_rules(self):
        """Hiển thị iptables rules"""
        print("\n" + "-"*70)
        print(" IPTABLES RULES ".center(70, "-"))
        print("-"*70)
        
        r1 = self.net.get('r1')
        
        print("\n[Filter Table - FORWARD Chain]")
        result = r1.cmd('iptables -L FORWARD -v -n --line-numbers')
        print(result)
        
        print("\n[Filter Table - INPUT Chain]")
        result = r1.cmd('iptables -L INPUT -v -n --line-numbers')
        print(result)
        
        print("\n[Router Interfaces]")
        result = r1.cmd('ip addr show')
        print(result)
        
        input("\nNhấn Enter để tiếp tục...")


class CustomCLI(CLI):
    """Custom Mininet CLI với lệnh test và diagram"""
    
    def __init__(self, mininet, test_menu, topology, **kwargs):
        self.test_menu = test_menu
        self.topology = topology
        CLI.__init__(self, mininet, **kwargs)
    
    def do_test(self, line):
        """Chạy menu test: test"""
        print("\n" + "="*70)
        print(" QUAY TRỞ LẠI MENU TEST ".center(70, "="))
        print("="*70)
        self.test_menu.run()
    
    def do_diagram(self, line):
        """Vẽ và hiển thị sơ đồ mạng: diagram [filename]"""
        filename = line.strip() if line.strip() else 'network_topology.png'
        print(f"\n*** Đang vẽ sơ đồ mạng...")
        path = self.topology.visualize_topology(save_path=filename)
        print(f"*** Sơ đồ đã được lưu tại: {path}")
        print(f"*** Mở file bằng lệnh: xdg-open {path}  (hoặc dùng trình xem ảnh)\n")


def main():
    """Main function"""
    setLogLevel('info')
    
    # Tạo network topology
    topology = NetworkTopology()
    
    # Cleanup trước khi chạy
    topology.cleanup_mininet()
    
    # Tạo và build mạng
    topology.create_topology()
    topology.build_network()
    
    # Hiển thị cấu hình
    topology.show_configuration()
    
    # Vẽ sơ đồ mạng
    print("\n" + "="*70)
    print(" VẼ SƠ ĐỒ MẠNG ".center(70, "="))
    print("="*70)
    diagram_path = topology.visualize_topology(save_path='network_topology.png')
    print(f"Sơ đồ mạng đã được lưu tại: {diagram_path}")
    print("Bạn có thể xem file này bằng trình xem ảnh.")
    
    # Chạy menu test
    print("\n" + "="*70)
    print(" CHÀO MỪNG ĐẾN VỚI HỆ THỐNG KIỂM TRA MẠNG ".center(70))
    print("="*70)
    
    choice = input("\nBạn muốn chạy menu test ngay? (y/n): ").strip().lower()
    
    test_menu = TestMenu(topology.net)
    
    if choice == 'y':
        test_menu.run()
    
    # Mở Mininet CLI với custom commands
    print("\n" + "="*70)
    print("*** Mở Mininet CLI (gõ 'exit' để thoát)")
    print("="*70)
    print("*** Lệnh hữu ích:")
    print("    - test: Quay lại menu kiểm tra")
    print("    - diagram [filename]: Vẽ lại sơ đồ mạng")
    print("    - pingall: Ping tất cả hosts")
    print("    - r1 iptables -L -v: Xem ACL rules")
    print("    - xterm <host>: Mở terminal của host")
    print("    - help: Xem tất cả lệnh")
    print("="*70 + "\n")
    
    # Sử dụng Custom CLI
    CustomCLI(topology.net, test_menu, topology)
    
    # Cleanup
    print("\n*** Đang dọn dẹp...")
    topology.net.stop()


if __name__ == '__main__':
    main()
