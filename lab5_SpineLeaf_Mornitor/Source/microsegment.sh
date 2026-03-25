#!/bin/bash
# source/microsegment.sh
# Kịch bản ip6tables thiết lập Zero Trust Micro-segmentation (Chuẩn IPv6)

echo "=== Triển khai Zero Trust IPv6 Micro-segmentation ==="

WEB_NET="fd00:10::/64"
DNS_NET="fd00:20::/64"
DB_NET="fd00:30::/64"

# 1. Clear cũ
for node in web_server1 dns_server1 db_server1 s3 s4 s5; do
    ip netns exec $node ip6tables -F INPUT 2>/dev/null
    ip netns exec $node ip6tables -F FORWARD 2>/dev/null
done

# 2. Host-based Micro-segmentation (IPv6)
echo " -> Thiết lập Host Firewall (IPv6 VM Level)..."

# Tại Web VM: Không cho DNS và DB chọc ngang sang
ip netns exec web_server1 ip6tables -A INPUT -s $DNS_NET -j LOG --log-prefix "ZT-BLOCK-V6: "
ip netns exec web_server1 ip6tables -A INPUT -s $DNS_NET -j DROP
ip netns exec web_server1 ip6tables -A INPUT -s $DB_NET -j LOG --log-prefix "ZT-BLOCK-V6: "
ip netns exec web_server1 ip6tables -A INPUT -s $DB_NET -j DROP

# 3. Leaf-based Firewall
echo " -> Thiết lập Leaf Router Firewall (IPv6 Network Level)..."
# Leaf s3 (Web) - Cắt kết hợp East-West với DNS và DB
ip netns exec s3 ip6tables -A FORWARD -s $WEB_NET -d $DNS_NET -j LOG --log-prefix "ZT-BLOCK-V6: "
ip netns exec s3 ip6tables -A FORWARD -s $WEB_NET -d $DNS_NET -j DROP
ip netns exec s3 ip6tables -A FORWARD -s $WEB_NET -d $DB_NET -j LOG --log-prefix "ZT-BLOCK-V6: "
ip netns exec s3 ip6tables -A FORWARD -s $WEB_NET -d $DB_NET -j DROP

# Leaf s5 (Database) - Chặn DNS truy cập thẳng DB nếu không cho phép
ip netns exec s5 ip6tables -A FORWARD -s $DNS_NET -d $DB_NET -j LOG --log-prefix "ZT-BLOCK-V6: "
ip netns exec s5 ip6tables -A FORWARD -s $DNS_NET -d $DB_NET -j DROP

echo "Hoàn thành! Các giao tiếp East-West trái phép IPv6 đã bị chặn đứng."
