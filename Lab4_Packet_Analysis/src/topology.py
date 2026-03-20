#!/usr/bin/python3
"""
Lab4 Packet Analysis - Network Topology
=======================================
OSPF Multi-Area + Extended ACLs + DMZ + Wireshark Integration

Usage:
  sudo python3 topology.py
"""

import os
import sys
import time

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class FRRouter(Node):
    def config(self, **params):
        super(FRRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

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
        with open(f'{confDir}/ospfd.conf', 'w') as f: f.write(base_conf)

        self.cmd(f'chown -R frr:frr {confDir}')

        self.cmd(f'/usr/lib/frr/zebra -d -u frr -g frr -A 127.0.0.1 -f {confDir}/zebra.conf -i {confDir}/zebra.pid -z {confDir}/zserv.api --vty_socket {confDir}')
        self.cmd(f'/usr/lib/frr/ospfd -d -u frr -g frr -A 127.0.0.1 -f {confDir}/ospfd.conf -i {confDir}/ospfd.pid -z {confDir}/zserv.api --vty_socket {confDir}')

    def terminate(self):
        self.cmd(f'kill `cat /tmp/{self.name}/ospfd.pid` 2> /dev/null')
        self.cmd(f'kill `cat /tmp/{self.name}/zebra.pid` 2> /dev/null')
        super(FRRouter, self).terminate()

class Lab4Topo(Topo):
    def build(self):
        # Tạo 5 Router chạy nền tảng FRRouting để giả lập tính năng OSPF của Cisco.
        r1 = self.addNode('r1', cls=FRRouter)
        r2 = self.addNode('r2', cls=FRRouter)
        r3 = self.addNode('r3', cls=FRRouter)
        r4 = self.addNode('r4', cls=FRRouter)
        r5 = self.addNode('r5', cls=FRRouter)

        # Tạo các máy trạm (PC/Sever)
        staff_pc = self.addHost('staff_pc', ip='192.168.10.10/24', defaultRoute='via 192.168.10.1')
        mgmt_pc = self.addHost('mgmt_pc', ip='192.168.20.10/24', defaultRoute='via 192.168.20.1')
        web_srv = self.addHost('web_srv', ip='172.16.10.100/24', defaultRoute='via 172.16.10.1')
        mail_srv = self.addHost('mail_srv', ip='172.16.10.200/24', defaultRoute='via 172.16.10.1')
        br_pc = self.addHost('br_pc', ip='192.168.30.10/24', defaultRoute='via 192.168.30.1')

        # Tạo các Switch (L2) để gom nhóm các ban bệ
        s1 = self.addSwitch('s1') # Switch mạng Staff (Area 10)
        s2 = self.addSwitch('s2') # Switch mạng Mgmt (Area 10)
        s3 = self.addSwitch('s3') # Switch mạng DMZ (Area 20)
        s4 = self.addSwitch('s4') # Switch mạng Branch (Area 30)

        # KẾT NỐI (LINK TRUNG TÂM / BACKBONE P2P /30)
        self.addLink(r1, r3) # r1-eth0 <-> r3-eth0 (Area 0 : 10.0.13.x/30)
        self.addLink(r1, r4) # r1-eth1 <-> r4-eth0 (Area 10: 10.0.14.x/30)
        self.addLink(r1, r2) # r1-eth2 <-> r2-eth0 (Area 20: 10.0.12.x/30)
        self.addLink(r3, r5) # r3-eth1 <-> r5-eth0 (Area 0 -> 30: 10.0.35.x/30)

        # KẾT NỐI NỘI BỘ (TỪ ROUTER XUỐNG SWITCH)
        self.addLink(r4, s1) # r4-eth1 -> Staff
        self.addLink(r4, s2) # r4-eth2 -> Mgmt
        self.addLink(r2, s3) # r2-eth1 -> DMZ
        self.addLink(r5, s4) # r5-eth1 -> Branch
        
        # CẮM MÁY TRẠM VÀO SWITCH
        self.addLink(staff_pc, s1)
        self.addLink(mgmt_pc, s2)
        self.addLink(web_srv, s3)
        self.addLink(mail_srv, s3)
        self.addLink(br_pc, s4)

def mn_cleanup():
    info('*** Cleaning up Mininet...\n')
    os.system('sudo mn -c 2>/dev/null')
    os.system('sudo killall -9 zebra ospfd tcpdump 2>/dev/null')
    os.system('sudo rm -rf /tmp/r* 2>/dev/null')
    os.system('sudo rm -rf /var/run/netns/* 2>/dev/null')
    info('*** Cleanup done.\n')

def apply_acls(net):
    """
    Hàm kích hoạt Tường lửa (Firewall ACL) để mô phỏng bảo mật theo yêu cầu lab.
    Chỉ dùng lệnh này khi đến pha kiểm tra bảo mật (Phase D) để không chặn bắt OSPF cơ bản ban đầu.
    """
    info('*** Configuring iptables ACLs... \n')
    r2, r4 = net['r2'], net['r4']
    
    # ------------------ KHU VỰC R2 (Cửa ngõ DMZ) ------------------
    # CHÍNH SÁCH 1: Chặn đứng mọi liên lạc chủ động bắt nguồn (NEW) từ DMZ đi xuống khu Inside (Mgmt/Staff)
    # Tuy nhiên vẫn cho phép (ACCEPT) truy cập nếu Inside khởi xướng kết nối trước (RELATED, ESTABLISHED).
    r2.cmd('iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT')
    r2.cmd('iptables -A FORWARD -s 172.16.10.0/24 -d 192.168.10.0/24 -m state --state NEW -j DROP')
    r2.cmd('iptables -A FORWARD -s 172.16.10.0/24 -d 192.168.20.0/24 -m state --state NEW -j DROP')
    
    # ------------------ KHU VỰC R4 (Cửa ngõ Inside) ------------------
    # CHÍNH SÁCH 2: Nhân viên từ Inside truy cập DMZ CHỈ được xài Web (Port 80/443) và DNS (Port 53).
    # Mọi gói tin ICMP (Ping) hoặc dịch vụ rác đều bị bóp nghẹt tại cổng của R4 nhằm tránh việc hack DMZ.
    r4.cmd('iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT')
    r4.cmd('iptables -A FORWARD -d 172.16.10.0/24 -p tcp -m multiport ! --dports 80,443 -j DROP')
    r4.cmd('iptables -A FORWARD -d 172.16.10.0/24 -p udp -m multiport ! --dports 53 -j DROP')
    r4.cmd('iptables -A FORWARD -d 172.16.10.0/24 -p icmp -j DROP')
    info('*** ACLs successfully applied!\n')

def generate_pcaps(net):
    r1, r2, r3, r4, r5 = net['r1'], net['r2'], net['r3'], net['r4'], net['r5']
    staff_pc, mgmt_pc = net['staff_pc'], net['mgmt_pc']
    web_srv, br_pc = net['web_srv'], net['br_pc']
    
    captures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../captures')
    os.system(f'mkdir -p {captures_dir}')
    
    info('*** Generating ospf_convergence.pcap\n')
    r1.cmd(f'tcpdump -U -i r1-eth1 -w {captures_dir}/ospf_convergence.pcap >/dev/null 2>&1 &')
    r1.cmd('ip link set r1-eth1 down')
    time.sleep(2)
    r1.cmd('ip link set r1-eth1 up')
    time.sleep(15)
    r1.cmd('killall tcpdump; sleep 1')
    
    info('*** Generating packet_flow_A.pcap (Staff->DMZ)\n')
    r4.cmd(f'tcpdump -U -i r4-eth1 -w {captures_dir}/flow_A_1.pcap >/dev/null 2>&1 &')
    r1.cmd(f'tcpdump -U -i r1-eth1 -w {captures_dir}/flow_A_2.pcap >/dev/null 2>&1 &')
    r1.cmd(f'tcpdump -U -i r1-eth2 -w {captures_dir}/flow_A_3.pcap >/dev/null 2>&1 &')
    r2.cmd(f'tcpdump -U -i r2-eth1 -w {captures_dir}/flow_A_4.pcap >/dev/null 2>&1 &')
    time.sleep(1)
    # staff_pc pings web_srv, but icmp is dropped by ACL on r4
    # let's ping so we see it dropped, AND do a TCP to see it pass
    staff_pc.cmd('ping -c 2 172.16.10.100')
    staff_pc.cmd('nc -zvw 1 172.16.10.100 80')
    time.sleep(1)
    os.system('sudo killall tcpdump; sleep 1')
    os.system(f'mergecap -w {captures_dir}/packet_flow_A.pcap {captures_dir}/flow_A_*.pcap 2>/dev/null || echo "mergecap failed"')
    os.system(f'rm -f {captures_dir}/flow_A_*.pcap')
    
    info('*** Generating packet_flow_B.pcap (Branch->Inside)\n')
    r5.cmd(f'tcpdump -U -i r5-eth1 -w {captures_dir}/flow_B_1.pcap >/dev/null 2>&1 &')
    r3.cmd(f'tcpdump -U -i r3-eth1 -w {captures_dir}/flow_B_2.pcap >/dev/null 2>&1 &')
    r1.cmd(f'tcpdump -U -i r1-eth0 -w {captures_dir}/flow_B_3.pcap >/dev/null 2>&1 &')
    r4.cmd(f'tcpdump -U -i r4-eth2 -w {captures_dir}/flow_B_4.pcap >/dev/null 2>&1 &')
    time.sleep(1)
    br_pc.cmd('ping -c 2 192.168.20.10')
    time.sleep(1)
    os.system('sudo killall tcpdump; sleep 1')
    os.system(f'mergecap -w {captures_dir}/packet_flow_B.pcap {captures_dir}/flow_B_*.pcap 2>/dev/null')
    os.system(f'rm -f {captures_dir}/flow_B_*.pcap')

    apply_acls(net)

    info('*** Generating acl_block.pcap (DMZ -> Inside)\n')
    r2.cmd(f'tcpdump -U -i r2-eth1 -w {captures_dir}/acl_in.pcap >/dev/null 2>&1 &')
    r2.cmd(f'tcpdump -U -i r2-eth0 -w {captures_dir}/acl_out.pcap >/dev/null 2>&1 &')
    time.sleep(1)
    web_srv.cmd('ping -c 2 192.168.20.10')
    time.sleep(1)
    os.system('sudo killall tcpdump; sleep 1')
    os.system(f'mergecap -w {captures_dir}/acl_block.pcap {captures_dir}/acl_*.pcap 2>/dev/null')
    os.system(f'rm -f {captures_dir}/acl_in.pcap {captures_dir}/acl_out.pcap')
    
    info('*** Generating acl_allow.pcap (Inside -> DMZ TCP HTTP)\n')
    r2.cmd(f'tcpdump -U -i r2-eth1 -w {captures_dir}/acl_allow.pcap >/dev/null 2>&1 &')
    web_srv.cmd('python3 -m http.server 80 & echo $! > /tmp/web.pid')
    time.sleep(1)
    staff_pc.cmd('curl http://172.16.10.100 -m 2')
    time.sleep(1)
    web_srv.cmd('kill -9 `cat /tmp/web.pid`')
    os.system('sudo killall tcpdump; sleep 1')
    
    info('*** Generating failover.pcap\n')
    r1.cmd(f'tcpdump -U -i any -w {captures_dir}/failover.pcap >/dev/null 2>&1 &')
    time.sleep(1)
    br_pc.cmd('ping 192.168.10.10 > /tmp/ping.log & echo $! > /tmp/ping.pid')
    time.sleep(2)
    info('    Link down R1-R3...\n')
    r1.cmd('ip link set r1-eth0 down')
    time.sleep(40) # 40s wait for dead interval (4*10s)
    info('    Link up R1-R3...\n')
    r1.cmd('ip link set r1-eth0 up')
    time.sleep(10)
    br_pc.cmd('kill -9 `cat /tmp/ping.pid`')
    os.system('sudo killall tcpdump; sleep 1')
    
    info('*** All PCAPs generated to captures/ directory.\n')

class CustomCLI(CLI):
    def do_acl(self, line):
        """Apply ACLs dynamically. Usage: acl"""
        apply_acls(self.mn)

    def do_gterm(self, line):
        """Open gnome-terminal natively for a node. Usage: gterm r1"""
        args = line.split()
        if not args:
            print("Usage: gterm <node>")
            return
        node_name = args[0]
        if node_name not in self.mn:
            print(f"Node {node_name} not found.")
            return
            
        user = os.environ.get('SUDO_USER', os.environ.get('USER'))
        uid = os.popen(f'id -u {user}').read().strip()
        env = f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus DISPLAY=:0"
        
        # Native gnome-terminal launch bridging directly into the netns
        cmd = f"sudo -u {user} env {env} gnome-terminal -- bash -c 'sudo ip netns exec {node_name} bash' >/dev/null 2>&1 &"
        os.system(cmd)
        print(f"*** Opened Gnome Terminal for {node_name}")

    def do_capture(self, line):
        """
        Custom packet capture command.
        Usage:
          capture start <node> <interface> <filename.pcap>
          capture stop <node>
        """
        args = line.split()
        if len(args) < 2:
            print("Usage: capture start r1 r1-eth0 captures/traffic.pcap | capture stop r1")
            return

        action, node_name = args[0], args[1]
        net = self.mn

        if node_name not in net:
            print(f"Node {node_name} not found.")
            return

        node = net[node_name]

        if action == "start":
            if len(args) != 4:
                print("Usage for start: capture start <node> <interface> <filename.pcap>")
                return
            intf, output_file = args[2], args[3]
            
            # Create captures directory if not exists
            os.system(f"mkdir -p {os.path.dirname(output_file) if '/' in output_file else 'captures'}")
            
            # Ensure path is absolute for nodes
            if not output_file.startswith('/'):
                output_file = os.path.join(os.getcwd(), output_file)

            print(f"Starting tcpdump on {node_name} intf {intf}. Saving to {output_file}")
            # Run tcpdump in background saving to the node's filesystem
            node.cmd(f'tcpdump -U -i {intf} -w {output_file} >/dev/null 2>&1 & echo $! > /tmp/{node_name}_tcpdump.pid')
            
        elif action == "stop":
            pid_file = f"/tmp/{node_name}_tcpdump.pid"
            print(f"Stopping packet capture on {node_name}...")
            out = node.cmd(f"if [ -f {pid_file} ]; then kill -9 `cat {pid_file}`; rm {pid_file}; echo 'Stopped'; else echo 'No capture running'; fi")
            print(out.strip())
        else:
            print("Unknown action.")

    def do_routes(self, line):
        """Show routing tables for all routers."""
        for rname in ['r1', 'r2', 'r3', 'r4', 'r5']:
            print(f'\n=== {rname.upper()} Routing Table ===')
            print(self.mn[rname].cmd('ip route show'))

    def do_neighbors(self, line):
        """Show OSPF neighbors for all routers."""
        for rname in ['r1', 'r2', 'r3', 'r4', 'r5']:
            print(f'\n=== {rname.upper()} OSPF Neighbors ===')
            print(self.mn[rname].cmd('echo -e "enable\\nshow ip ospf neighbor\\nexit" | nc -w 1 localhost 2604 | grep -v "--------"'))

def run():
    topo = Lab4Topo()
    net = Mininet(topo=topo, controller=None)
    net.start()

    r1, r2, r3, r4, r5 = net['r1'], net['r2'], net['r3'], net['r4'], net['r5']

    info('*** Assigning IP addresses...\n')
    # Area 0 Links
    r1.cmd('ifconfig r1-eth0 10.0.13.1/30')
    r3.cmd('ifconfig r3-eth0 10.0.13.2/30')
    # Area 10 Links
    r1.cmd('ifconfig r1-eth1 10.0.14.1/30')
    r4.cmd('ifconfig r4-eth0 10.0.14.2/30')
    # Area 20 Links
    r1.cmd('ifconfig r1-eth2 10.0.12.1/30')
    r2.cmd('ifconfig r2-eth0 10.0.12.2/30')
    # Area 30 Links
    r3.cmd('ifconfig r3-eth1 10.0.35.1/30')
    r5.cmd('ifconfig r5-eth0 10.0.35.2/30')

    # Gateway IP Addresses
    r4.cmd('ifconfig r4-eth1 192.168.10.254/24')
    r4.cmd('ifconfig r4-eth2 192.168.20.254/24')
    r2.cmd('ifconfig r2-eth1 172.16.10.254/24')
    r5.cmd('ifconfig r5-eth1 192.168.30.254/24')

    info('*** Waiting for OSPF daemons to start (3s)....\n')
    time.sleep(3)

    # --- OSPF Configuration ---
    def configure_ospf(node, router_id, networks, extra_cmds=""):
        """
        Hàm tiện ích đổ cấu hình OSPF vào tiến trình ospfd thông qua port điều khiển nội bộ 2604 (VTY) của thiết bị.
        networks: Danh sách các mạng cần quảng bá kèm theo Area của chúng. Ví dụ: [('10.0.13.0/30', '0')].
        """
        cmds = "enable\\n"
        cmds += "configure terminal\\n"
        cmds += f"router ospf\\n"
        cmds += f"ospf router-id {router_id}\\n"
        for net, area in networks:
            cmds += f"network {net} area {area}\\n"
        if extra_cmds:
            cmds += extra_cmds + "\\n"
        cmds += "exit\\nexit\\nwrite\\n"
        node.cmd(f'echo -e "{cmds}" | nc -w 1 localhost 2604 >/dev/null 2>&1')

    info('*** Applying OSPF configurations...\n')
    
    # ================= KHU VỰC CẤU HÌNH VAI TRÒ OSPF BẰNG CLI =================
    
    # R1: Xương sống Backbone (ABR). Giao tiếp với R3 (Backbone), R4 (Inside Area 10) và R2 (DMZ Area 20).
    configure_ospf(r1, '1.1.1.1',
        [('10.0.13.0/30', '0'), ('10.0.14.0/30', '10'), ('10.0.12.0/30', '20')],
        "int r1-eth0\nip ospf network point-to-point\n"
        "int r1-eth1\nip ospf network point-to-point\n"
        "int r1-eth2\nip ospf network point-to-point")

    # R2: Bộ định tuyến khu vực DMZ (Area 20). Chứa Web/Mail Server (172.16.10.x). Không chạy OSPF về hướng Switch để tối ưu (passive-interface).
    configure_ospf(r2, '2.2.2.2',
        [('10.0.12.0/30', '20'), ('172.16.10.0/24', '20')],
        "int r2-eth0\nip ospf network point-to-point\npassive-interface r2-eth1")

    # R3: Bộ định tuyến Backbone phụ (ABR). Giao tiếp R1 và nối ra Chi nhánh Branch R5 (Area 30).
    configure_ospf(r3, '3.3.3.3',
        [('10.0.13.0/30', '0'), ('10.0.35.0/30', '30')],
        "int r3-eth0\nip ospf network point-to-point\n"
        "int r3-eth1\nip ospf network point-to-point")

    # R4: Cửa ngõ Mạng Nội Bộ (Inside HQ - Area 10). Phục vụ mạng Nhân viên (Staff 192.168.10.x) và Quản trị (Mgmt 192.168.20.x).
    configure_ospf(r4, '4.4.4.4',
        [('10.0.14.0/30', '10'), ('192.168.10.0/24', '10'), ('192.168.20.0/24', '10')],
        "int r4-eth0\nip ospf network point-to-point\n"
        "passive-interface r4-eth1\npassive-interface r4-eth2")

    # R5: Bộ định tuyến Chi nhánh (Branch - Area 30). Nối với mạng khách (192.168.30.x).
    configure_ospf(r5, '5.5.5.5',
        [('10.0.35.0/30', '30'), ('192.168.30.0/24', '30')],
        "int r5-eth0\nip ospf network point-to-point\npassive-interface r5-eth1")

    if '--capture' in sys.argv:
        generate_pcaps(net)
        net.stop()
        return

    info('*** Lab environment ready!\n')
    info('*** Mapping namespaces for native terminal usage...\n')
    os.system('mkdir -p /var/run/netns')
    for name in net.keys():
        pid = net[name].pid
        os.system(f'ln -sf /proc/{pid}/ns/net /var/run/netns/{name}')

    info('*** Available custom CLI commands:\n')
    info('  gterm <node>                              : Opens Gnome-Terminal natively (fixes Ubuntu GUI bug)\n')
    info('  acl                                       : Applies the Firewall/ACL rules midway\n')
    info('  capture start <node> <intf> <file>        : Starts silent tcpdump\n')
    info('  capture stop <node>                       : Stops running tcpdump\n')
    info('  routes                                    : Show IP routes of all routers\n')
    info('  neighbors                                 : Show OSPF neighbors\n')
    
    CustomCLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    if os.geteuid() != 0:
        print('Error: Run as root. E.g: sudo python3 topology.py')
        sys.exit(1)

    mn_cleanup()
    run()
