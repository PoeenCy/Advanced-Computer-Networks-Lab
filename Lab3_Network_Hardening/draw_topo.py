import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_topology(save_path='topology.png'):
    G = nx.Graph()

    nodes = {
        'R1':{'label':'R1\nABR 0/10\n10.0.0.1','zone':'core','shape':'s'},
        'R2':{'label':'R2\nABR 0/20/30\n10.0.0.2','zone':'core','shape':'s'},
        'R3':{'label':'R3\nCore\n10.0.0.3','zone':'core','shape':'s'},
        'R4':{'label':'R4\nHQ\n10.10.14.2','zone':'hq','shape':'s'},
        'R5':{'label':'R5\nDMZ\n10.20.25.2','zone':'dmz','shape':'s'},
        'R6':{'label':'R6\nIoT\n10.30.56.2','zone':'iot','shape':'s'},
        'pc1':{'label':'pc1\n10.1.1.10','zone':'staff','shape':'o'},
        'pc2':{'label':'pc2\n10.1.1.11','zone':'staff','shape':'o'},
        'admin':{'label':'admin\n10.1.2.50','zone':'mgmt','shape':'o'},
        'filesrv':{'label':'filesrv\n10.1.2.100','zone':'mgmt','shape':'o'},
        'web':{'label':'web\n172.16.10.100','zone':'dmz_h','shape':'o'},
        'email':{'label':'email\n172.16.10.101','zone':'dmz_h','shape':'o'},
        'syslog':{'label':'syslog\n172.16.10.200','zone':'dmz_h','shape':'o'},
        'cam1':{'label':'cam1\n.100.10','zone':'iot_h','shape':'o'},
        'cam15':{'label':'cam15\n.100.15\nCOMPROMISED','zone':'hack','shape':'o'},
        'sensor':{'label':'sensor\n.100.50','zone':'iot_h','shape':'o'},
    }
    for n, d in nodes.items(): G.add_node(n, **d)

    edges = [
        ('R1','R2'), ('R2','R3'), ('R3','R1'),
        ('R1','R4'), ('R2','R5'), ('R5','R6'), ('R2','R6'),
        ('R4','pc1'), ('R4','pc2'), ('R4','admin'), ('R4','filesrv'),
        ('R5','web'), ('R5','email'), ('R5','syslog'),
        ('R6','cam1'), ('R6','cam15'), ('R6','sensor'),
    ]
    for s, d in edges: G.add_edge(s, d)

    COLORS = {'core':'#cce5ff','hq':'#d4edda','dmz':'#fff3cd','iot':'#f8d7da',
              'staff':'#28a745','mgmt':'#20c997','dmz_h':'#ffc107',
              'iot_h':'#fd7e14','hack':'#dc3545'}

    pos = {
        'R1':(-2,4),'R2':(0,4),'R3':(2,4),
        'R4':(-4,2),'R5':(0,2),'R6':(4,2),
        'pc1':(-5.5,0),'pc2':(-4.5,0),'admin':(-3.5,0),'filesrv':(-2.5,0),
        'web':(-1,0),'email':(0,0),'syslog':(1,0),
        'cam1':(3,0),'cam15':(4.5,0),'sensor':(6,0),
    }

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    routers = [n for n in G.nodes if nodes[n]['shape']=='s']
    hosts = [n for n in G.nodes if nodes[n]['shape']=='o']

    nx.draw_networkx_nodes(G, pos, nodelist=routers,
        node_color=[COLORS[nodes[n]['zone']] for n in routers],
        node_size=3000, node_shape='s', ax=ax, linewidths=2, edgecolors='black')
    
    nx.draw_networkx_nodes(G, pos, nodelist=hosts,
        node_color=[COLORS[nodes[n]['zone']] for n in hosts],
        node_size=1500, node_shape='o', ax=ax, linewidths=1.5, edgecolors='black')
    
    # Draw edges with varying styles
    main_edges = [e for e in edges if e != ('R2', 'R6')]
    backup_edge = [('R2', 'R6')]
    
    nx.draw_networkx_edges(G, pos, edgelist=main_edges, edge_color='black', width=1.5, alpha=0.8, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=backup_edge, edge_color='red', width=2, style='dashed', alpha=0.8, ax=ax)

    labels = {n: nodes[n]['label'] for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='black', font_weight='bold', ax=ax)

    legend = [
        mpatches.Patch(color='#cce5ff', label='Area 0 - Backbone'),
        mpatches.Patch(color='#d4edda', label='Area 10 - HQ (Staff+Mgmt)'),
        mpatches.Patch(color='#fff3cd', label='Area 20 - DMZ'),
        mpatches.Patch(color='#f8d7da', label='Area 30 - IoT (Totally Stubby)'),
        mpatches.Patch(color='#dc3545', label='Compromised Device'),
    ]
    ax.legend(handles=legend, loc='upper right', fontsize=10,
              facecolor='white', edgecolor='black', labelcolor='black')
              
    ax.set_title('Logical Network Topology\nOSPF Multi-Area & Extended ACLs',
                 color='black', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f'Topology successfully saved to {save_path}')

if __name__ == '__main__':
    draw_topology('d:/Advanced-Computer-Networks-Lab/Lab3_Network_Hardening/topology_logical_2d.png')
