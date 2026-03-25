#!/bin/bash
# source/loadbalance_scenario.sh
# Kịch bản sinh luồng dữ liệu (Traffic Generator) IPv6 OSPFv3 ECMP

echo "=== Kịch bản Test Cân bằng Tải IPv6 ECMP trên Spine s1 và s2 ==="

echo "Tạm thời gỡ bỏ Tường lửa Zero Trust (ip6tables) để luồng dữ liệu Loadbalancer chạy lọt qua..."
for node in web_server1 dns_server1 s3 s4; do
    ip netns exec $node ip6tables -F INPUT 2>/dev/null
    ip netns exec $node ip6tables -F FORWARD 2>/dev/null
done

echo "Đang khởi tạo iPerf Server trên DNS_SERVER1 (IPv6: fd00:20::1)..."
ip netns exec dns_server1 iperf -s -V -D

echo "Bắt đầu bơm traffic IPv6 dạng lũ từ WEB_SERVER1 (fd00:10::1) tới DNS_SERVER1 (fd00:20::1) qua 100 luồng UDP/TCP song song..."
ip netns exec web_server1 iperf -V -c fd00:20::1 -P 100 -t 40 > /tmp/iperf_web1.log &

echo "Bơm thêm traffic nền IPv6 NAT64 từ DB_SERVER1 đi Public IPv4 (serverHCM)..."
# Với NAT64 trên r1, ping tới IPv4 bằng cách bọc tiền tố 64:ff9b::
# Ở đây ta giả lập bằng ping flood IPv6.
ip netns exec db_server1 ping6 -f -c 50000 64:ff9b::203.162.1.1 > /dev/null 2>&1 &

echo ">> Hệ thống OSPFv3 sẽ tự phân chia luồng dữ liệu IPv6. Hãy mở File stats_tool.py GUI lên để xem biểu đồ Spine s1 vs s2 ngay lúc này!"