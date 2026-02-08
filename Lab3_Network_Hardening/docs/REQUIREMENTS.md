# YÊU CẦU KỸ THUẬT

**Nhiệm vụ cần thực hiện - KHÔNG có lời giải sẵn**

---

> ⚠️ **LƯU Ý QUAN TRỌNG:**  
> Tài liệu này CHỈ mô tả **YÊU CẦU** - KHÔNG cung cấp configuration commands.  
> Sinh viên phải tự nghiên cứu tài liệu Cisco IOS, Mininet, iptables để triển khai.

---

## I. YÊU CẦU TỔNG QUAN

**Mục tiêu:** Triển khai hạ tầng mạng an toàn theo thiết kế trong [TOPOLOGY.md](./TOPOLOGY.md), đáp ứng yêu cầu từ CISO trong [SCENARIO.md](./SCENARIO.md).

**Điểm tối đa:** 100 điểm

---

## II. PHẦN A - ĐỊNH TUYẾN OSPF MULTI-AREA (40 điểm)

### A1. Cấu hình OSPF Cơ bản (15 điểm)

**Yêu cầu:**
- [ ] Khởi tạo OSPF process trên tất cả 6 routers
- [ ] Cấu hình Router ID **rõ ràng** bằng Loopback interface
  - R1: RID = 1.1.1.1
  - R2: RID = 2.2.2.2
  - ...R6: RID = 6.6.6.6
- [ ] Khai báo networks vào đúng OSPF Areas:
  - R1, R2, R3: Area 0 (Backbone)
  - R4: Area 10
  - R5: Area 20
  - R6: Area 30

**Tài liệu tham khảo:**
- RFC 2328 - OSPF Version 2 (Section 9: The Routing Table Structure)
- Cisco IOS Command Reference: `router ospf`

**Câu hỏi để suy ngẫm:**
1. Tại sao phải dùng Loopback làm Router ID thay vì để OSPF tự chọn?
2. Điều gì xảy ra nếu 2 router có cùng Router ID trong cùng Area?

---

### A2. Tối ưu hóa OSPF (15 điểm)

**Yêu cầu:**
- [ ] **Network Type:** Đặt tất cả liên kết P2P (router-to-router) thành `point-to-point`
  - Tại sao? Tránh lãng phí thời gian bầu chọn DR/BDR không cần thiết
  - Liên kết nào cần? R1↔R4, R2↔R5, R2↔R6, R5↔R6
  
- [ ] **OSPF Priority** trên Area 0 (Backbone Switch):
  - R1: Priority = 100 (DR candidate)
  - R2: Priority = 100 (BDR candidate)
  - R3: Priority = 0 (NEVER DR/BDR)
  
- [ ] **Cost Manipulation** cho backup route:
  - Đường R2→R5→R6: Giữ nguyên cost mặc định
  - Đường R2→R6 (trực tiếp): Tăng cost lên **500**
  - Mục đích: Đường R2→R6 chỉ dùng khi R5 down

**Tài liệu tham khảo:**
- Cisco IOS: `ip ospf network point-to-point`
- Cisco IOS: `ip ospf priority`
- Cisco IOS: `ip ospf cost`

**Câu hỏi để suy ngẫm:**
1. Làm thế nào tính OSPF cost? (Công thức: Cost = ?)
2. Nếu không set cost 500, mà để mặc định, điều gì xảy ra?
   - Hint: ECMP (Equal-Cost Multi-Path)

---

### A3. OSPF Totally Stubby Area (10 điểm)

**Yêu cầu:**
- [ ] Cấu hình Area 30 (IoT) thành **Totally Stubby Area**
  - Trên ABR (R2): Khai báo `area 30 stub no-summary`
  - Trên Internal Router (R6): Khai báo `area 30 stub`

**Kết quả mong đợi:**
- Trên R6, lệnh `show ip route` chỉ hiển thị:
  - `O*IA 0.0.0.0/0` (default route duy nhất)
  - Directly connected subnets (C)
  - KHÔNG có route cụ thể đến Area 0, 10, 20

**Tại sao quan trọng?**
- Hacker chiếm R6 không biết IP của Management/Staff zones
- Giảm kích thước routing table → tiết kiệm RAM trên router yếu

**Tài liệu tham khảo:**
- RFC 2328 - Section 3.6: Virtual Links
- Cisco Doc: "OSPF Stub Areas"

**Câu hỏi để suy ngẫm:**
1. So sánh: Standard Area vs Stub Area vs Totally Stubby Area?
2. Area 0 (Backbone) có thể là Stub được không? Tại sao?

---

## III. PHẦN B - EXTENDED ACLs (40 điểm)

### B1. ACL 110: Cô lập IoT Zone (15 điểm)

**Vị trí:** Router R6, Interface eth2 (kết nối IoT Zone), Direction: **IN**

**Mục tiêu:** Chặn mọi traffic từ IoT đi vào Management, Staff, DMZ

**Logic yêu cầu:**
```
1. PERMIT: IoT → Syslog Server (172.16.10.200:514/UDP)
   Lý do: IoT cần gửi logs để monitoring

2. PERMIT: IoT → Internet (8.8.8.8)
   Lý do: IoT cần update firmware, NTP time sync
   Chú ý: Chỉ permit ping (ICMP echo), không permit tất cả

3. DENY: IoT → Management Zone (10.1.2.0/24)
   Keyword: log (để audit attempted attacks)

4. DENY: IoT → Staff Zone (10.1.1.0/24)
   Keyword: log

5. DENY: IoT → DMZ Zone (172.16.10.0/24) EXCEPT Syslog
   Keyword: log

6. DENY: ip any any (implicit deny, nên explicit để log)
```

**Wildcard Mask:**
- Chú ý: KHÔNG dùng subnet mask, phải dùng wildcard mask!
- Ví dụ: /24 subnet → Wildcard mask = 0.0.0.255
- Công thức: Wildcard = 255.255.255.255 - Subnet Mask

**Tài liệu tham khảo:**
- Cisco IOS: `access-list 100-199 extended`
- Mininet/Linux: `iptables -A INPUT/OUTPUT/FORWARD`

**Câu hỏi để suy ngẫm:**
1. Tại sao đặt ACL ở direction IN thay vì OUT?
2. Thứ tự các rules có quan trọng không? Điều gì xảy ra nếu đặt DENY trước PERMIT?

---

### B2. ACL 120: Bảo vệ DMZ (10 điểm)

**Vị trí:** Router R5, Interface eth2 (kết nối DMZ), Direction: **IN**

**Mục tiêu:** Cho phép Internet truy cập DMZ, chặn DMZ truy cập Inside

**Logic yêu cầu:**
```
1. PERMIT: Any → Web Server (172.16.10.100:80/TCP)
   Lý do: Public website

2. PERMIT: Any → Web Server (172.16.10.100:443/TCP)
   Lý do: HTTPS

3. PERMIT: Any → Email Server (172.16.10.101:25/TCP)
   Lý do: SMTP inbound

4. PERMIT: Staff (10.1.1.0/24) → DMZ (172.16.10.0/24:443/TCP)
   Lý do: Employees cần truy cập internal web portal

5. DENY: DMZ (172.16.10.0/24) → Inside (10.1.0.0/16)
   Keyword: log
   Lý do: Nếu Web Server bị hack, không cho nhảy vào Inside

6. PERMIT: ICMP echo-reply, time-exceeded, unreachable
   Lý do: Cho phép troubleshooting (traceroute, ping response)

7. DENY: ip any any log
```

**Khái niệm "Stateless" ACL:**
- ACLs trong Cisco/Linux là stateless (không nhớ session)
- Nếu permit request, phải permit response riêng (hoặc dùng `established` keyword)

**Câu hỏi để suy ngẫm:**
1. Tại sao cần permit ICMP unreachable? Điều gì xảy ra nếu block hết ICMP?
2. Có cách nào để ACL "nhớ" session không? (Hint: Reflexive ACLs, hoặc Stateful Firewall)

---

### B3. ACL 130: Kiểm soát Staff Zone (10 điểm)

**Vị trí:** Router R4, Interface eth1 (VLAN Staff), Direction: **IN**

**Mục tiêu:** Staff chỉ làm việc, không truy cập zones nhạy cảm

**Logic yêu cầu:**
```
1. PERMIT: Staff (10.1.1.0/24) → DMZ (172.16.10.0/24:443/TCP)
   Lý do: Truy cập internal portal

2. PERMIT: Staff → DNS (any:53/UDP)
   Lý do: Domain name resolution

3. PERMIT: Staff → Internet (ICMP echo)
   Lý do: Test connectivity

4. DENY: Staff → Management (10.1.2.0/24)
   Keyword: log
   Lý do: Nhân viên không được xem salary database

5. DENY: Staff → IoT (192.168.100.0/24)
   Keyword: log
   Lý do: Không cần thiết

6. DENY: ip any any log
```

**Nguyên tắc Least Privilege:**
- Chỉ cho phép những gì **CẦN THIẾT** để làm việc
- Còn lại: Deny ALL

---

### B4. ACL 140: SSH Access Control (5 điểm)

**Vị trí:** Tất cả Routers, VTY lines (virtual terminal)

**Mục tiêu:** Chỉ Admin PC được SSH vào thiết bị mạng

**Logic yêu cầu:**
```
1. PERMIT: Host 10.1.2.50 → Any (TCP 22)
   Lý do: Admin PC duy nhất

2. DENY: ip any any log
```

**Áp dụng:**
- Trên VTY lines (line vty 0 4)
- Keyword: `access-class <ACL> in`

**Bảo mật bổ sung:**
- Disable Telnet: `transport input ssh`
- Require SSH version 2: `ip ssh version 2`

---

## IV. PHẦN C - BẢO MẬT BỔ SUNG (20 điểm)

### C1. OSPF MD5 Authentication (10 điểm)

**Mục tiêu:** Chống route poisoning / man-in-the-middle

**Yêu cầu:**
- [ ] Bật MD5 authentication trên **tất cả** interface chạy OSPF
- [ ] Password: `TechVerse2026!` (hoặc tự đặt password mạnh)
- [ ] Key ID: 1

**on mọi OSPF interface:**
- Interface phải enable `ip ospf authentication message-digest`
- Interface phải có `ip ospf message-digest-key 1 md5 <password>`

**Kiểm tra:**
- Lệnh: `show ip ospf interface | include auth`
- Kết quả mong đợi: "Message digest authentication enabled"

**Tại sao quan trọng?**
- Không có auth: Hacker có thể gửi fake LSAs → poison routing table
- MD5 auth: Packet không có signature đúng → bị drop

---

### C2. Password Security (5 điểm)

**Yêu cầu:**
- [ ] Mã hóa passwords trong config: `service password-encryption`
- [ ] Dùng `enable secret` (MD5 hashed) thay vì `enable password` (clear-text)
- [ ] VTY lines phải có password

**Kiểm tra:**
- Lệnh: `show running-config | include password`
- Không được thấy password dạng clear-text

---

### C3. Logging & Monitoring (5 điểm)

**Yêu cầu:**
- [ ] Enable logging với keyword `log` trong các ACL quan trọng
- [ ] Cấu hình buffer: `logging buffered 16384`
- [ ] Timestamps: `service timestamps log datetime msec`

**Tại sao quan trọng?**
- Khi bị tấn công, cần logs để forensic analysis
- Timestamps giúp correlate events across multiple devices

---

## V. YÊU CẦU TRIỂN KHAI MININET

### Môi trường

**Bắt buộc sử dụng:**
- **Mininet** trên Linux (Ubuntu 20.04+, Kali Linux)
- **FRRouting** (thay thế Quagga để chạy OSPF trên Mininet)
- **iptables** cho ACLs simulation

**KHÔNG được dùng:**
- ❌ GNS3
- ❌ Packet Tracer
- ❌ EVE-NG

**Lý do:** Đảm bảo môi trường test đồng nhất, dễ reproduce bugs

---

### Script yêu cầu

**Tối thiểu:**
1. **topology.py** - Tạo Mininet network với 6 routers
   - Sử dụng `mn.addHost()` để tạo routers
   - Enable IP forwarding: `router.cmd('sysctl -w net.ipv4.ip_forward=1')`

2. **configure_ospf.sh** (hoặc Python) - Script cấu hình OSPF
   - Có thể dùng FRRouting vtysh commands

3. **configure_acls.sh** - Script deploy iptables rules

**Khuyến nghị:**
- Tự động hóa việc tạo topology
- Có thể teardown và rebuild dễ dàng

---

## VI. BÁO CÁO YÊU CẦU

### Cấu trúc báo cáo (PDF)

**Phần 1: Thiết kế (20%)**
- Sơ đồ topology (vẽ tay hoặc dùng draw.io)
- Bảng IP addressing
- Bảng OSPF areas
- Danh sách ACL policies (tóm tắt)

**Phần 2: Triển khai (20%)**
- Mô tả các bước đã làm
- Screenshot Mininet topology
- Quan trọng: GIẢI THÍCH tại sao làm như vậy, không chỉ copy-paste commands

**Phần 3: Kiểm chứng (40%)**
- Kết quả tất cả test cases trong [VERIFICATION.md](./VERIFICATION.md)
- Screenshots + logs minh chứng
- Phân tích nếu có test case fail

**Phần 4: Phân tích & Câu hỏi (20%)**
- Trả lời các câu hỏi lý thuyết (xem phần VII)
- Reflection: Điều gì khó, điều gì học được?

---

## VII. CÂU HỎI LÝ THUYẾT (BẮT BUỘC TRẢ LỜI TRONG BÁO CÁO)

### Câu hỏi 1: OSPF Areas
**Tại sao Area 30 (IoT) phải được cấu hình là Totally Stubby thay vì Standard Area? Phân tích ưu điểm và nhược điểm.**

**Gợi ý trả lời:**
- Ưu điểm: Che giấu topology, giảm routing table, tiết kiệm RAM...
- Nhược điểm: Mất tính linh hoạt routing, phụ thuộc hoàn toàn vào default route...

---

### Câu hỏi 2: ACL Placement
**Trong ACL 110 (IoT Isolation), tại sao phải đặt ở interface IoT với direction IN, thay vì đặt ở interface Management với direction OUT?**

**Gợi ý trả lời:**
- Early filtering tiết kiệm băng thông...
- Dễ troubleshoot ...
- Centralized policy at source...

---

### Câu hỏi 3: Defense in Depth
**Nếu chỉ dùng Totally Stubby Area mà KHÔNG dùng ACLs, hệ thống có an toàn không? Nếu chỉ dùng ACLs mà KHÔNG dùng Totally Stubby, thì sao? Giải thích.**

**Gợi ý trả lời:**
- Totally Stubby: Che topology, nhưng nếu hacker biết IP (hard-coded), vẫn ping được...
- ACL only: Chặn được traffic, nhưng hacker vẫn liệt kê được IP qua routing table...
- Cần CẢ HAI → Defense in Depth

---

### Câu hỏi 4: Wildcard Mask
**Giải thích wildcard mask `0.0.0.255` trong ACL. Tại sao không dùng subnet mask `255.255.255.0`?**

**Gợi ý trả lời:**
- Wildcard mask = inverse of subnet mask...
- 0 = must match exactly, 255 = don't care...
- Dùng sai → ACL match sai hosts

---

## VIII. TIÊU CHÍ CHẤM ĐIỂM CHI TIẾT

| Hạng mục | Điểm | Yêu cầu Pass |
|:---|:---:|:---|
| **A. OSPF Multi-Area** | 40 | Neighbors FULL, Area 30 Totally Stubby đúng |
| - Cấu hình cơ bản | 15 | All routers have correct RID, areas |
| - Tối ưu hóa | 15 | P2P type, priority correct, backup route works |
| - Totally Stubby Area | 10 | R6 chỉ có default route |
| **B. Extended ACLs** | 40 | Pass tất cả test cases trong VERIFICATION.md |
| - ACL 110 (IoT) | 15 | IoT blocked from Internal |
| - ACL 120 (DMZ) | 10 | DMZ blocked from Inside |
| - ACL 130 (Staff) | 10 | Staff blocked from Management |
| - ACL 140 (SSH) | 5 | Only Admin can SSH |
| **C. Bảo mật bổ sung** | 20 | MD5 auth enabled, passwords encrypted |
| - OSPF Auth | 10 | All interfaces have MD5 |
| - Password security | 5 | No clear-text passwords |
| - Logging | 5 | ACL logs + timestamps |

**TOTAL: 100 điểm**

**PASS: ≥ 70 điểm**

---

## IX. DEADLINE & NỘP BÀI

**Hạn nộp:** [Ngày/Tháng/Năm - Giờ]

**Nộp qua:** [Platform - Moodle/Email/etc.]

**Files cần nộp:**
1. `topology.py` - Mininet script
2. `configure_ospf.sh` hoặc `configure_ospf.py`
3. `configure_acls.sh` hoặc `configure_acls.py`
4. `report.pdf` - Báo cáo đầy đủ
5. (Optional) `demo.mp4` - Video demo

**Nộp muộn:** Trừ 10 điểm/ngày (tối đa 3 ngày)

---

> **Lưu ý cuối:**  
> Đây là đồ án khó, yêu cầu tự học và research. Hãy bắt đầu sớm, đừng để đến phút cuối.  
> **Không có lời giải sẵn → Đây là cơ hội để bạn thực sự hiểu, không chỉ copy-paste.**

**Good luck! 🚀**
