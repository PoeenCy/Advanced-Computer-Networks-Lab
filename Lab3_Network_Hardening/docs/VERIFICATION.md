# TIÊU CHÍ NGHIỆM THU & KIỂM CHỨNG

**Cách kiểm tra và đánh giá kết quả**

---

## I. TỔNG QUAN

Phần này liệt kê **TẤT CẢ** các test cases sinh viên cần thực hiện để chứng minh hệ thống hoạt động đúng.

**Quy tắc:**
- ✅ = Kết quả mong đợi: SUCCESS
- ❌ = Kết quả mong đợi: BLOCKED/FAILED
- Mỗi test case phải có screenshot hoặc log minh chứng trong báo cáo

---

## II. PHẦN 1: KIỂM TRA KẾT NỐI HỢP LỆ (20 điểm)

**Mục tiêu:** Chứng minh các kết nối hợp lệ KHÔNG bị chặn

### TC-001: Staff truy cập DMZ Web Server (HTTPS)
**Nguồn:** Employee PC1 (`10.1.1.10`)  
**Đích:** Web Server (`172.16.10.100:443`)  
**Kết quả mong đợi:** ✅ **SUCCESS**

**Lệnh test:**
```bash
# Từ Employee PC1
curl -k https://172.16.10.100

# Hoặc nếu có web server thực
wget --no-check-certificate https://172.16.10.100
```

**Minh chứng cần có:**
- Output thành công (HTTP 200, hoặc HTML content)
- Hoặc tcpdump showing TCP 3-way handshake complete

**Điểm:** 5 điểm

---

### TC-002: Admin PC SSH vào Router R1
**Nguồn:** Admin PC (`10.1.2.50`)  
**Đích:** R1 Management IP (`10.0.0.1:22`)  
**Kết quả mong đợi:** ✅ **SUCCESS**

**Lệnh test:**
```bash
# Từ Admin PC
ssh admin@10.0.0.1
```

**Minh chứng cần có:**
- SSH login prompt hiện ra
- Hoặc thành công đăng nhập vào VTY

**Điểm:** 5 điểm

---

### TC-003: IoT gửi Syslog đến Syslog Server
**Nguồn:** IoT Camera (`192.168.100.10`)  
**Đích:** Syslog Server (`172.16.10.200:514/UDP`)  
**Kết quả mong đợi:** ✅ **SUCCESS**

**Lệnh test:**
```bash
# Từ IoT Camera
logger -n 172.16.10.200 -P 514 "Test syslog from IoT"

# Trên Syslog Server, check logs
tail -f /var/log/syslog | grep "Test syslog"
```

**Minh chứng cần có:**
- Log message xuất hiện trên Syslog Server

**Điểm:** 5 điểm

---

### TC-004: IoT ping ra Internet
**Nguồn:** IoT Camera (`192.168.100.10`)  
**Đích:** Internet (`8.8.8.8`)  
**Kết quả mong đợi:** ✅ **SUCCESS**

**Lệnh test:**
```bash
# Từ IoT Camera
ping -c 4 8.8.8.8
```

**Minh chứng cần có:**
- Ping replies nhận được (0% packet loss hoặc < 10%)

**Điểm:** 5 điểm

---

## III. PHẦN 2: KIỂM TRA BẢO MẬT (40 điểm)

**Mục tiêu:** Chứng minh ACLs chặn đúng traffic độc hại

### TC-005: IoT KHÔNG ping được Staff Zone
**Nguồn:** IoT Camera (`192.168.100.10`)  
**Đích:** Employee PC1 (`10.1.1.10`)  
**Kết quả mong đợi:** ❌ **BLOCKED by ACL 110**

**Lệnh test:**
```bash
# Từ IoT Camera
ping -c 4 10.1.1.10
```

**Kết quả chấp nhận:**
- 100% packet loss
- Hoặc "Destination Host Unreachable"
- Hoặc timeout

**Minh chứng cần có:**
- Screenshot ping failed
- Log entry từ ACL (nếu có keyword `log`)

**Điểm:** 5 điểm

---

### TC-006: IoT KHÔNG ping được Management Zone
**Nguồn:** IoT Camera (`192.168.100.10`)  
**Đích:** File Server (`10.1.2.100`)  
**Kết quả mong đợi:** ❌ **BLOCKED by ACL 110**

**Lệnh test:**
```bash
# Từ IoT Camera
ping -c 4 10.1.2.100
```

**Kết quả chấp nhận:** 100% packet loss

**Điểm:** 10 điểm (vì đây là test case QUAN TRỌNG NHẤT!)

---

### TC-007: IoT KHÔNG truy cập được DMZ (ngoại trừ Syslog)
**Nguồn:** IoT Camera (`192.168.100.10`)  
**Đích:** Web Server (`172.16.10.100:80`)  
**Kết quả mong đợi:** ❌ **BLOCKED by ACL 110**

**Lệnh test:**
```bash
# Từ IoT Camera
curl http://172.16.10.100
# Hoặc
telnet 172.16.10.100 80
```

**Kết quả chấp nhận:** Connection refused hoặc timeout

**Điểm:** 5 điểm

---

### TC-008: Staff KHÔNG truy cập được Management Zone
**Nguồn:** Employee PC1 (`10.1.1.10`)  
**Đích:** File Server (`10.1.2.100`)  
**Kết quả mong đợi:** ❌ **BLOCKED by ACL 130**

**Lệnh test:**
```bash
# Từ Employee PC1
ping -c 4 10.1.2.100

# Hoặc thử SMB share (nếu có)
smbclient //10.1.2.100/HR
```

**Kết quả chấp nhận:** Ping timeout, SMB connection refused

**Điểm:** 10 điểm

---

### TC-009: Staff PC KHÔNG SSH được vào Router
**Nguồn:** Employee PC1 (`10.1.1.10`)  
**Đích:** R1 (`10.0.0.1:22`)  
**Kết quả mong đợi:** ❌ **BLOCKED by ACL 140 (VTY ACL)**

**Lệnh test:**
```bash
# Từ Employee PC1
ssh admin@10.0.0.1
```

**Kết quả chấp nhận:** "Connection refused" hoặc "Permission denied"

**Điểm:** 5 điểm

---

### TC-010: DMZ Web Server KHÔNG truy cập được vào Inside
**Nguồn:** Web Server (`172.16.10.100`)  
**Đích:** File Server (`10.1.2.100`)  
**Kết quả mong đợi:** ❌ **BLOCKED by ACL 120**

**Lệnh test:**
```bash
# Từ Web Server (giả sử bị hack)
ping -c 4 10.1.2.100

# Hoặc thử scan
nmap -p 445 10.1.2.100
```

**Kết quả chấp nhận:** Ping timeout, nmap shows "filtered" hoặc no response

**Điểm:** 5 điểm

---

## IV. PHẦN 3: KIỂM TRA OSPF (20 điểm)

**Mục tiêu:** Chứng minh OSPF hoạt động đúng

### TC-011: Totally Stubby Area - R6 chỉ có default route
**Router:** R6 (IoT Router)  
**Lệnh test:**
```bash
R6# show ip route
```

**Kết quả mong đợi:**
- Chỉ hiển thị `O*IA 0.0.0.0/0 [110/X] via ...` (default route)
- KHÔNG hiển thị route cụ thể đến:
  - `10.1.1.0/24` (Staff)
  - `10.1.2.0/24` (Management)
  - `172.16.10.0/24` (DMZ)

**Minh chứng cần có:**
- Screenshot `show ip route` output

**Điểm:** 10 điểm

---

### TC-012: OSPF Neighbors đều ở trạng thái FULL
**Router:** Tất cả routers  
**Lệnh test:**
```bash
R1# show ip ospf neighbor
R2# show ip ospf neighbor
...
R6# show ip ospf neighbor
```

**Kết quả mong đợi:**
- Tất cả neighbors hiển thị `State: FULL/DR`, `FULL/BDR`, hoặc `FULL/-` (P2P)
- KHÔNG có neighbor ở trạng thái `INIT`, `EXSTART`, `2-WAY` (trừ non-DR/BDR trên multi-access)

**Minh chứng cần có:**
- Screenshot từ ít nhất 3 routers (R1, R2, R6)

**Điểm:** 5 điểm

---

### TC-013: OSPF MD5 Authentication đang hoạt động
**Router:** Bất kỳ router nào  
**Lệnh test:**
```bash
R1# show ip ospf interface | include auth
```

**Kết quả mong đợi:**
- Mọi interface OSPF hiển thị: "Message digest authentication enabled"

**Hoặc test negative:**
- Tạm tắt auth trên 1 interface → Neighbor phải down
- Bật lại → Neighbor lên FULL trở lại

**Minh chứng cần có:**
- Screenshot `show ip ospf interface`

**Điểm:** 5 điểm

---

## V. PHẦN 4: KIỂM TRA FAILOVER (10 điểm)

**Mục tiêu:** Chứng minh backup route hoạt động

### TC-014: Failover khi R5 down
**Kịch bản:**
1. Ban đầu: Traffic từ R2 đến R6 đi qua R5 (main path)
2. Shutdown interface R5→R6
3. Kiểm tra: Traffic tự động chuyển sang R2→R6 trực tiếp (backup path)
4. Khôi phục R5→R6
5. Kiểm tra: Traffic trở lại đi qua R5

**Lệnh test:**
```bash
# Bước 1: Kiểm tra route ban đầu
R6# show ip route 10.0.0.0

# Bước 2: Shutdown link R5→R6
R5# configure terminal
R5(config)# interface eth1
R5(config-if)# shutdown

# Bước 3: Chờ OSPF re-converge (30 giây)
R6# show ip route 10.0.0.0
# Phải thấy next-hop là 10.20.26.1 (R2) thay vì 10.30.56.1 (R5)

# Bước  4: Khôi phục
R5(config-if)# no shutdown

# Bước 5: Route trở lại qua R5
R6# show ip route 10.0.0.0
```

**Minh chứng cần có:**
- Screenshot route table TRƯỚC và SAU khi shutdown R5
- Hoặc traceroute output showing path change

**Điểm:** 10 điểm

---

## VI. PHẦN 5: BÁO CÁO & PHÂN TÍCH (10 điểm)

**Yêu cầu báo cáo:**

### 1. Tóm tắt kết quả test (4 điểm)
Tạo bảng tổng hợp:

| Test Case | Kết quả | Pass/Fail | Note |
|:---|:---:|:---:|:---|
| TC-001 | ✅ Success | Pass | Staff can access DMZ |
| TC-002 | ✅ Success | Pass | Admin can SSH |
| ... | ... | ... | ... |
| TC-014 | ✅ Failover OK | Pass | Backup route works |

**Pass rate mong đợi:** ≥ 90% (ít nhất 13/14 test cases pass)

---

### 2. Phân tích kỹ thuật (3 điểm)
**Trả lời:**
1. Test case nào failed? Tại sao?
2. Có phát hiện issue/bug nào không?
3. Hệ thống có bottleneck nào không? (performance)

---

### 3. Bài học & Cải tiến (3 điểm)
**Trả lời:**
1. Điều gì khó nhất trong quá trình triển khai?
2. Nếu làm lại, bạn sẽ thay đổi gì?
3. Trong thực tế, cần thêm biện pháp bảo mật nào? (ví dụ: IDS/IPS, WAF, DLP...)

---

## VII. CHECKLIST NGHIỆM THU CUỐI CÙNG

Trước khi nộp bài, kiểm tra:

### OSPF
- [ ] Tất cả neighbors đều FULL
- [ ] R6 chỉ có default route
- [ ] MD5 authentication enable trên tất cả interface
- [ ] Backup route hoạt động (test failover)

### ACLs
- [ ] IoT KHÔNG ping được Management/Staff (TC-005, TC-006) ← **CRITICAL**
- [ ] Staff KHÔNG ping được Management (TC-008) ← **CRITICAL**
- [ ] DMZ KHÔNG ping được Inside (TC-010) ← **CRITICAL**
- [ ] SSH chỉ từ Admin PC (TC-009)

### Báo cáo
- [ ] Có đầy đủ screenshots cho tất cả test cases
- [ ] Có phân tích chi tiết (không chỉ screenshot)
- [ ] Trả lời đầy đủ 4 câu hỏi lý thuyết trong REQUIREMENTS.md

### Source code
- [ ] Mininet topology chạy được
- [ ] Configuration scripts clear, có comment
- [ ] README hướng dẫn cách chạy

---

## VIII. COMMON MISTAKES (Lỗi thường gặp)

### Lỗi 1: ACL không hoạt động
**Triệu chứng:** Ping từ IoT vẫn đến được Management

**Nguyên nhân thường gặp:**
- Quên `apply` ACL lên interface: `ip access-group <ACL> in`
- Wildcard mask sai (dùng subnet mask thay vì wildcard)
- Đặt ACL sai hướng (IN vs OUT)
- Thứ tự rules sai (DENY đặt sau PERMIT any any)

**Cách debug:**
```bash
# Kiểm tra ACL có applied chưa
R6# show ip interface eth2 | include access list

# Xem ACL hit count
R6# show access-lists 110
Extended IP access list 110
    10 deny ip 192.168.100.0 0.0.0.255 10.1.2.0 0.0.0.255 log (0 matches) ← Nếu 0 matches → ACL không match!
```

---

### Lỗi 2: OSPF neighbor không lên FULL
**Nguyên nhân thường gặp:**
- Sai Area ID
- Sai MD5 password
- MTU mismatch
- Network type mismatch

**Cách debug:**
```bash
# Check neighbor state
R1# show ip ospf neighbor

# Debug (cẩn thận, nhiều output!)
R1# debug ip ospf adj
```

---

### Lỗi 3: Totally Stubby Area không hoạt động
**Triệu chứng:** R6 vẫn thấy route cụ thể đến Area 10

**Nguyên nhân:**
- Thiếu `no-summary` keyword trên ABR
- Chưa clear OSPF process sau khi config

**Giải pháp:**
```bash
R2# clear ip ospf process
# Nhập "yes" để confirm
```

---

## IX. ACCEPTANCE CRITERIA (Tiêu chí chấp nhận)

**Dự án được chấp nhận (PASS) khi:**

| Tiêu chí | Yêu cầu tối thiểu |
|:---|:---|
| **Test Cases** | ≥ 90% pass (13/14) |
| **Critical ACLs** | 100% pass (TC-006, TC-008, TC-010) |
| **OSPF** | All neighbors FULL, Stubby Area correct |
| **Báo cáo** | Đầy đủ screenshots + phân tích |
| **Code** | Run được, có README |

**Dự án FAIL nếu:**
- Critical test cases (TC-006, TC-008, TC-010) fail
- OSPF neighbors không lên FULL
- Báo cáo thiếu minh chứng

---

## X. SUBMISSION FORMAT

**Cấu trúc thư mục nộp bài:**

```
StudentID_Lab3_Submission/
├── code/
│   ├── topology.py
│   ├── configure_ospf.sh
│   ├── configure_acls.sh
│   └── README.md (hướng dẫn chạy)
├── report/
│   ├── Lab3_Report_StudentID.pdf
│   └── screenshots/
│       ├── TC-001_staff_to_dmz.png
│       ├── TC-006_iot_blocked.png
│       └── ...
└── demo/ (optional)
    └── demo_video.mp4
```

**Nén thành:** `StudentID_Lab3.zip`

---

**Chúc các bạn test thành công! 🎯**

> *"Testing shows the presence, not the absence of bugs."* — Edsger W. Dijkstra  
> Hãy test kỹ, đừng bỏ sót test case nào!
