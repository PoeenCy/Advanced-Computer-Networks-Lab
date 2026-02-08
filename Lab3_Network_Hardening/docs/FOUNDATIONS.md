# PHÂN TÍCH BÀI BÁO & NỀN TẢNG LÝ THUYẾT

**Từ bảo mật gia đình đến bảo mật doanh nghiệp**

---

## I. NGUỒN THAM KHẢO

**Bài báo chính:** [How to secure your router and home network - PCWorld](https://www.pcworld.com/article/415583/how-to-secure-your-router-and-home-network.html)

Bài báo của PCWorld hướng tới người dùng gia đình (consumer-level security), nhưng các nguyên tắc bảo mật trong đó hoàn toàn có thể áp dụng và **mở rộng** lên quy mô doanh nghiệp. Đồ án này sẽ "dịch" các khái niệm đơn giản sang kỹ thuật mạng chuyên sâu.

---

## II. PHÂN TÍCH CHI TIẾT BÀI BÁO PCWORLD

### 1. Vấn đề: Tại sao Router gia đình dễ bị tấn công?

**Theo PCWorld, các nguy cơ chính:**

#### 🔴 Nguy cơ 1: Mật khẩu yếu và mặc định
- **Mô tả:** Router xuất xưởng với password mặc định (admin/admin, admin/password)
- **Hậu quả:** Hacker dễ dàng truy cập vào trang quản trị
-  **Thống kê:** 61% người dùng không bao giờ đổi password router (theo PCWorld)

**👉 Áp dụng lên Doanh nghiệp:**
- Thiết bị mạng (Router, Switch) phải có password phức tạp
- Sử dụng **AAA (Authentication, Authorization, Accounting)**
- Enable **SSH với key-based authentication**, disable Telnet

#### 🔴 Nguy cơ 2: Firmware lỗi thời
- **Mô tả:** Router chạy phần mềm cũ, có lỗ hổng bảo mật đã biết
- **Hậu quả:** Botnet như Mirai có thể chiếm quyền điều khiển

**👉 Áp dụng lên Doanh nghiệp:**
- Thường xuyên update IOS/firmware
- Subscribe vào Cisco Security Advisories
- Triển khai patch management process

#### 🔴 Nguy cơ 3: Tất cả thiết bị nằm chung mạng (Flat Network)
- **Mô tả:** Smart TV, IoT camera, laptop cùng chung một mạng LAN
- **Hậu quả:** Nếu camera bị hack, hacker có thể nhảy sang laptop

**Minh họa từ PCWorld:**
```
❌ MÔ HÌNH KHÔNG AN TOÀN (Flat Network):
┌─────────────────────────────────────┐
│         Home Router/WiFi            │
│  ┌───────┬─────────┬────────────┐  │
│  │ Laptop│ Smart TV│ IoT Camera │  │
│  └───────┴─────────┴────────────┘  │
└─────────────────────────────────────┘
→ Camera bị hack → Hacker có thể scan và tấn công Laptop
```

**👉 Áp dụng lên Doanh nghiệp - OSPF Multi-Area:**

PCWorld khuyên dùng "Guest Network" để cô lập thiết bị. Trong doanh nghiệp, chúng ta **nâng cấp** khái niệm này thành **OSPF Multi-Area**:

```
✅ MÔ HÌNH AN TOÀN (OSPF Multi-Area):

Area 0 (Backbone) - Mạng lõi tin cậy
    ├─ Area 10 (HQ) - Nhân viên & Quản lý
    ├─ Area 20 (DMZ) - Dịch vụ công khai
    └─ Area 30 (IoT - TOTALLY STUBBY) - Thiết bị kém bảo mật
```

**Lợi ích của Multi-Area so với Flat Network:**

| Đặc điểm | Flat Network | OSPF Multi-Area |
|:---|:---|:---|
| **Routing Table Size** | Lớn (tất cả routes) | Nhỏ (nhờ summarization) | 
| **Failure Domain** | Toàn bộ mạng ảnh hưởng | Chỉ Area đó bị ảnh hưởng |
| **Security** | Không cô lập | Có thể kết hợp với ACL |
| **Che giấu topology** | Không | Stub Area ẩn chi tiết mạng |

**TẠI SAO DÙNG TOTALLY STUBBY AREA CHO IOT?**

Khi Area 30 (IoT) được cấu hình là **Totally Stubby**:
- Router IoT (R6) **chỉ nhận** một default route `0.0.0.0/0` từ ABR
- R6 **KHÔNG BIẾT** chi tiết về:
  - Subnet nào tồn tại trong Area 10 (HQ)
  - Subnet nào tồn tại trong Area 20 (DMZ)
  - Địa chỉ IP của các server quan trọng

**Hậu quả với Hacker:**
- Ngay cả khi hacker chiếm quyền điều khiển router R6
- Họ không thể liệt kê được danh sách target trong mạng
- **"Nếu không biết target IP, không thể tấn công"**

---

#### 🔴 Nguy cơ 4: Không có Firewall/Packet Filtering
- **Mô tả:** Router chỉ làm nhiệm vụ định tuyến, không kiểm tra nội dung gói tin
- **Hậu quả:** Malware lan truyền tự do giữa các thiết bị

**👉 Áp dụng lên Doanh nghiệp - Extended ACLs:**

PCWorld khuyên bật "Firewall" trên router. Trong Cisco, chúng ta dùng **Extended ACLs** để:

**So sánh Standard ACL vs Extended ACL:**

| Đặc điểm | Standard ACL (1-99, 1300-1999) | Extended ACL (100-199, 2000-2699) |
|:---|:---|:---|
| **Lọc theo** | Source IP only | Source + Dest IP + Protocol + Port |
| **Sử dụng** | Đơn giản, phạm vi nhỏ | Phức tạp, chi tiết |
| **Ví dụ** | `access-list 10 deny 192.168.1.0 0.0.0.255` | `access-list 110 deny tcp 192.168.1.0 0.0.0.255 10.1.1.0 0.0.0.255 eq 445` |
| **Đặt ở đâu** | Gần đích (destination) | Gần nguồn (source) |

**NGUYÊN TẮC ĐẶT ACL:**
- Standard ACL: Đặt **gần đích** (để không chặn traffic hợp lệ đến nơi khác)
- Extended ACL: Đặt **gần nguồn** (để chặn sớm, tiết kiệm băng thông)

**Ví dụ ACL chặn IoT truy cập Management:**
```cisco
! Extended ACL - Đặt trên Router R6 (IoT) - Interface IoT, direction IN
access-list 110 remark === Protect Management Zone ===
access-list 110 deny ip 192.168.100.0 0.0.0.255 10.1.2.0 0.0.0.255 log
access-list 110 permit ip any any

interface eth2
 ip access-group 110 in
```

**Giải thích:**
- Chặn **SỚM nhất** ngay khi traffic rời khỏi IoT zone
- Không cần chờ đến khi packet đến Management zone mới chặn
- Keyword `log` giúp phát hiện attempt tấn công

---

#### 🔴 Nguy cơ 5: Dịch vụ công khai đặt trong mạng nội bộ
- **Mô tả:** Web server, Email server cùng mạng với PC cá nhân
- **Hậu quả:** Khi server bị hack, toàn bộ mạng nội bộ lộ

**Ví dụ thực tế:** Vụ tấn công Equifax (2017)
- Hacker khai thác lỗ hổng trên web server
- Từ web server, nhảy vào database server (cùng mạng)
- Đánh cắp 147 triệu hồ sơ cá nhân

**👉 Áp dụng lên Doanh nghiệp - DMZ (Demilitarized Zone):**

**Khái niệm DMZ:**
- Vùng đệm giữa Internet (Outside) và Mạng nội bộ (Inside)
- Đặt các dịch vụ công khai (Web, Email, DNS) trong DMZ
- Áp dụng ACL nghiêm ngặt:
  - **Internet → DMZ**: CHO PHÉP (HTTP/HTTPS, SMTP)
  - **DMZ → Inside**: CHẶN (trừ các dịch vụ cần thiết)
  - **Inside → DMZ**: CHO PHÉP có điều kiện

**Sơ đồ kiến trúc DMZ:**
```
Internet (Untrusted)
     ↓
     ACL: Permit 80/443 to DMZ only
     ↓
┌────────────────┐
│   DMZ Zone     │  172.16.10.0/24
│  Web  │ Email  │
└────────────────┘
     ↓
     ACL: Deny DMZ → Inside (except specific services)
     ↓
┌────────────────┐
│  Inside Zone   │  10.1.x.0/24
│ Staff │ Mgmt   │
└────────────────┘
```

**Chính sách ACL cho DMZ:**

1. **Trên Router biên (R5) - Interface DMZ, direction IN:**
```cisco
access-list 120 remark === DMZ to Inside Policy ===

! Cho phép DMZ Query DNS internal
access-list 120 permit udp 172.16.10.0 0.0.0.255 10.1.2.10 eq 53

! Cho phép DMZ backup data đến backup server (chỉ port 22)
access-list 120 permit tcp host 172.16.10.100 host 10.1.2.20 eq 22

! CHẶN mọi connection khác từ DMZ vào Inside
access-list 120 deny ip 172.16.10.0 0.0.0.255 10.1.0.0 0.0.255.255 log

! Cho phép traffic khác (đi Internet, đi IoT if needed)
access-list 120 permit ip any any
```

**Lý do tại sao cần chặn DMZ → Inside:**
- Nếu Web server trong DMZ bị chiếm quyền
- Hacker không thể nhảy sang mạng nội bộ được
- **Nguyên tắc Least Privilege**: Chỉ cho phép những gì cần thiết

---

## III. BẢNG TỔNG HỢP: TỪ PCWORLD ĐẾN DOANH NGHIỆP

| Mục tiêu Bảo mật | Giải pháp PCWorld (Gia đình) | Giải pháp Đồ án (Doanh nghiệp) | Công nghệ Cisco |
|:---|:---|:---|:---|
| **Cô lập thiết bị nguy hiểm** | Tạo Guest WiFi network | OSPF Totally Stubby Area | `area 30 stub no-summary` |
| **Bảo vệ dịch vụ công khai** | Enable DMZ port trên router SOHO | DMZ Zone với ACL nghiêm ngặt | Extended ACL 120 |
| **Chống malware lan truyền** | Bật Firewall cơ bản | Extended ACLs theo từng zone | ACL 110 (IoT), 130 (Staff) |
| **Đổi password mặc định** | Đặt password WiFi phức tạp | OSPF MD5 Authentication | `ip ospf message-digest-key 1 md5 <pass>` |
| **Giới hạn quản trị** | Tắt WAN management | SSH ACL (chỉ Admin PC) | `line vty 0 4` + ACL 140 |
| **Tối ưu định tuyến** | Không có (SOHO dùng static) | OSPF với cost, backup routes | `ip ospf cost 500` |

---

## IV. MÔ HÌNH 3 LỚP - TẠI SAO CẦN?

PCWorld không đề cập đến kiến trúc mạng phân tầng vì đây là khái niệm doanh nghiệp. Nhưng **3-layer model** là nền tảng thiết kế mạng chuẩn công nghiệp.

### Tại sao không dùng 1 router khổng lồ cho toàn bộ mạng?

**Vấn đề của Single-Router Design:**
- Quá tải xử lý (routing decisions, ACL processing, NAT)
- Single point of failure
- Khó mở rộng (scalability)
- Khó quản lý security policies

**Giải pháp: Hierarchical Design (3 lớp)**

```
┌─────────────────────────────────────┐
│     CORE LAYER (Lớp Xương sống)    │
│   Nhiệm vụ: High-speed switching    │
│   Không nên: ACLs phức tạp          │
│   R1 ────── R2 ────── R3            │
└─────────────┬───────────────────────┘
              │
┌─────────────┴───────────────────────┐
│  DISTRIBUTION LAYER (Lớp Phân phối) │
│   Nhiệm vụ: Route between VLANs     │
│            Apply ACLs, QoS          │
│            Summarization            │
│   R4 (HQ)  R5 (DMZ)  R6 (IoT)       │
└─────────────┬───────────────────────┘
              │
┌─────────────┴───────────────────────┐
│    ACCESS LAYER (Lớp Truy cập)      │
│   Nhiệm vụ: Connect end devices     │
│            Port security            │
│   SW1 ── SW2 ── SW3                 │
│   │      │      │                   │
│  PCs  Servers  IoT                  │
└─────────────────────────────────────┘
```

**Phân chia trách nhiệm:**

| Layer | Nhiệm vụ chính | KHÔNG nên làm |
|:---|:---|:---|
| **Core** | Chuyển tiếp traffic nhanh, OSPF backbone | ACL phức tạp, NAT (tốn CPU) |
| **Distribution** | Route summarization, ACLs, QoS, Inter-VLAN routing | Kết nối trực tiếp end-users |
| **Access** | Kết nối hosts, port security, VLAN assignment | Routing phức tạp |

**Áp dụng vào đồ án:**
- Area 0 (R1, R2, R3) = **Core Layer**
- Area 10, 20, 30 (R4, R5, R6) = **Distribution Layer**
- Switches (SW1, SW2, SW3) = **Access Layer**

---

## V. ZERO TRUST MODEL - TRIẾT LÝ BẢO MẬT

PCWorld nhấn mạnh: **"Đừng tin tưởng mù quáng các thiết bị trong mạng"**

**Zero Trust = "Never Trust, Always Verify"**

### So sánh Perimeter Security vs Zero Trust

| Aspect | Perimeter Security (Cũ) | Zero Trust (Mới) |
|:---|:---|:---|
| **Triết lý** | "Bên trong tường lửa = An toàn" | "Không tin ai, kể cả bên trong" |
| **Ví dụ** | Một khi vào mạng WiFi công ty, truy cập tự do | Mọi request đều phải xác thực |
| **Áp dụng** | DMZ biên, firewall edge | Micro-segmentation, ACL mọi nơi |
| **Nhược điểm** | Lateral movement dễ dàng | Phức tạp để triển khai |

### Áp dụng Zero Trust trong đồ án

1. **Cô lập Host-to-Host trong cùng VLAN:**
   - Ngay cả 2 PC trong cùng VLAN Staff không nên ping nhau
   - Sử dụng Private VLAN hoặc ACL on switches

2. **Whitelist thay vì Blacklist:**
   - ❌ Sai: "Chặn IoT đến Management, còn lại cho phép"
   - ✅ Đúng: "Chỉ cho phép IoT đến Internet (8.8.8.8), còn lại chặn hết"

3. **Least Privilege:**
   - Staff chỉ được HTTPS đến DMZ (không được HTTP, SSH, RDP...)
   - Admin chỉ được SSH từ 1 IP cụ thể, không phải cả subnet

---

## VI. KẾT LUẬN: DEFENSE IN DEPTH

**Bài học lớn nhất từ PCWorld:** Không có giải pháp bảo mật nào là hoàn hảo 100%.

**Defense in Depth = Nhiều lớp phòng thủ chồng lên nhau:**

```
Attacker phải vượt qua TẤT CẢ các lớp này:

1️⃣ OSPF Totally Stubby Area  → Không biết target IP
2️⃣ Extended ACL (Source IP)  → Bị chặn theo nguồn
3️⃣ Extended ACL (Dest IP)    → Bị chặn theo đích
4️⃣ Extended ACL (Port)       → Bị chặn theo service
5️⃣ MD5 Authentication        → Không giả mạo được routing
6️⃣ SSH với keypair           → Không đoán được password

→ Nếu 1 lớp thất bại, còn 5 lớp khác bảo vệ
```

**Câu hỏi để suy ngẫm:**
1. Nếu một camera IoT bị nhiễm malware, nó có thể làm gì với mạng của bạn?
2. Nếu web server trong DMZ bị hack, làm thế nào để ngăn hacker nhảy vào database server?
3. Tại sao cần cả OSPF Stub Area VÀ ACLs? Một cái thôi có đủ không?

**Trả lời:**
1. Với Totally Stubby + ACL: Nó chỉ ping được `0.0.0.0/0`, không biết IP của server nào
2. Với DMZ ACL: Chặn traffic từ DMZ subnet vào Inside subnet
3. Không đủ! OSPF Stub che giấu topology, ACL kiểm soát traffic - **hai mục đích khác nhau**

---

**Hãy đọc kỹ phần này trước khi thiết kế. Hiểu TẠI SAO quan trọng hơn biết LÀM THẾ NÀO.**
