import sys
import os
import time
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory

# Add source directory to path to import tool.py
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.abspath(os.path.join(current_dir, '../source'))
sys.path.append(source_dir)

import tool

app = Flask(__name__)

# Global log storage for web UI
global_logs = []

def web_log_ui(txt_wid, msg):
    timestamp = time.strftime('%H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    global_logs.append(log_line)
    tool.log_to_file(msg)

# Monkey-patch tool.py's log_ui so it writes to our web array instead of Tkinter
tool.log_ui = web_log_ui

def get_node_traffic(node_name):
    # Total TX and RX for a node excluding loopback
    intfs_str = tool.exec_netns(node_name, "ls /sys/class/net/ 2>/dev/null").strip()
    if not intfs_str: return 0, 0
    intfs = intfs_str.split()
    
    rx_total, tx_total = 0, 0
    for i in intfs:
        if i in ['lo', 'vxlan100']: continue
        try:
            rx = int(tool.exec_netns(node_name, f"cat /sys/class/net/{i}/statistics/rx_bytes").strip() or 0)
            tx = int(tool.exec_netns(node_name, f"cat /sys/class/net/{i}/statistics/tx_bytes").strip() or 0)
            rx_total += rx
            tx_total += tx
        except: pass
    return rx_total, tx_total

@app.route('/')
def index():
    return render_template('index.html', nodes=tool.NODE_LIST)

@app.route('/api/logs')
def get_logs():
    last_idx = int(request.args.get('last_idx', 0))
    new_logs = global_logs[last_idx:]
    return jsonify({
        'logs': new_logs,
        'next_idx': len(global_logs)
    })

@app.route('/api/traffic')
def get_traffic():
    src = request.args.get('src')
    dst = request.args.get('dst')
    if not src or not dst: return jsonify({'error': 'Missing parameters'}), 400
    
    src_rx, src_tx = get_node_traffic(src)
    dst_rx, dst_tx = get_node_traffic(dst)
    
    return jsonify({
        'timestamp': time.time(),
        'src': {'rx_bytes': src_rx, 'tx_bytes': src_tx},
        'dst': {'rx_bytes': dst_rx, 'tx_bytes': dst_tx}
    })

@app.route('/api/diagnostics', methods=['POST'])
def run_diagnostics():
    data = request.json
    action = data.get('action')
    src = data.get('src')
    dst = data.get('dst')
    
    if src == dst:
        return jsonify({'error': 'Nguồn và Đích không được trùng nhau!'}), 400
        
    def task():
        msg = f"\n[Executing] {action.upper()} từ {src} -> {dst}...\n"
        global_logs.append(msg)
        try:
            if action == 'ping':
                rtt = tool.measure_rtt(src, dst)
                res_msg = f"➜ Độ trễ (RTT): {rtt} ms" if rtt >= 0 else "➜ Lỗi: Không thể Ping (Timeout)"
            elif action == 'path':
                pth = tool.measure_path(src, dst)
                res_msg = f"➜ Đường đi (Trace): \n    {pth}"
            elif action == 'loss':
                ls = tool.measure_loss(src, dst)
                res_msg = f"➜ Tỉ lệ rớt gói (Packet Loss): {ls}%"
            else:
                res_msg = f"➜ Unknown action: {action}"
            
            global_logs.append(f"[{time.strftime('%H:%M:%S')}] {res_msg}")
        except Exception as e:
            global_logs.append(f"[{time.strftime('%H:%M:%S')}] Lỗi thực thi: {str(e)}")
            
    # Run in background to avoid blocking Flask
    threading.Thread(target=task, daemon=True).start()
    return jsonify({'status': 'started'})

@app.route('/api/run_cases', methods=['POST'])
def run_cases():
    data = request.json
    cases = data.get('cases', [])
    src = data.get('src', 'web_server1')
    dst = data.get('dst', 'db_server1')
    
    if not cases:
        return jsonify({'error': 'Vui lòng chọn ít nhất 1 biểu đồ cần chạy!'}), 400

    def task():
        global_logs.append(f"\n[{time.strftime('%H:%M:%S')}] >>> BẮT ĐẦU CHẠY KỊCH BẢN XUẤT BIỂU ĐỒ <<<")
        try:
            if 1 in cases: tool.case1_ospf_startup(None)
            if 2 in cases: tool.case2_s1_failover(None)
            if 3 in cases: tool.case3_firewall_acl(None)
            if 4 in cases: tool.case4_ecmp_balance(None)
            if 5 in cases: tool.case5_path_tracing(None, src, dst)
            global_logs.append(f"[{time.strftime('%H:%M:%S')}] >>> KẾT THÚC CHUỖI XUẤT BIỂU ĐỒ <<<")
        except Exception as e:
            global_logs.append(f"[{time.strftime('%H:%M:%S')}] Lỗi nghiêm trọng khi chạy biểu đồ: {str(e)}")

    threading.Thread(target=task, daemon=True).start()
    return jsonify({'status': 'started'})

@app.route('/api/images/<filename>')
def serve_image(filename):
    return send_from_directory(tool.LOG_DIR, filename)

if __name__ == '__main__':
    # Log startup message
    global_logs.append(f"[{time.strftime('%H:%M:%S')}] === HỆ THỐNG WEB DASHBOARD ĐÃ SẴN SÀNG ===")
    global_logs.append(f"[{time.strftime('%H:%M:%S')}] Mọi kết quả Biểu Đồ & Log sẽ được lưu tại: {tool.LOG_DIR}")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
