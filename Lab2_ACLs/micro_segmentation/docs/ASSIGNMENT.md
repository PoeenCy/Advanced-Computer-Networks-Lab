# 📝 ĐỀ BÀI: BẢO MẬT PHÂN ĐOẠN (MICRO-SEGMENTATION)

**Môn học:** Mạng Máy Tính Nâng Cao
**Giảng viên:** Lê Viết Thanh

---

## 1. Tư duy cốt lõi (Core Concepts)
*   **Zero Trust:** "Cùng một mạng không có nghĩa là an toàn". Không tin bất cứ ai, kể cả thiết bị trong mạng nội bộ.
*   **ACL Chuyên sâu:** Sử dụng Extended ACL để kiểm soát chi tiết lưu lượng Host-to-Host.
*   **Ngăn chặn Lateral Movement:** Chặn đứng khả năng kẻ tấn công nhảy từ máy này sang máy khác.

---

## 2. Mục đích & Yêu cầu Kỹ thuật
Bạn cần cấu hình mạng để đạt được 3 mục tiêu bảo mật sau:

### ✅ Yêu cầu 1: Isolated Hosts (Cô lập máy trạm)
*   **Đối tượng:** PC-A (`10.1.1.5`) và PC-B (`10.1.1.6`)
*   **Yêu cầu:** Tuyệt đối **KHÔNG** được Ping thấy nhau và **KHÔNG** được truy cập các dịch vụ chia sẻ file (như SMB/Port 445) của nhau.
*   *Ý nghĩa:* Nếu PC-A bị nhiễm virus, nó không thể lây sang PC-B.

### ✅ Yêu cầu 2: Shared Service (Dịch vụ chia sẻ)
*   **Đối tượng:** PC-A, PC-B → truy cập PC-C (`10.1.1.100`)
*   **Yêu cầu:** Cả hai máy đều được phép truy cập vào File Server (PC-C) nhưng **CHỈ** qua cổng **HTTPS (443)** để lấy tài liệu thực hành.
*   **Cấm:** Mọi giao thức khác (HTTP 80, SSH 22, Ping...) đến PC-C đều phải bị chặn.

### ✅ Yêu cầu 3: Strict Management (Quản trị nghiêm ngặt)
*   **Đối tượng:** Truy cập vào Router/Gateway
*   **Yêu cầu:** Chỉ duy nhất **PC-A** được phép truy cập vào giao diện quản trị Web của Router (Port 80) để cấu hình.
*   **Cấm:** Các máy khác (PC-B, PC-C...) bị chặn hoàn toàn truy cập vào trang quản trị này.

---

## 3. Các bước thực hiện (Implementation Steps)

1.  **Thiết lập Topology:**
    *   Chạy script `infrastructure.py` để dựng mạng Mininet với các máy: PC-A, PC-B, PC-C, Router và Switch.

2.  **Xác định lỗ hổng (Verify Flat Network):**
    *   Trước khi áp dụng bảo mật, hãy thử dùng công cụ tấn công (`c2_attacker.py` hoặc ping tay) để thấy rằng mạng đang "thông suốt" hoàn toàn. PC-A có thể tấn công PC-B dễ dàng.

3.  **Triển khai Micro-segmentation (OpenFlow Rules / ACL):**
    *   Viết script hoặc dùng lệnh `ovs-ofctl` để đẩy các luật (Flow Rules) vào Switch s1.
    *   **Logic cần đạt:**
        *   Cho phép ARP.
        *   Drop traffic PC-A ↔ PC-B.
        *   Allow IP Src Any → IP Dst PC-C (Port 443).
        *   Allow IP Src PC-A → IP Dst Gateway (Port 80).
        *   Drop All (Default).

4.  **Kiểm thử & Nghiệm thu:**
    *   Chạy lại kịch bản tấn công để chứng minh Hacker đã bị vô hiệu hóa.

---

## 4. Tiêu chí nghiệm thu (Acceptance Criteria)

Sinh viên cần cung cấp bằng chứng (Screenshot/Log) cho các kịch bản sau:
1.  **Ping thất bại:** PC-A ping PC-B → `Request Timed Out` (hoặc 100% packet loss).
2.  **Dịch vụ hoạt động:** PC-A truy cập `https://10.1.1.100` → Thành công (Lấy được file).
3.  **Chặn truy cập trái phép:** PC-B truy cập Web Router → `Connection Refused` hoặc Timeout.
4.  **Giải thích:** Tại sao phải dùng địa chỉ IP cụ thể (/32) trong luật thay vì dùng cả dải mạng (/24)?
