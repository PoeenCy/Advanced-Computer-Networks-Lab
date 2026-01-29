# ĐỒ ÁN LAB 2: GIA CỐ & BẢO MẬT HẠ TẦNG MẠNG DOANH NGHIỆP

**Ứng dụng OSPF Multi-Area và ACLs dựa trên phân tích rủi ro thực tế**

---

## I. PHÂN TÍCH BÀI BÁO & CƠ SỞ THỰC TIỄN

**Nguồn tham khảo:** [How to secure your router and home network - PCWorld](https://www.pcworld.com/article/415583/how-to-secure-your-router-and-home-network.html).

### 1. Các nguy cơ bảo mật trọng yếu
Dựa trên phân tích từ PCWorld, chúng ta nhận diện được các lỗ hổng chí mạng trong mô hình mạng truyền thống:
*   **Hiểm họa từ "Mạng phẳng" (Flat Network):** Khi các thiết bị IoT kém bảo mật (Camera, Cảm biến, Smart TV) nằm chung vùng mạng với các máy tính chứa dữ liệu quan trọng, hacker có thể chiếm quyền điều khiển IoT để tấn công leo thang (Pivot) sang hệ thống lõi.
*   **Thiếu kiểm soát truy cập:** Việc không có các chính sách lọc gói tin (Packet Filtering) khiến mã độc dễ dàng lây lan ngang hàng (Lateral Movement).
*   **Rủi ro từ thiết bị lạ:** Nguy cơ giả mạo thiết bị định tuyến nếu không có cơ chế xác thực.

### 2. Chiến lược chuyển đổi: Từ SOHO sang Enterprise
Bài báo đề xuất các giải pháp ở mức người dùng phổ thông (Consumer). Trong đồ án này, chúng ta sẽ "phiên dịch" các ý tưởng đó sang kỹ thuật mạng doanh nghiệp chuyên sâu:

| Mục tiêu bảo mật | Giải pháp PCWorld (Consumer) | Giải pháp Đồ án (Enterprise - Cisco IOS) |
| :--- | :--- | :--- |
| **Guest Network / VLAN** | **OSPF Multi-Area (Stub Area)** | Cô lập vùng mạng rủi ro về mặt định tuyến, giảm tải tài nguyên. |
| **IP Filtering / Firewall** | **Extended ACLs** | Kiểm soát chi tiết luồng dữ liệu (Source/Dest/Port). |
| **Secure Password** | **OSPF MD5 Authentication** | Chống giả mạo thiết bị định tuyến (Rogue Router). |

---

## II. MÔ TẢ ĐỀ TÀI (LAB ASSIGNMENT)

### 1. Kịch bản (Scenario)
Công ty công nghệ **TechSecure** có trụ sở chính (HQ) và một chi nhánh văn phòng. Chi nhánh này gần đây đã lắp đặt hệ thống cảm biến giám sát môi trường (IoT).

Ban Giám đốc lo ngại rằng nếu hacker xâm nhập vào hệ thống IoT (vốn có bảo mật kém), họ có thể tấn công ngược về Server dữ liệu tại HQ.

**Nhiệm vụ:** Bạn hãy thiết kế và triển khai hệ thống mạng đảm bảo sự liên thông nhưng cô lập hoàn toàn vùng IoT khỏi vùng dữ liệu nhạy cảm.

### 2. Yêu cầu Topology (GNS3 Simulation)
Xây dựng mô hình mạng gồm 3 Router Cisco đại diện cho 3 vùng bảo mật:
*   **Vùng 1: HQ Core (Trụ sở chính)**
    *   Chứa Server dữ liệu quan trọng.
    *   Thuộc **OSPF Area 0 (Backbone)**.
*   **Vùng 2: User Branch (Chi nhánh Nhân viên)**
    *   Chứa PC làm việc của nhân viên.
    *   Thuộc **OSPF Area 1 (Standard Area)**.
*   **Vùng 3: IoT Zone (Vùng rủi ro)**
    *   Chứa các thiết bị Camera/Sensor.
    *   Thuộc **OSPF Area 2**.

### 3. Nhiệm vụ Kỹ thuật (Student Tasks)

#### A. Định tuyến nâng cao (Advanced Routing)
*   Cấu hình giao thức định tuyến **OSPFv2** trên tất cả các Router để đảm bảo kết nối.
*   **Yêu cầu đặc biệt:** Cấu hình Vùng IoT (Area 2) trở thành **Totally Stubby Area**.
    *   *Mục đích:* Router biên tại vùng IoT chỉ được phép nhận một đường default route (`0.0.0.0/0`). Nó không được phép biết chi tiết về các subnet của vùng HQ hay Vùng User (Che giấu kiến trúc mạng).

#### B. Kiểm soát truy cập (Access Control Lists)
*   Thực hiện nguyên tắc **Zero Trust** đối với vùng IoT.
*   Tạo và áp dụng **Extended ACL** tại Router biên (ABR) với các luật sau:
    *   **CHẶN (DENY):** Mọi lưu lượng khởi tạo từ **Vùng IoT** (Source IP) đi tới **Vùng HQ** (Destination IP).
    *   **CHO PHÉP (PERMIT):** Mọi lưu lượng từ **Vùng IoT** đi ra Internet (Giả lập bằng Loopback 8.8.8.8).

#### C. Gia cố hạ tầng (Hardening)
*   Bật tính năng xác thực **OSPF MD5 Authentication** trên tất cả các đường link kết nối giữa các Router.
*   Đảm bảo password được mã hóa, không hiển thị dưới dạng clear-text.

### 4. Tiêu chí nghiệm thu (Acceptance Criteria)
Sinh viên hoàn thành bài Lab khi chứng minh được các kết quả sau:

- [ ] **Kiểm tra tính liên thông:** PC Nhân viên (Area 1) ping thành công Server (Area 0).
- [ ] **Kiểm tra bảo mật:** Từ thiết bị IoT (Area 2) thực hiện lệnh Ping tới Server (Area 0) -> Kết quả phải là **Destination Unreachable** (Bị chặn bởi ACL).
- [ ] **Kiểm tra bảng định tuyến:** Lệnh `show ip route` trên Router IoT chỉ hiển thị duy nhất dòng `0.0.0.0/0 (O*IA)`, không hiển thị các dải mạng cụ thể của HQ.
- [ ] **Kiểm tra xác thực:** Dùng lệnh `debug ip ospf adj` để chứng minh quá trình xác thực MD5 diễn ra thành công.

> **Lưu ý:** Sinh viên tự thiết lập địa chỉ IP phù hợp với quy hoạch mạng.
