# Hướng dẫn chạy Lab3 Network Hardening

## 1. Cài đặt thư viện

```bash
# FRRouting (OSPF daemon)
curl -s https://deb.frrouting.org/frr/keys.gpg | sudo tee /usr/share/keyrings/frrouting.gpg > /dev/null
FRRVER="frr-stable"
echo deb '[signed-by=/usr/share/keyrings/frrouting.gpg]' https://deb.frrouting.org/frr $(lsb_release -s -c) $FRRVER | sudo tee -a /etc/apt/sources.list.d/frr.list
sudo apt update && sudo apt install frr frr-pythontools -y

# Python libs (ve hinh)
pip install networkx matplotlib
```

---

## 2. Khởi động mạng

```bash
sudo python3 topology.py
```

Script sẽ tự động:
1. Cleanup Mininet cũ (`mn -c`)
2. Tạo topology (6 routers, 10 hosts, 5 switches)
3. Gán IP thủ công
4. Cấu hình OSPF Multi-Area qua netcat
5. Đợi 50s cho OSPF hội tụ (DR election + LSA exchange)
6. Vẽ topology → `topology.png`
7. Kiểm tra tự động: OSPF neighbors, routing table, ping inter-area
8. Mở Mininet CLI

---

## 3. Các lệnh CLI

| Lệnh | Mô tả |
|-------|--------|
| `acl` | Áp dụng ACL từ `configure_acls.sh` |
| `acl_status` | Xem iptables rules trên R4, R5, R6 |
| `acl_clear` | Xóa tất cả ACL rules |
| `routes` | Xem routing tables 6 routers |
| `neighbors` | Xem OSPF neighbors |
| `pingall` | Ping tất cả nodes |

---

## 4. Áp dụng ACL

```
mininet> acl
```

Lệnh này chạy file `configure_acls.sh` — deploy 4 ACL policies bằng iptables.

---

## 5. Giải thích ACL

### ACL 110: Cô lập IoT (R6)

**Vị trí:** Router R6, interface r6-eth2 (kết nối IoT Zone), chiều IN

**Mục tiêu:** IoT là zone UNTRUST — camera15 có thể bị hack → cô lập hoàn toàn.

**Thứ tự rules (first-match-wins!)**

```
1. ESTABLISHED,RELATED → ACCEPT    ← Cho phép gói phản hồi
2. IoT → Syslog:514/UDP → ACCEPT   ← IoT gửi log để monitoring
3. IoT → Management → DROP + LOG   ← Chặn truy cập salary DB
4. IoT → Staff → DROP + LOG        ← Chặn truy cập PC nhân viên
5. IoT → DMZ → DROP + LOG          ← Chặn DMZ (trừ Syslog ở rule 2)
6. IoT → 10.0.0.0/8 → DROP + LOG   ← Chặn mọi mạng nội bộ còn lại
7. IoT → ICMP echo → ACCEPT        ← Cho ping Internet (firmware update)
```

**Tại sao ICMP ở cuối?** Vì iptables first-match-wins — nếu ICMP ACCEPT ở trước, nó match `0.0.0.0/0` (mọi destination) → DENY rules không bao giờ fire!

**Ví dụ test:**
```
mininet> camera1 ping -c 2 -W 2 10.1.2.50   # DROP (IoT → Mgmt)
mininet> camera1 ping -c 2 -W 2 10.1.1.10   # DROP (IoT → Staff)
mininet> camera1 ping -c 2 10.0.0.1          # DROP (IoT → Backbone)
mininet> r6 dmesg | grep ACL110              # Xem log bị chặn
```

---

### ACL 120: Bảo vệ DMZ (R5)

**Vị trí:** Router R5, interface r5-eth2, chiều IN

**Mục tiêu:** DMZ chứa webserver/email — nếu bị hack, KHÔNG cho tấn công vào mạng nội bộ (lateral movement).

```
1. ESTABLISHED,RELATED → ACCEPT
2. Any → Web:80 → ACCEPT            ← HTTP public
3. Any → Web:443 → ACCEPT           ← HTTPS public
4. Any → Email:25 → ACCEPT          ← SMTP inbound
5. Staff → DMZ:443 → ACCEPT         ← Nhân viên truy cập portal
6. Any → Syslog:514/UDP → ACCEPT    ← Nhận log từ thiết bị
7. DMZ → Inside (10.0.0.0/8) → DROP ← CHẶN lateral movement!
8. ICMP → ACCEPT                    ← Ping troubleshooting
```

**Ví dụ test:**
```
mininet> webserver ping -c 2 -W 2 10.1.2.50   # DROP (DMZ → Inside)
mininet> webserver ping -c 2 -W 2 10.1.1.10   # DROP (DMZ → Inside)
mininet> admin ping -c 2 172.16.10.100         # ACCEPT (Outside → Web)
```

---

### ACL 130: Kiểm soát Staff (R4)

**Vị trí:** Router R4, interface r4-eth1, chiều IN

**Mục tiêu:** Nhân viên chỉ được làm việc cơ bản — không truy cập Management (salary DB) hay IoT.

```
1. ESTABLISHED,RELATED → ACCEPT
2. Staff → DMZ:443 → ACCEPT         ← Internal web portal
3. Staff → DNS:53/UDP → ACCEPT      ← Domain resolution
4. Staff → Management → DROP + LOG  ← CHẶN salary database!
5. Staff → IoT → DROP + LOG         ← Không cần thiết
6. Staff → ICMP echo → ACCEPT       ← Ping (chỉ DMZ/backbone còn)
7. Management → Any → ACCEPT        ← Admin có FULL ACCESS
```

**Ví dụ test:**
```
mininet> pc1 ping -c 2 -W 2 10.1.2.50         # DROP (Staff → Mgmt)
mininet> pc1 ping -c 2 -W 2 192.168.100.10    # DROP (Staff → IoT)
mininet> pc1 ping -c 2 172.16.10.100           # ACCEPT (Staff → DMZ ICMP)
mininet> admin ping -c 2 192.168.100.10        # ACCEPT (Admin full access)
```

---

### ACL 140: SSH Access Control (Tất cả routers)

**Vị trí:** INPUT chain trên tất cả 6 routers

**Mục tiêu:** Chỉ Admin PC (10.1.2.50) SSH được vào thiết bị mạng.

```
1. 10.1.2.50 → TCP 22 → ACCEPT     ← Chỉ admin duy nhất
2. Any → TCP 22 → DROP + LOG       ← Tất cả nguồn khác bị chặn
```

---

## 6. Các lệnh khác

```bash
# Ve topology (khong can sudo)
python3 topology.py --draw

# Cleanup
sudo python3 topology.py --clean

# Help
python3 topology.py --help
```

---

## 7. Cấu trúc files

```
Lab3_Network_Hardening/
├── topology.py          # Topology + OSPF + CLI
├── configure_acls.sh    # ACL policies (iptables) - file riêng
├── testacl.txt          # Hướng dẫn test ACL chi tiết
├── huongdan.md          # File này
├── topology.png         # Hình topology (tự tạo khi chạy)
└── docs/
    ├── TOPOLOGY.md      # Thiết kế topology
    ├── REQUIREMENTS.md  # Yêu cầu đề bài
    └── VERIFICATION.md  # Test cases
```
