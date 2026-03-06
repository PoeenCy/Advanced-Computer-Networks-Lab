# ĐỒ ÁN LAB: TÁI THIẾT KẾ HẠ TẦNG MẠNG DOANH NGHIỆP THEO MÔ HÌNH ZERO TRUST

**Tích hợp OSPF Multi-Area + Extended ACLs + Kiến trúc 3 Lớp + DMZ**

---

## � TÓM TẮT ĐỀ BÀI

| Mục | Nội dung |
|:---|:---|
| **🎯 Mục tiêu** | Thiết kế hạ tầng mạng doanh nghiệp theo mô hình **Zero Trust**, ngăn chặn tấn công lan truyền (Lateral Movement) từ IoT Zone |
| **🏢 Kịch bản** | Tập đoàn TechVerse phát hiện malware trên camera IoT, cần gia cố toàn bộ hệ thống mạng |
| **🔧 Công nghệ** | OSPF Multi-Area (4 areas), Extended ACLs (5 policies), DMZ, MD5 Authentication, 3-Layer Architecture |
| **🌐 Topology** | 6 Routers, 4 OSPF Areas (Area 0-Backbone, 10-HQ, 20-DMZ, 30-IoT Stub), 4 Security Zones |
| **🛡️ Bảo mật** | IoT Zone cách ly hoàn toàn (Totally Stubby Area + ACLs), DMZ không truy cập Inside, Staff không truy cập Management |
| **💻 Môi trường** | **Mininet trên Linux** (Ubuntu/Kali) - FRRouting + iptables |
| **📚 Học liệu** | [FOUNDATIONS.md](./docs/FOUNDATIONS.md) (Phân tích PCWorld), [SCENARIO.md](./docs/SCENARIO.md) (Bối cảnh), [TOPOLOGY.md](./docs/TOPOLOGY.md) (Thiết kế), [REQUIREMENTS.md](./docs/REQUIREMENTS.md) (Yêu cầu), [VERIFICATION.md](./docs/VERIFICATION.md) (Test cases) |
| **⚠️ Lưu ý** | **KHÔNG có cấu hình mẫu** - Sinh viên phải tự research và thiết kế |

**Đọc thứ tự khuyến nghị:** FOUNDATIONS → SCENARIO → TOPOLOGY → REQUIREMENTS → VERIFICATION

---

## �📚 TÀI LIỆU HƯỚNG DẪN

Để hoàn thành đồ án này, sinh viên cần nghiên cứu kỹ các tài liệu sau theo thứ tự:

### 1. [📖 PHÂN TÍCH BÀI BÁO & NỀN TẢNG LÝ THUYẾT](./docs/FOUNDATIONS.md)
*Đọc đầu tiên để hiểu TẠI SAO cần các giải pháp này*

- Phân tích chi tiết bài báo PCWorld về bảo mật mạng
- Ánh xạ từ giải pháp gia đình sang doanh nghiệp
- Các nguy cơ bảo mật trong mạng phẳng (Flat Network)
- Tại sao cần OSPF Multi-Area?
- Tại sao cần Extended ACLs?
- Tại sao cần DMZ?
- Tại sao cần kiến trúc 3 lớp?

### 2. [📝 BỐI CẢNH & KỊCH BẢN](./docs/SCENARIO.md)
*Hiểu rõ tình huống thực tế cần giải quyết*

- Giới thiệu Tập đoàn TechVerse
- 3 Campus và chư năng
- Sự kiện kích hoạt (IoT malware discovery)
- Yêu cầu từ CISO
- Phân tích rủi ro cụ thể

### 3. [🏗️ THIẾT KẾ KIẾN TRÚC MẠNG](./docs/TOPOLOGY.md)
*Thiết kế chi tiết hạ tầng mạng*

- Mô hình 3 lớp (Core-Distribution-Access)
- OSPF Multi-Area design (4 Areas)
- Quy hoạch IP addressing
- Security Zones layout
- Sơ đồ topology chi tiết

### 4. [⚙️ YÊU CẦU KỸ THUẬT](./docs/REQUIREMENTS.md)
*Các nhiệm vụ cần thực hiện*

- Cấu hình OSPF Multi-Area
- Triển khai Extended ACLs
- Thiết lập DMZ Security Policies
- Gia cố hạ tầng (MD5 Auth, Stub Areas)
- Phân bổ điểm chi tiết

### 5. [✅ TIÊU CHÍ NGHIỆM THU](./docs/VERIFICATION.md)
*Cách kiểm tra và đánh giá kết quả*

- Test cases kết nối hợp lệ
- Test cases bảo mật (blocked traffic)
- OSPF verification commands
- Failover testing
- Báo cáo yêu cầu

---

## 🎯 MỤC TIÊU HỌC TẬP

Sau khi hoàn thành đồ án, sinh viên sẽ:

1. **Hiểu sâu về Defense in Depth**
   - Tại sao một lớp bảo mật không đủ
   - Cách kết hợp nhiều cơ chế phòng thủ
   - Áp dụng Zero Trust model trong thực tế

2. **Thiết kế mạng doanh nghiệp**
   - Phân tích requirements và rủi ro
   - Lựa chọn topology phù hợp
   - Quy hoạch IP và OSPF areas hợp lý

3. **Triển khai OSPF Multi-Area**
   - Hiểu khác biệt giữa các loại Areas
   - Tối ưu hóa với cost manipulation
   - Thiết lập backup routes
   - Bảo mật với MD5 authentication

4. **Áp dụng Extended ACLs**
   - Viết ACL policies theo security zones
   - Đặt ACL đúng vị trí, đúng hướng
   - Cân bằng giữa bảo mật và chức năng

5. **Kỹ năng troubleshooting**
   - Debug OSPF neighbor issues  
   - Phân tích ACL logic errors
   - Verify security policies

---

## 🛠️ MÔI TRƯỜNG THỰC HÀNH

### Yêu cầu bắt buộc: Mininet

### Hệ thống khuyến nghị

- **OS:** Ubuntu 20.04+, Kali Linux, hoặc Debian 11+
- **RAM:** Tối thiểu 4GB (khuyến nghị 8GB)
- **CPU:** 2 cores+ (khuyến nghị 4 cores)
- **Storage:** 10GB free space

---

## 📋 QUY TRÌNH THỰC HIỆN

### Bước 1: Nghiên cứu lý thuyết 
1. Đọc kỹ [FOUNDATIONS.md](./docs/FOUNDATIONS.md)
2. Đọc [SCENARIO.md](./docs/SCENARIO.md)
3. Ghi chú các điểm quan trọng

### Bước 2: Thiết kế 
1. Đọc [TOPOLOGY.md](./docs/TOPOLOGY.md)
2. Vẽ lại sơ đồ theo hiểu biết của mình
3. Quy hoạch IP addresses
4. Thiết kế OSPF areas
5. Lập danh sách ACL policies cần thiết

### Bước 3: Triển khai 
1. Tạo Mininet topology
2. Cấu hình OSPF trên các router
3. Triển khai ACLs
4. Áp dụng security hardening

### Bước 4: Kiểm chứng 
1. Thực hiện tất cả test cases trong [VERIFICATION.md](./docs/VERIFICATION.md)
2. Ghi lại kết quả (screenshot, logs)
3. Phân tích kết quả bất thường

### Bước 5: Báo cáo 
1. Viết báo cáo theo template
2. Giải thích các quyết định thiết kế
3. Trả lời các câu hỏi lý thuyết

---

## 💡 LƯU Ý QUAN TRỌNG

### ⚠️ KHÔNG có Lời giải Sẵn

Đồ án này **KHÔNG** cung cấp:
- ❌ Configuration scripts hoàn chỉnh
- ❌ Lệnh cấu hình chi tiết từng bước
- ❌ Topology scripts tự động

**Tại sao?**
- Mục tiêu là rèn luyện kỹ năng tự thiết kế và troubleshoot
- Trong thực tế, bạn sẽ phải tự tìm cách giải quyết vấn đề
- Học sâu hơn khi tự research và thử nghiệm

---

## 🆘 HỖ TRỢ & TÀI LIỆU THAM KHẢO

### Tài liệu bổ sung
- RFC 2328 - OSPF Version 2
- Cisco IOS Command Reference
- Mininet Documentation
- FRRouting User Guide

### Câu hỏi thường gặp

**Q: Tôi có thể dùng Cisco Packet Tracer thay vì Mininet không?**
A: Bài lab này được thiết kế cho Mininet để đảm bảo môi trường đồng nhất.

**Q: Tôi không biết cách cấu hình OSPF Totally Stubby Area?**
A: Hãy nghiên cứu RFC 2328 và tài liệu Cisco IOS. Phần [FOUNDATIONS.md](./docs/FOUNDATIONS.md) cũng có phân tích chi tiết.

**Q: ACL của tôi không hoạt động, làm sao debug?**
A: Kiểm tra: (1) Wildcard mask đúng chưa? (2) Đặt đúng interface và direction chưa? (3) Thứ tự rules hợp lý chưa?

**Q: Tôi có thể tham khảo cấu hình của Lab1 và Lab2 không?**
A: Được, nhưng cần hiểu và điều chỉnh cho phù hợp với thiết kế của bạn. Đừng copy mà không hiểu.

---

## 📜 GIẤY PHÉP & GHI NGUỒN

Tài liệu này được phát triển cho mục đích giáo dục dựa trên:
- Bài báo **PCWorld: "How to secure your router and home network"**
- Kiến thức từ Lab1_OSPF (OSPF Multi-Area implementation)
- Kiến thức từ Lab2_ACLs (3-layer + DMZ + Micro-segmentation)

**Tác giả:** Trần Thanh Nhã - Huỳnh Văn Dũng  
**Phiên bản:** 2.0 (Cập nhật: Tháng 2/2026)

---

> **"Security is not a product, but a process."** — Bruce Schneier

**Chúc các bạn học tốt và hoàn thành xuất sắc đồ án! 🚀**
