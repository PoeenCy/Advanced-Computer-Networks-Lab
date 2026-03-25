#!/usr/bin/env python3
# source/draw_failover.py
import sys
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def parse_ping_log(filepath):
    data = {}
    max_seq = 0
    min_seq = float('inf')
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                m = re.search(r'icmp_seq=(\d+).*time=([\d\.]+)\s*ms', line)
                if m:
                    seq = int(m.group(1))
                    rtt = float(m.group(2))
                    data[seq] = rtt
                    max_seq = max(max_seq, seq)
                    min_seq = min(min_seq, seq)
    except Exception as e:
        print(f"Lỗi đọc file log ICMP: {e}")
        return [], [], 0
                
    if max_seq == 0 or min_seq == float('inf'):
        return [], [], 0
        
    seqs = list(range(int(min_seq), int(max_seq) + 1))
    rtts = []
    loss_count = 0
    
    for s in seqs:
        if s in data:
            rtts.append(data[s])
        else:
            rtts.append(-1.0)
            loss_count += 1
            
    return seqs, rtts, loss_count

def generate_comparative_chart():
    log_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/ping_failover.log'
    seqs, rtts, loss_count = parse_ping_log(log_file)
    
    if not seqs:
        fig, ax = plt.subplots(figsize=(11, 5.5))
        ax.text(0.5, 0.5, "BÀI TEST FAILOVER THẤT BẠI: KHÔNG CÓ TÍN HIỆU PING NỀN TRẢ VỀ!\n\n(Lý do: Tường lửa Zero Trust có thể vẫn đang chặn luồng Ping Test.\nHãy gõ lệnh 'dropacl' trên Mininet để xóa Firewall, sau đó chạy lại 'failtest'!)", ha='center', va='center', fontweight='bold', fontsize=12, color='red', bbox=dict(boxstyle='round,pad=1', fc='#ffe6e6', ec='red'))
        ax.axis('off')
        plt.tight_layout()
        plt.savefig('/home/mn/mmtnc_lab4/failover_chart.png')
        print("Trống dữ liệu Ping mô phỏng! Đã xuất ảnh báo lỗi thành /home/mn/mmtnc_lab4/failover_chart.png")
        sys.exit(0)
    
    conv_time = loss_count * 0.1
    
    fig, ax = plt.subplots(figsize=(11, 5.5))
    
    import numpy as np
    
    x_valid = [s for s, r in zip(seqs, rtts) if r >= 0]
    y_valid = [r for r in rtts if r >= 0]
    x_loss = [s for s, r in zip(seqs, rtts) if r < 0]
    y_loss = [0.0] * len(x_loss)
    
    # Bẻ gãy đường vẽ bằng NaN tại các thời điểm rớt gói
    y_line = [r if r >= 0 else np.nan for r in rtts]
    
    # Trace the latency dots
    ax.plot(seqs, y_line, 'g-', label='Nhịp Ping Thành công (RTT)', linewidth=1.5)
    
    if x_loss:
        # Paint the outage area Red
        ax.axvspan(x_loss[0]-1, x_loss[-1]+1, color='red', alpha=0.15, label='Khu vực Nhiễu tín hiệu (Đang Dò tìm Route Mới)')
        ax.scatter(x_loss, y_loss, color='red', marker='x', label='Gói tin thất lạc (Timeout/ICMP Drop)', s=40)
    
    ax.set_title(f'Báo cáo Giám sát Sự cố Đứt Cáp Lõi Backbone Data Center (Spine s1)\nSo Sánh Tốc Độ: Trước, Trong và Sau Sự cố (Hội tụ Mất {conv_time:.2f} giây)', fontweight='bold', pad=15)
    ax.set_xlabel('Số thứ tự Gói tin Ping (Interval 0.1 giây/Gói)')
    ax.set_ylabel('Độ trễ quá cảnh (Ping RTT)')
    
    # Calculate annotation anchors dynamically
    max_y = max(y_valid) if y_valid else 1.0
    if x_loss:
        mid_before = x_loss[0] / 2
        mid_after = x_loss[-1] + (seqs[-1] - x_loss[-1])/2
        ax.text(mid_before, max_y * 0.85, 'GIAI ĐOẠN ỔN ĐỊNH BẮT ĐẦU\n(Đường truyền đi qua R1/Spine 1)', ha='center', va='center', fontweight='bold', backgroundcolor='white', bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='green', alpha=0.9))
        ax.text(mid_after, max_y * 0.85, 'SAU KHI OSPF HỘI TỤ THÀNH CÔNG\n(Tự động điều Route qua R2/Spine 2)', ha='center', va='center', fontweight='bold', backgroundcolor='white', bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='blue', alpha=0.9))
    
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('/home/mn/mmtnc_lab4/failover_chart.png')
    print(f"[+] Vẽ thành công bức tranh Siêu trực quan Failover tại: /home/mn/mmtnc_lab4/failover_chart.png")

if __name__ == "__main__":
    generate_comparative_chart()
