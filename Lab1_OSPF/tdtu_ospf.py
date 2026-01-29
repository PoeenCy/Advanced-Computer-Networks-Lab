#!/usr/bin/python3
import os
import time
# Kiem tra thu vien ve hinh, neu khong co thi bo qua
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    HAS_GRAPH = True
except ImportError:
    HAS_GRAPH = False

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

# --- CLASS ROUTER (FRR) ---
class FRRouter(Node):
    def config(self, **params):
        super(FRRouter, self).config(**params)
        # Bat tinh nang chuyen tiep goi tin
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        
        # 1. Tao moi truong rieng biet trong /tmp
        confDir = f'/tmp/{self.name}'
        self.cmd(f'rm -rf {confDir} && mkdir -p {confDir}')
        self.cmd(f'chmod 777 {confDir}')
        
        # 2. Tao file config co ban
        # QUAN TRONG: 'no login' giup script tu dong nhap lenh
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
        
        # Gan quyen so huu cho user 'frr'
        self.cmd(f'chown -R frr:frr {confDir}')
        
        # 3. Khoi dong Zebra va OSPF tren TCP Localhost (127.0.0.1)
        # Zebra: 2601, OSPF: 2604
        self.cmd(f'/usr/lib/frr/zebra -d -u frr -g frr -A 127.0.0.1 -f {confDir}/zebra.conf -i {confDir}/zebra.pid')
        self.cmd(f'/usr/lib/frr/ospfd -d -u frr -g frr -A 127.0.0.1 -f {confDir}/ospfd.conf -i {confDir}/ospfd.pid')

    def terminate(self):
        self.cmd(f'kill `cat /tmp/{self.name}/ospfd.pid` 2> /dev/null')
        self.cmd(f'kill `cat /tmp/{self.name}/zebra.pid` 2> /dev/null')
        super(FRRouter, self).terminate()

# --- SO DO MANG TDTU ---
class TDTU_Topo(Topo):
    def build(self):
        # Area 0 Switch
        s1 = self.addSwitch('s1', failMode='standalone')
        
        # Tao 6 Router
        r1 = self.addHost('r1', cls=FRRouter)
        r2 = self.addHost('r2', cls=FRRouter)
        r3 = self.addHost('r3', cls=FRRouter)
        r4 = self.addHost('r4', cls=FRRouter)
        r5 = self.addHost('r5', cls=FRRouter)
        r6 = self.addHost('r6', cls=FRRouter)
        
        # Area 0
        self.addLink(r1, s1, intfName1='r1-eth0')
        self.addLink(r2, s1, intfName1='r2-eth0')
        self.addLink(r3, s1, intfName1='r3-eth0')
        
        # Area 10
        self.addLink(r1, r4, intfName1='r1-eth1', intfName2='r4-eth0')
        
        # Area 20
        self.addLink(r2, r5, intfName1='r2-eth1', intfName2='r5-eth0')
        self.addLink(r5, r6, intfName1='r5-eth1', intfName2='r6-eth0')
        self.addLink(r2, r6, intfName1='r2-eth2', intfName2='r6-eth1') # Du phong

# --- HAM VE HINH ---
def draw_topology(net):
    if not HAS_GRAPH:
        info('*** Khong tim thay thu vien ve hinh (networkx/matplotlib). Bo qua buoc nay.\n')
        return

    info('*** Dang ve so do mang va luu thanh "tdtu_topology.png"...\n')
    try:
        G = nx.Graph()
        for link in net.links:
            n1 = link.intf1.node.name
            n2 = link.intf2.node.name
            G.add_edge(n1, n2)
        
        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 8))
        
        color_map = []
        for node in G:
            if 's' in node: color_map.append('red')
            else: color_map.append('skyblue')
            
        nx.draw(G, pos, node_color=color_map, with_labels=True, node_size=2000, font_weight='bold')
        plt.title("TDTU Backbone Topology (OSPFv2)")
        plt.savefig("tdtu_topology.png")
        plt.close()
        info('*** Da luu anh thanh cong!\n')
    except Exception as e:
        info(f'*** Loi khi ve hinh: {e}\n')

def run():
    topo = TDTU_Topo()
    net = Mininet(topo=topo, controller=None)
    net.start()
    
    # --- [FIX] LAY DOI TUONG NODE TU MANG ---
    # Day la buoc quan trong de sua loi "NameError" ban gap phai
    r1, r2, r3 = net['r1'], net['r2'], net['r3']
    r4, r5, r6 = net['r4'], net['r5'], net['r6']
    
    # --- QUY HOACH IP ---
    info('*** Gan dia chi IP thu cong...\n')
    
    # Area 0
    r1.cmd('ifconfig r1-eth0 10.0.0.1/24')
    r2.cmd('ifconfig r2-eth0 10.0.0.2/24')
    r3.cmd('ifconfig r3-eth0 10.0.0.3/24')
    
    # Area 10
    r1.cmd('ifconfig r1-eth1 10.10.14.1/30')
    r4.cmd('ifconfig r4-eth0 10.10.14.2/30')
    
    # Area 20
    r2.cmd('ifconfig r2-eth1 10.20.25.1/30')
    r5.cmd('ifconfig r5-eth0 10.20.25.2/30')
    r5.cmd('ifconfig r5-eth1 10.20.56.1/30')
    r6.cmd('ifconfig r6-eth0 10.20.56.2/30')
    r2.cmd('ifconfig r2-eth2 10.20.26.1/30')
    r6.cmd('ifconfig r6-eth1 10.20.26.2/30')

    info('*** Doi 5s cho tien trinh OSPF khoi dong on dinh...\n')
    time.sleep(5)

    # --- HAM CAU HINH QUA NETCAT ---
    def config_ospf_via_tcp(node, rid, networks, extra=""):
        cmds = f"enable\nconf t\nrouter ospf\nospf router-id {rid}\n"
        for net_addr, area in networks:
            cmds += f"network {net_addr} area {area}\n"
        if extra: cmds += f"exit\n{extra}\n"
        cmds += "end\nwr\nexit\n"
        
        # Gui lenh -> Loc ky tu rac -> Python doc ket qua
        node.cmd(f'echo -e "{cmds}" | nc -w 1 localhost 2604 | tr -cd \'\\11\\12\\15\\40-\\176\'')

    info('*** Dang nap cau hinh OSPF (Nhiem vu 1, 2, 3)...\n')
    
    # R1: ABR Area 0-10
    config_ospf_via_tcp(r1, '1.1.1.1', 
                        [('10.0.0.0/24', '0'), ('10.10.14.0/30', '10')], 
                        "int r1-eth1\nip ospf network point-to-point")
    
    # R2: ABR Area 0-20
    config_ospf_via_tcp(r2, '2.2.2.2', 
                        [('10.0.0.0/24', '0'), ('10.20.25.0/30', '20'), ('10.20.26.0/30', '20')])
    
    # R3: Priority 0
    config_ospf_via_tcp(r3, '3.3.3.3', 
                        [('10.0.0.0/24', '0')], 
                        "int r3-eth0\nip ospf priority 0")
    
    # R4: Area 10
    config_ospf_via_tcp(r4, '4.4.4.4', 
                        [('10.10.14.0/30', '10')], 
                        "int r4-eth0\nip ospf network point-to-point")
    
    # R5: Thu vien
    config_ospf_via_tcp(r5, '5.5.5.5', 
                        [('10.20.25.0/30', '20'), ('10.20.56.0/30', '20')])
    
    # R6: KTX (Cost 500)
    config_ospf_via_tcp(r6, '6.6.6.6', 
                        [('10.20.56.0/30', '20'), ('10.20.26.0/30', '20')], 
                        "int r6-eth1\nip ospf cost 500")

    info('*** Doi 15s cho mang hoi tu OSPF...\n')
    time.sleep(15)

    # --- VE HINH ---
    draw_topology(net)

    info('\n=== KET QUA KIEM TRA TU DONG ===\n')
    
    def show_cmd(node, command):
        return node.cmd(f'echo -e "enable\\n{command}\\nexit" | nc -w 1 localhost 2604 | tr -cd \'\\11\\12\\15\\40-\\176\'')

    info("1. Trang thai Interface cua R1:\n")
    print(show_cmd(r1, "show ip ospf interface"))
    
    info("2. Bang lang gieng cua R1:\n")
    print(show_cmd(r1, "show ip ospf neighbor"))

    info("3. Kiem tra Ping tu R4 -> R6:\n")
    print(r4.cmd('ping -c 2 10.20.56.2'))
    
    info("\n*** HUONG DAN SU DUNG THU CONG: ***\n")
    info("  Copy lenh duoi day va dan vao dau nhac mininet> :\n")
    info("  r1 echo -e \"show ip ospf neighbor\\nexit\" | nc localhost 2604 | tr -cd '\\11\\12\\15\\40-\\176'\n")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    # Xoa rac truoc khi chay
    os.system('sudo mn -c 2>/dev/null')
    os.system('sudo rm -rf /tmp/r* 2>/dev/null')
    run()