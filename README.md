# BÀI TẬP THỰC HÀNH - MẠNG MÁY TÍNH NÂNG CAO

**Advanced Computer Networks Lab - Practical Assignments**

---

## 📚 TỔNG QUAN

Repository này chứa các bài thực hành về thiết kế và triển khai hạ tầng mạng doanh nghiệp, tập trung vào **định tuyến động**, **bảo mật mạng**, và **kiến trúc phân tầng**.

---

## 🗂️ CÁC BÀI LAB

### [Lab 1: OSPF Multi-Area Routing](./Lab1_OSPF/)
**Chủ đề:** Định tuyến động với OSPF Multi-Area

| Mục | Nội dung |
|:---|:---|
| **Công nghệ** | OSPFv2, Multi-Area Design, ABR/ASBR |
| **Kịch bản** | Mạng campus Đại học TDTU với 3 khu vực (Đào tạo, Tiện ích, Backbone) |
| **Mục tiêu** | Hiểu phân cấp OSPF Areas, route summarization, failover routing |
| **Điểm nổi bật** | Backup routes với cost manipulation, DR/BDR election |
| **Công cụ** | Mininet + FRRouting |

---

### [Lab 2: Access Control Lists (ACLs)](./Lab2_ACLs/)
**Chủ đề:** Kiểm soát truy cập mạng với Extended ACLs

#### 2.1. [3-Layer Network + DMZ](./Lab2_ACLs/3layer_DMZ/)
| Mục | Nội dung |
|:---|:---|
| **Công nghệ** | Extended ACLs, 3-Layer Architecture (Core-Distribution-Access), DMZ |
| **Kịch bản** | Mạng doanh nghiệp với vùng Inside, DMZ, Outside |
| **Mục tiêu** | Thiết kế ACL policies: Security, Privacy, Management |
| **Điểm nổi bật** | ACL placement strategies, Firewall zone-based security |

#### 2.2. [Micro-segmentation & Zero Trust](./Lab2_ACLs/micro_segmentation/)
| Mục | Nội dung |
|:---|:---|
| **Công nghệ** | Micro-segmentation, Zero Trust Network, OpenFlow |
| **Kịch bản** | Ngăn chặn tấn công Lateral Movement trong mạng phẳng |
| **Mục tiêu** | Cô lập host-to-host, chặn malware lan truyền |
| **Điểm nổi bật** | Attack simulation, defense implementation |

---

### [Lab 3: Enterprise Network Hardening](./Lab3_Network_Hardening/)
**Chủ đề:** Gia cố bảo mật hạ tầng mạng doanh nghiệp tích hợp

| Mục | Nội dung |
|:---|:---|
| **Công nghệ** | **OSPF Multi-Area + Extended ACLs + 3-Layer + DMZ** (tích hợp Lab 1 & 2) |
| **Kịch bản** | Tập đoàn TechVerse phát hiện malware IoT, tái thiết kế theo Zero Trust |
| **Mục tiêu** | Thiết kế hệ thống phòng thủ nhiều lớp (Defense in Depth) |
| **Điểm nổi bật** | Totally Stubby Area cho IoT, 5 ACL policies, MD5 authentication |
| **Phân tích** | Dựa trên bài báo PCWorld về bảo mật mạng |
| **Công cụ** | Mininet + FRRouting + iptables |

**Đặc biệt:** Lab 3 KHÔNG cung cấp configuration mẫu - sinh viên phải tự nghiên cứu và thiết kế.

---

### [Lab 4: Packet Analysis](./Lab4/)
**Chủ đề:** Phân tích Gói Tin & Troubleshooting Mạng

| Mục | Nội dung |
|:---|:---|
| **Công nghệ** | Wireshark, Tshark, PCAP, TCP/IP Suite |
| **Kịch bản** | Phân tích lưu lượng đa vùng OSPF, bắt chi tiết gói giao thức. |
| **Mục tiêu** | Đọc hiểu sơ đồ bản tin L2/L3/L4, phân loại bản tin Hello/LSA. |
| **Điểm nổi bật** | Troubleshooting OSPF Neighbor Adjacency và ACL blocking logic. |

---

### [Lab 5: IPv6 Spine-Leaf Data Center (Final Lab)](./Lab5_Final/)
**Chủ đề:** Mô Hình Data Center Hiện Đại & Web Dashboard Giám Sát

| Mục | Nội dung |
|:---|:---|
| **Công nghệ** | Spine-Leaf Architecture, Pure IPv6, Tayga NAT64, Zero Trust Micro-segmentation, Web Dashboard (Flask/Chart.js). |
| **Kịch bản** | Triển khai trung tâm dữ liệu thế hệ mới cho nền tảng web đa cụm (Web, DNS, Database). |
| **Mục tiêu** | Hiệu năng cao (ECMP), An ninh đa lớp, Chuyển đổi linh hoạt IPv6<->IPv4. |
| **Điểm nổi bật** | Giao diện Web Monitor Dashboard trực quan đo lường độ trễ RTT, kiểm thử Tắc nghẽn mạng (Failover/ECMP Load Balance), tự động xuất dữ liệu đồ thị `.png` & phổ `.csv`. |
| **Phân tích** | ECMP Link chia tải thời gian thực, Hội tụ mạng trong 0.x mili-giây. |

---

**OS khuyến nghị:** Ubuntu 20.04+, Kali Linux, Debian 11+

---

## 📖 TÀI LIỆU THAM KHẢO

**Standards & RFCs:**
- RFC 2328 - OSPF Version 2
- RFC 2740 - OSPFv3 for IPv6

**Cisco Documentation:**
- Cisco IOS Command Reference
- CCNA Routing and Switching Study Guide

**Security Resources:**
- PCWorld: "How to secure your router and home network"
- NIST SP 800-41: Guidelines on Firewalls

---

## 👥 THÔNG TIN

**Tác giả:** Trần Thanh Nhã - Huỳnh Văn Dũng  
**Môn học:** Mạng Máy Tính Nâng Cao  

---

## 📜 LICENSE

Tài liệu này được phát triển cho mục đích giáo dục. Mọi sử dụng vì mục đích thương mại phải được sự cho phép.

---

**Chúc các bạn học tốt! 🚀**
