#!/usr/bin/env python3
"""
MÔ HÌNH BÀI TẬP: BORDER-SPINE-LEAF PURE IPV6 INTERNAL + NAT64 TAYGA
- Theo cấu trúc logic_network.png mới
- Toàn bộ thiết bị nội bộ (s1-s7, r1, web, dns, db) chạy IPv6.
- Định tuyến động OSPFv3 (ospf6d).
- r1 chạy Tayga NAT64 chuyển IP nguồn IPv6 -> IPv4 Public.
"""
import os
import sys
import time

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class TechVerseCLI(CLI):
    def default(self, line):
        first, args, text = self.parseline(line)
        # Hỗ trợ ping ngược từ ngoài (IPv4) vào mạng IPv6 (NAT64 tĩnh)
        if hasattr(self, 'mn') and first in self.mn and args and args.strip().startswith('ping '):
            node = self.mn[first]
            if first in ['internet', 'serverhcm']:
                args = args.replace('web_server1', '192.168.255.11')
                args = args.replace('web_server2', '192.168.255.12')
                args = args.replace('dns_server1', '192.168.255.21')
                args = args.replace('dns_server2', '192.168.255.22')
                args = args.replace('db_server1', '192.168.255.31')
                args = args.replace('db_server2', '192.168.255.32')
            node.sendCmd(args)
            self.waitForNode(node)
            return

        # Bắt lệnh ping6 để không cho Mininet tự thay đổi Hostname thành IPv4 trước khi Bash chạy
        if hasattr(self, 'mn') and first in self.mn and args and args.strip().startswith('ping6 '):
            node = self.mn[first]
            node.sendCmd(args)
            self.waitForNode(node)
            return
        super(TechVerseCLI, self).default(line)

    def do_acl(self, line):
        """Zero Trust IPv6 Micro-segmentation. Call: acl"""
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'microsegment.sh')
        os.system(f'chmod +x {script} && bash {script}')
        
    def do_failtest(self, line):
        """Kịch bản Tự động Cắt cáp thử Failover Spine. Call: failtest"""
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'failover_test.sh')
        os.system(f'chmod +x {script} && bash {script}')

    def do_dropacl(self, line):
        """Gỡ bỏ toàn bộ Zero Trust Firewall (ip6tables). Call: dropacl"""
        for node in ['web_server1', 'dns_server1', 'db_server1', 's3', 's4', 's5']:
            os.system(f"ip netns exec {node} ip6tables -F INPUT 2>/dev/null")
            os.system(f"ip netns exec {node} ip6tables -F FORWARD 2>/dev/null")
        print("Đã xóa hoàn toàn vách ngăn Micro-segmentation! (Cho phép Ping chéo thả ga)")
        
    def do_dropnat(self, line):
        """Hủy bộ NAT64 và IPv4 Masquerade trên R1. Call: dropnat"""
        os.system("ip netns exec r1 iptables -t nat -F POSTROUTING 2>/dev/null")
        os.system("ip netns exec r1 killall -9 tayga 2>/dev/null")
        os.system("ip netns exec r1 ip link del nat64 2>/dev/null")
        print("Đã đánh sập Hầm NAT64 và Tường lửa SNAT! (Các máy chủ đã bị chặt đứt đường ra Internet)")

    def do_acl_status(self, line):
        """Xem rule ip6tables. Call: acl_status"""
        for node in ['web_server1', 'dns_server1', 'db_server1', 's3', 's4', 's5']:
            print(f'\n=== {node.upper()} ===')
            print(self.mn[node].cmd('ip6tables -nvL'))
            
    def do_nat(self, line):
        """Khởi động Tayga NAT64 trên r1. Call: nat"""
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nat_setup.sh')
        os.system(f'chmod +x {script} && bash {script}')

class FRRouter(Node):
    def config(self, **params):
        super(FRRouter, self).config(**params)
        # Enable IPv4, IPv6 forwarding and multipath hashing for ECMP
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')
        self.cmd('sysctl -w net.ipv4.fib_multipath_hash_policy=1')
        # Fast initialization IPv6
        self.cmd('sysctl -w net.ipv6.conf.all.accept_dad=0')

        confDir = f'/tmp/{self.name}'
        self.cmd(f'rm -rf {confDir} && mkdir -p {confDir}')
        self.cmd(f'chmod 777 {confDir}')

        base_conf = (
            f"hostname {self.name}\n"
            "log stdout\n"
            "service advanced-vty\n"
            "!\n"
            "line vty\n"
            " no login\n"
            "!\n"
        )
        with open(f'{confDir}/zebra.conf', 'w') as f: f.write(base_conf)
        with open(f'{confDir}/ospf6d.conf', 'w') as f: f.write(base_conf)
        self.cmd(f'chown -R frr:frr {confDir}')
        self.cmd(f'/usr/lib/frr/zebra -d -u frr -g frr -A 127.0.0.1 -f {confDir}/zebra.conf -i {confDir}/zebra.pid')
        self.cmd(f'/usr/lib/frr/ospf6d -d -u frr -g frr -A 127.0.0.1 -f {confDir}/ospf6d.conf -i {confDir}/ospf6d.pid')

    def terminate(self):
        self.cmd(f'kill `cat /tmp/{self.name}/ospf6d.pid` 2> /dev/null')
        self.cmd(f'kill `cat /tmp/{self.name}/zebra.pid` 2> /dev/null')
        super(FRRouter, self).terminate()

class LogicNetworkTopo(Topo):
    def build(self):
        s1 = self.addHost('s1', cls=FRRouter, ip='1.1.1.1/32')
        s2 = self.addHost('s2', cls=FRRouter, ip='2.2.2.2/32')
        s3 = self.addHost('s3', cls=FRRouter, ip='3.3.3.3/32')
        s4 = self.addHost('s4', cls=FRRouter, ip='4.4.4.4/32')
        s5 = self.addHost('s5', cls=FRRouter, ip='5.5.5.5/32')
        s7 = self.addHost('s7', cls=FRRouter, ip='7.7.7.7/32')
        r1 = self.addHost('r1', cls=FRRouter, ip='100.100.100.100/32')

        # IPv6 Hosts (Gán IP thủ công xuống config để tránh lỗi parse của Mininet)
        web_server1 = self.addHost('web_server1', ip=None)
        web_server2 = self.addHost('web_server2', ip=None)
        dns_server1 = self.addHost('dns_server1', ip=None)
        dns_server2 = self.addHost('dns_server2', ip=None)
        db_server1 = self.addHost('db_server1', ip=None)
        db_server2 = self.addHost('db_server2', ip=None)
        
        # IPv4 External Hosts
        serverhcm = self.addHost('serverhcm', ip='203.162.1.1/24', defaultRoute='via 203.162.1.254')
        internet = self.addHost('internet', ip='8.8.8.8/24', defaultRoute='via 8.8.8.254')

        # Link s7 to Spines & Router
        self.addLink(s7, s1, intfName1='s7-eth0', intfName2='s1-eth0')
        self.addLink(s7, s2, intfName1='s7-eth1', intfName2='s2-eth0')
        self.addLink(s7, r1, intfName1='s7-eth2', intfName2='r1-eth0')
        
        # Link Spine to Leaf
        self.addLink(s1, s3, intfName1='s1-eth1', intfName2='s3-eth0')
        self.addLink(s1, s4, intfName1='s1-eth2', intfName2='s4-eth0')
        self.addLink(s1, s5, intfName1='s1-eth3', intfName2='s5-eth0')
        
        self.addLink(s2, s3, intfName1='s2-eth1', intfName2='s3-eth1')
        self.addLink(s2, s4, intfName1='s2-eth2', intfName2='s4-eth1')
        self.addLink(s2, s5, intfName1='s2-eth3', intfName2='s5-eth1')
        
        # Link Leaf to Hosts
        self.addLink(s3, web_server1, intfName1='s3-eth2', intfName2='web-eth0')
        self.addLink(s3, web_server2, intfName1='s3-eth3', intfName2='web-eth1')
        self.addLink(s4, dns_server1, intfName1='s4-eth2', intfName2='dns-eth0')
        self.addLink(s4, dns_server2, intfName1='s4-eth3', intfName2='dns-eth1')
        self.addLink(s5, db_server1, intfName1='s5-eth2', intfName2='db-eth0')
        self.addLink(s5, db_server2, intfName1='s5-eth3', intfName2='db-eth1')
        
        # External IPv4 Links
        self.addLink(r1, serverhcm, intfName1='r1-eth1', intfName2='serverhcm-eth0')
        self.addLink(r1, internet, intfName1='r1-eth2', intfName2='internet-eth0')

def configure_network(net):
    info('*** Liên kết Network Namespace...\n')
    os.system('mkdir -p /var/run/netns')
    for name_str, n in net.nameToNode.items():
        if hasattr(n, 'pid'):
            pid = getattr(n, 'pid')
            os.system(f'ln -sf /proc/{pid}/ns/net /var/run/netns/{name_str}')

    info('*** Gán IPv6 cho Internal Network...\n')
    routers = ['s1', 's2', 's3', 's4', 's5', 's7', 'r1']
    for r in routers:
        node = net[r]
        node.cmd("ip -6 addr add fc00:1111::%s/128 dev lo" % (r.replace('s', '').replace('r', '9')))
        
    s1, s2, s3, s4, s5, s7, r1 = [net[x] for x in routers]
    
    # Core links P2P
    s7.cmd('ip -6 addr add fc00:3::1/126 dev s7-eth0'); s1.cmd('ip -6 addr add fc00:3::2/126 dev s1-eth0')
    s7.cmd('ip -6 addr add fc00:3::5/126 dev s7-eth1'); s2.cmd('ip -6 addr add fc00:3::6/126 dev s2-eth0')
    s7.cmd('ip -6 addr add fc00:3::9/126 dev s7-eth2'); r1.cmd('ip -6 addr add fc00:3::10/126 dev r1-eth0')
    
    # s1 - leaf
    s1.cmd('ip -6 addr add fc00:1::1/126 dev s1-eth1'); s3.cmd('ip -6 addr add fc00:1::2/126 dev s3-eth0')
    s1.cmd('ip -6 addr add fc00:1::5/126 dev s1-eth2'); s4.cmd('ip -6 addr add fc00:1::6/126 dev s4-eth0')
    s1.cmd('ip -6 addr add fc00:1::9/126 dev s1-eth3'); s5.cmd('ip -6 addr add fc00:1::10/126 dev s5-eth0')
    
    # s2 - leaf
    s2.cmd('ip -6 addr add fc00:2::1/126 dev s2-eth1'); s3.cmd('ip -6 addr add fc00:2::2/126 dev s3-eth1')
    s2.cmd('ip -6 addr add fc00:2::5/126 dev s2-eth2'); s4.cmd('ip -6 addr add fc00:2::6/126 dev s4-eth1')
    s2.cmd('ip -6 addr add fc00:2::9/126 dev s2-eth3'); s5.cmd('ip -6 addr add fc00:2::10/126 dev s5-eth1')
    
    # Gateways Local
    s3.cmd('ip -6 addr add fd00:10::254/64 dev s3-eth2; ip -6 addr add fd00:10::254/64 dev s3-eth3')
    s4.cmd('ip -6 addr add fd00:20::254/64 dev s4-eth2; ip -6 addr add fd00:20::254/64 dev s4-eth3')
    s5.cmd('ip -6 addr add fd00:30::254/64 dev s5-eth2; ip -6 addr add fd00:30::254/64 dev s5-eth3')
    
    # Host Client IPv6 setup
    net['web_server1'].cmd('ip -6 addr add fd00:10::1/64 dev web-eth0; ip -6 route add default via fd00:10::254')
    net['web_server2'].cmd('ip -6 addr add fd00:10::2/64 dev web-eth1; ip -6 route add default via fd00:10::254')
    net['dns_server1'].cmd('ip -6 addr add fd00:20::1/64 dev dns-eth0; ip -6 route add default via fd00:20::254')
    net['dns_server2'].cmd('ip -6 addr add fd00:20::2/64 dev dns-eth1; ip -6 route add default via fd00:20::254')
    net['db_server1'].cmd('ip -6 addr add fd00:30::1/64 dev db-eth0; ip -6 route add default via fd00:30::254')
    net['db_server2'].cmd('ip -6 addr add fd00:30::2/64 dev db-eth1; ip -6 route add default via fd00:30::254')

    # Bridge the dual interfaces for /64 subnet on Leaf
    for leaf, net_ip, eth2, eth3 in [(s3, 'fd00:10::254/64', 's3-eth2', 's3-eth3'),
                                     (s4, 'fd00:20::254/64', 's4-eth2', 's4-eth3'),
                                     (s5, 'fd00:30::254/64', 's5-eth2', 's5-eth3')]:
        leaf.cmd('ip link add name br0 type bridge')
        leaf.cmd('ip link set br0 up')
        leaf.cmd(f'ip link set {eth2} master br0')
        leaf.cmd(f'ip link set {eth3} master br0')
        leaf.cmd(f'ip -6 addr add {net_ip} dev br0')
        leaf.cmd(f'ip -6 addr flush dev {eth2}')
        leaf.cmd(f'ip -6 addr flush dev {eth3}')
        
    # r1 Public WAN IPv4
    r1.cmd('ifconfig r1-eth1 203.162.1.254/24')
    r1.cmd('ifconfig r1-eth2 8.8.8.254/24')
    net['serverhcm'].cmd('ip route add 192.168.255.0/24 via 203.162.1.254')
    net['internet'].cmd('ip route add 192.168.255.0/24 via 8.8.8.254')
    
    info('*** Kích hoạt NAT64 Tayga trên r1...\n')
    os.system('bash source/nat_setup.sh 2>/dev/null')
    
    time.sleep(2)
    
    info('*** Cấu hình OSPFv3 (ospf6d) cho IPv6...\n')
    def config_ospf6_via_tcp(node, rid, infts, r_extra=""):
        cmds = f"enable\nconf t\nrouter ospf6\nospf6 router-id {rid}\nexit\n"
        for i in infts:
            cmds += f"interface {i}\nipv6 ospf6 area 0\nexit\n"
        if r_extra:
            cmds += f"router ospf6\n{r_extra}\nexit\n"
        cmds += "end\nwr\nexit\n"
        node.cmd(f'echo -e "{cmds}" | nc -w 1 127.0.0.1 2606 | tr -cd \'\\11\\12\\15\\40-\\176\'')

    config_ospf6_via_tcp(s7, '7.7.7.7', ['s7-eth0', 's7-eth1', 's7-eth2', 'lo'])
    config_ospf6_via_tcp(s1, '1.1.1.1', ['s1-eth0', 's1-eth1', 's1-eth2', 's1-eth3', 'lo'])
    config_ospf6_via_tcp(s2, '2.2.2.2', ['s2-eth0', 's2-eth1', 's2-eth2', 's2-eth3', 'lo'])
    
    config_ospf6_via_tcp(s3, '3.3.3.3', ['s3-eth0', 's3-eth1', 'br0', 'lo'])
    config_ospf6_via_tcp(s4, '4.4.4.4', ['s4-eth0', 's4-eth1', 'br0', 'lo'])
    config_ospf6_via_tcp(s5, '5.5.5.5', ['s5-eth0', 's5-eth1', 'br0', 'lo'])
    
    # r1 tiêm default route hoặc NAT64 prefix (64:ff9b::/96)
    # Cấu hình Chuẩn Data Center: r1 PHÁT một luồng Default Route (::/0) vĩnh viễn xuống Spine-Leaf,
    # đảm bảo 100% các Server nội bộ luôn biết ném gói tin External/NAT64 lên Gateway r1 mà không bao giờ báo "No route".
    config_ospf6_via_tcp(r1, '100.100.100.100', ['r1-eth0', 'lo'], "redistribute static\nredistribute kernel\ndefault-information originate always")

    info('*** OSPFv3 đang hội tụ (Tạm đợi 15s)...\n')
    time.sleep(15)
    
    info('*** Thiết lập Overlay VXLAN (VNI 100) dựa trên Loopback IPv6...\n')
    # Leaf s3, s4, s5 đóng vai trò VTEP
    for leaf, ip, v6_lo in [('s3', '192.168.100.3/24', 'fc00:1111::3'), 
                            ('s4', '192.168.100.4/24', 'fc00:1111::4'), 
                            ('s5', '192.168.100.5/24', 'fc00:1111::5')]:
        node = net[leaf]
        node.cmd(f'ip -6 link add vxlan100 type vxlan id 100 dstport 4789 local {v6_lo}')
        node.cmd('ip link set vxlan100 up')
        node.cmd(f'ip addr add {ip} dev vxlan100')

    # FDB Entries (Multi-point VXLAN Mesh)
    s3.cmd('bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst fc00:1111::4')
    s3.cmd('bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst fc00:1111::5')
    
    s4.cmd('bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst fc00:1111::3')
    s4.cmd('bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst fc00:1111::5')

    s5.cmd('bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst fc00:1111::3')
    s5.cmd('bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst fc00:1111::4')
    
    info('*** Cấu hình DNS ảo phân giải Name cho Lệnh Ping...\n')
    hosts_entries = (
        "\n# MININET-DNS-MAPPING-START\n"
        "fd00:10::1 web_server1\n"
        "fd00:10::2 web_server2\n"
        "fd00:20::1 dns_server1\n"
        "fd00:20::2 dns_server2\n"
        "fd00:30::1 db_server1\n"
        "fd00:30::2 db_server2\n"
        "64:ff9b::203.162.1.1 serverhcm\n"
        "64:ff9b::808:808 internet\n"
        "# MININET-DNS-MAPPING-END\n"
    )
    os.system("sed -i '/# MININET-DNS-MAPPING-START/,/# MININET-DNS-MAPPING-END/d' /etc/hosts")
    with open('/etc/hosts', 'a') as f:
        f.write(hosts_entries)

def mn_cleanup():
    info('*** Dọn rác Mininet...\n')
    os.system('rm -rf /var/run/netns/web* /var/run/netns/dns* /var/run/netns/db* 2>/dev/null')
    os.system("sed -i '/# MININET-DNS-MAPPING-START/,/# MININET-DNS-MAPPING-END/d' /etc/hosts 2>/dev/null")
    os.system('sudo mn -c 2>/dev/null')
    os.system('sudo killall -9 zebra ospf6d tayga 2>/dev/null')

def run():
    topo = LogicNetworkTopo()
    # Không dùng Controller vì chúng ta dùng OSPFv3 Distributed Routing
    net = Mininet(topo=topo, controller=None)
    net.start()
    configure_network(net)
    
    info('    mininet> web_server1 ping6 dns_server1  (Native IPv6 East-West)\n')
    info('    mininet> web_server1 ping 203.162.1.1   (NAT64 to IPv4 serverhcm)\n')
    info('    mininet> acl                            (Micro-seg IPv6 Firewall)\n')
    
    TechVerseCLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if '--clean' in sys.argv or '-c' in sys.argv:
        mn_cleanup()
        sys.exit(0)
    
    if os.geteuid() != 0:
        print('Phải chạy sudo: sudo python3 topology.py')
        sys.exit(1)
        
    mn_cleanup()
    run()
