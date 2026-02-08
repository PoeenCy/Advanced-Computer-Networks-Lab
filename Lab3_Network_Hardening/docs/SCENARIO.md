# BỐI CẢNH & KỊCH BẢN

**Tình huống thực tế cần giải quyết**

---

## I. GIỚI THIỆU TỔ CHỨC

### 🏢 Tập đoàn Công nghệ TechVerse

**TechVerse Corporation** là một tập đoàn công nghệ đa quốc gia chuyên về phát triển giải pháp Smart City và IoT. Công ty có trụ sở chính tại Việt Nam với 3 cơ sở:

---

## II. CÁC CAMPUS VÀ CHỨC NĂNG

### Campus 1: Trụ sở chính (Headquarters - HQ)

**Vị trí:** Khu công nghệ cao, TP.HCM  
**Mạng:** Area 10 - OSPF Standard Area  
**Subnet:** `10.1.x.0/24`

#### Tòa nhà A - **Khu vực Điều hành & Quản lý**
- **Phòng Giám đốc:** Văn phòng Ban lãnh đạo
- **Phòng Kế toán - Tài chính:**  
  - File server chứa database bảng lương nhân viên (`salary.db`)
  - Hệ thống ERP nội bộ
  - Dữ liệu tài chính nhạy cảm
- **Phòng Nhân sự:**
  - Hồ sơ nhân viên, hợp đồng lao động
  - Privacy data theo GDPR/PDPA

**Mức độ bảo mật:** 🔴 **CRITICAL** → Phải cách ly hoàn toàn khỏi vùng nguy hiểm

**VLAN Assignment:**
- VLAN 12 (Management): `10.1.2.0/24` - Quản lý & Kế toán
- Admin PC: `10.1.2.50`  
- File Server: `10.1.2.100`

#### Tòa nhà B - **Khu vực Làm việc Chung**
- **Phòng R&D:** Phát triển sản phẩm Smart Home
- **Phòng Marketing:** Content creation, social media
- **Phòng IT Support:** Helpdesk, infrastructure

**Mức độ bảo mật:** 🟡 **MEDIUM**

**VLAN Assignment:**
- VLAN 11 (Staff): `10.1.1.0/24` - Nhân viên thông thường
- Employees PCs: `10.1.1.x`

---

### Campus 2: Trung tâm Dữ liệu & Dịch vụ (Data Center & Services)

**Vị trí:** Tòa nhà C - Khu vực khác, có kết nối Internet công cộng  
**Mạng:** Area 20 - OSPF Standard Area  
**Subnet:** `172.16.10.0/24` (DMZ) + `10.20.x.0/24` (Internal services)

#### DMZ Zone (Demilitarized Zone)
Chứa các dịch vụ hướng ra công cộng:

**1. Web Server (`172.16.10.100`)**
- Website công ty: https://techverse.com
- API Gateway cho Mobile App
- Cổng: HTTP (80), HTTPS (443)
- **Nguy cơ:** Target chính của hacker, thường bị scan/exploit

**2. Email Server (`172.16.10.101`)**
- Mail server công ty: mail.techverse.com
- Cổng: SMTP (25), IMAP (143), SMTP over TLS (587)
- **Nguy cơ:** Phishing, spam relay

**3. Syslog Server (`172.16.10.200`)**
- Thu thập logs từ tất cả thiết bị
- Chỉ nhận UDP 514 (Syslog)

**Mức độ bảo mật:** 🟠 **PUBLIC-FACING** → Phải chặn DMZ truy cập Inside

---

### Campus 3: Nhà máy Sản xuất & IoT Zone (Manufacturing & IoT)

**Vị trí:** Khu công nghiệp, cách xa trụ sở  
**Mạng:** Area 30 - **OSPF Totally Stubby Area** (quan trọng!)  
**Subnet:** `192.168.100.0/24`

#### Thiết bị IoT triển khai

**1. Hệ thống Camera giám sát (IP Cameras)**
- 20 camera giám sát an ninh
- Firmware: `v2.3 (2019)` ← **LỖI THỜI**, có lỗ hổng CVE-2019-xxxx
- **Nguy cơ:** Dễ bị Botnet chiếm quyền (như Mirai)

**2. Cảm biến môi trường (Environmental Sensors)**
- Nhiệt độ, độ ẩm, áp suất
- Giao thức: MQTT, HTTP API
- **Nguy cơ:** Không có authentication

**3. Hệ thống điều khiển sản xuất (SCADA/PLC)**
- Điều khiển băng chuyền, robot
- **Nguy cơ:** Nếu bị hack, ảnh hưởng sản xuất

**Mức độ bảo mật:** 🔴 **UNTRUSTED** → Phải cách ly khỏi mọi mạng nội bộ

**Đặc điểm đặc biệt của IoT Zone:**
- Thiết bị không thể update firmware thường xuyên (downtime production)
- Vendor không còn support (End-of-Life products)
- Sử dụng giao thức cũ, không mã hóa
- **→ KHÔNG THỂ TRUST được, phải CÔ LẬP hoàn toàn**

---

## III. SỰ KIỆN KÍCH HOẠT (TRIGGER EVENT)

### 📅 Ngày 15 tháng 1 năm 2026 - 08:30 AM

**Phản hồi từ Security Operations Center (SOC):**

```
───────────────────────────────────────────────────
🚨 SECURITY ALERT - PRIORITY: HIGH
───────────────────────────────────────────────────
Thời gian: 2026-01-15 08:27:03 
Nguồn: IDS (Intrusion Detection System)

⚠️  PHÁT HIỆN HOẠT ĐỘNG BẤT THƯỜNG:

[1] Network Scanning detected:
    Source IP: 192.168.100.15 (Camera-Warehouse-C15)
    Target Range: 10.1.2.0/24 (Management VLAN)
    Ports scanned: 22, 80, 445, 3389, 5900
    Packets sent: 1,247 probes in 3 minutes

[2] Unusual outbound connections:
    Source: 192.168.100.15
    Dest: 185.XXX.XXX.XXX (Russia - Known C&C server)
    Protocol: TCP/8443
    Status: ESTABLISHED

[3] File access attempts (FAILED):
    Source: 192.168.100.15
    Target: \\10.1.2.100\HR\salary.db
    Result: Access Denied (Firewall blocked)
───────────────────────────────────────────────────
```

### 🔍 Phân tích Ban đầu (Initial Triage)

**Phát hiện:**
1. Camera IP `192.168.100.15` đã bị nhiễm malware
2. Malware đang cố gắng **scan** mạng nội bộ để tìm target
3. Đã thiết lập kết nối đến **Command & Control server** ở nước ngoài
4. Cố gắng truy cập file nhạy cảm `salary.db` trên File Server

**May mắn:** Hiện tại hệ thống có firewall cơ bản, đã chặn được truy cập  
**Nguy hiểm:** Nếu không có firewall? → Attacker đã đánh cắp được database

---

## IV. CUỘC HỌP KHẨN CẤP

### 💼 Cuộc họp Ban lãnh đạo - 10:00 AM cùng ngày

**Thành phần:**
- Giám đốc Công nghệ (CTO)
- Giám đốc An ninh Thông tin (CISO)
- Trưởng phòng IT
- Trưởng phòng Vận hành Nhà máy

**Nội dung cuộc họp:**

**CISO phát biểu:**
> *"Chúng ta đã may mắn lần này. Nhưng hệ thống hiện tại có nhiều điểm yếu:*
> 
> 1. *Mạng IoT và mạng văn phòng **KHÔNG** được cách ly đúng cách*
> 2. *Camera biết quá nhiều về cấu trúc mạng nội bộ (do routing table đầy đủ)*
> 3. *Chúng ta chỉ có firewall ở biên, không có micro-segmentation*
> 4. *Nguy cơ **Lateral Movement** rất cao nếu một thiết bị bị xâm nhập*
> 
> *Tôi yêu cầu phải **thiết kế lại toàn bộ hạ tầng mạng** theo mô hình Zero Trust."*

**CTO hỏi:**
> *"Cụ thể chúng ta cần làm gì? Và mất bao lâu?"*

**CISO đề xuất:**
> *"Tôi đề xuất triển khai các giải pháp sau trong 2 tuần:*
> 
> **1. OSPF Multi-Area với Totally Stubby Area cho IoT**
> - Area 30 (IoT) chỉ nhận **default route**
> - Router IoT không biết subnet cụ thể của Management/Staff
> - *→ Ngay cả khi hacker chiếm Router, họ không biết tấn công đâu*
> 
> **2. Extended ACLs theo mô hình 3 lớp**
> - Core Layer: Bảo vệ backbone, chỉ cho phép OSPF + Admin SSH
> - Distribution Layer: ACL cô lập IoT, bảo vệ DMZ
> - Access Layer: ACL kiểm soát Staff → Management
> - *→ Chặn ở mọi điểm tiếp xúc*
> 
> **3. DMZ Security Hardening**
> - Chặn DMZ khởi tạo kết nối vào Inside
> - Chỉ cho phép Internet truy cập DMZ qua HTTP/HTTPS
> - *→ Nếu Web server bị hack, không thể nhảy vào database*
> 
> **4. OSPF Authentication**
> - Bật MD5 authentication trên tất cả link OSPF
> - *→ Chống giả mạo routing advertisements*
> 
> **5. Least Privilege Access**
> - Chỉ Admin PC (`10.1.2.50`) được SSH vào thiết bị mạng
> - Staff chỉ được HTTPS đến DMZ (không được HTTP, SSH...)
> - *→ Giảm attack surface*"

**Giám đốc phê duyệt:**
> *"OK, hãy triển khai ngay. Đây là ưu tiên cao nhất. Chúng ta không thể để sự kiện này lặp lại."*

---

## V. YÊU CẦU TỪ CISO (YOUR MISSION)

**Bạn là kỹ sư mạng được giao nhiệm vụ triển khai giải pháp của CISO.**

### Mục tiêu tổng quát:
> **Thiết kế và triển khai hạ tầng mạng an toàn theo mô hình Zero Trust, ngăn chặn nguy cơ Lateral Movement từ IoT Zone.**

### Yêu cầu cụ thể:

#### ✅ Yêu cầu 1: Cô lập hoàn toàn IoT Zone
- **Mục tiêu:** IoT KHÔNG được biết địa chỉ IP cụ thể của mạng nội bộ
- **Công nghệ:** OSPF Totally Stubby Area
- **Kiểm tra:** `show ip route` trên Router IoT chỉ hiển thị `O*IA 0.0.0.0/0`

#### ✅ Yêu cầu 2: Chặn traffic độc hại từ IoT
- **Mục tiêu:** IoT bị chặn truy cập Management, Staff, DMZ
- **Công nghệ:** Extended ACL tại Router IoT
- **Ngoại lệ:** Cho phép IoT gửi Syslog đến `172.16.10.200:514`

#### ✅ Yêu cầu 3: Bảo vệ DMZ
- **Mục tiêu:** Web Server bị hack không thể nhảy vào Inside
- **Công nghệ:** Extended ACL chặn DMZ → Inside

#### ✅ Yêu cầu 4: Kiểm soát truy cập Staff
- **Mục tiêu:** Staff chỉ làm việc, không xem data nhạy cảm
- **Công nghệ:** Extended ACL chặn Staff → Management VLAN

#### ✅ Yêu cầu 5: Bảo vệ quyền quản trị
- **Mục tiêu:** Chỉ Admin PC được SSH vào thiết bị mạng
- **Công nghệ:** ACL trên VTY lines

#### ✅ Yêu cầu 6: Chống giả mạo định tuyến
- **Mục tiêu:** Không ai có thể đưa fake routes vào hệ thống
- **Công nghệ:** OSPF MD5 Authentication

#### ✅ Yêu cầu 7: Khả năng chịu lỗi
- **Mục tiêu:** Khi một đường truyền đứt, tự động chuyển sang backup
- **Công nghệ:** OSPF cost manipulation, multiple paths

---

## VI. PHÂN TÍCH RỦI RO

### Rủi ro 1: Lateral Movement (Tấn công lan truyền ngang)

**Kịch bản tấn công nếu KHÔNG có giải pháp:**

```
1. Hacker chiếm Camera IoT (192.168.100.15)
         ↓
2. Từ Camera, scan mạng nội bộ
   → Phát hiện File Server: 10.1.2.100
         ↓
3. Khai thác lỗ hổng SMB (Port 445)
   → Tải file salary.db về
         ↓
4. Đòi tiền chuộc hoặc bán data trên dark web
         ↓
   💸 Thiệt hại: Triệu đô + Uy tín công ty
```

**Giải pháp:**
- Totally Stubby Area: Camera không biết `10.1.2.100` tồn tại
- Extended ACL: Ngay cả khi biết IP, packet bị drop

---

### Rủi ro 2: Compromised DMZ Server

**Kịch bản tấn công nếu KHÔNG có DMZ ACL:**

```
1. Hacker exploit Web Server (172.16.10.100)
         ↓
2. Từ Web Server, ping sweep mạng Inside
   → Phát hiện Database Server: 10.1.2.100
         ↓
3. Tấn công SQL Injection vào Database
         ↓
   🗃️ Đánh cắp toàn bộ dữ liệu khách hàng
```

**Giải pháp:**
- ACL chặn DMZ → Inside (except specific services)

---

### Rủi ro 3: Insider Threat (Nhân viên nội bộ)

**Kịch bản:**
- Nhân viên Marketing tò mò muốn xem bảng lương
- Truy cập `\\10.1.2.100\HR\salary.db`

**Giải pháp:**
- ACL chặn VLAN Staff (10.1.1.0/24) → VLAN Management (10.1.2.0/24)

---

## VII. THỜI GIAN TRIỂN KHAI

**Tuần 1:**
- Thiết kế topology chi tiết
- Quy hoạch IP, OSPF areas
- Viết danh sách ACL policies

**Tuần 2:**
- Triển khai trên môi trường test (Mininet)
- Kiểm chứng tất cả test cases
- Viết tài liệu vận hành

**Tuần 3 (Production):**
- Migration từ hệ thống cũ
- Monitoring 24/7 trong tuần đầu

---

## VIII. TIÊU CHÍ THÀNH CÔNG

Dự án được coi là thành công khi:

- [x] **Không còn cảnh báo từ IDS** về scanning từ IoT zone
- [x] **Penetration Test** bởi Red Team không thể lateral movement
- [x] **Uptime 99.9%** - không ảnh hưởng hoạt động kinh doanh
- [x] **Compliance** với ISO 27001, PCI-DSS (nếu có payment data)

---

> **"Bảo mật không phải là trạng thái, mà là một quá trình liên tục."**  
> Sau khi triển khai, phải monitoring, audit, và cải tiến thường xuyên.

**BÂY GIỜ, HÃY BẮT ĐẦU THIẾT KẾ HỆ THỐNG!**
