# 🚀 Hướng dẫn Cài đặt & Sử dụng (Installation & Usage)

## 1. Yêu cầu Tiên quyết
Bạn cần cài đặt Mininet và Open vSwitch trên máy Linux (khuyên dùng Kali hoặc Ubuntu):
```bash
sudo apt update
sudo apt install mininet openvswitch-switch
```

## 2. Chạy Mô phỏng
Chạy script Python chính với quyền root:
```bash
sudo python3 tdtu_ospf.py
```
*Lưu ý: Script sẽ tự động yêu cầu quyền sudo nếu bạn quên.*

## 3. Kiểm tra & Xác thực Hệ thống
Sau khi mạng khởi động, các cửa sổ Terminal cho từng Router sẽ hiện ra. Bạn có thể thực hiện các bước kiểm tra sau:

### 📡 Truy cập vào Router Console
Từ màn hình CLI của Mininet:
```bash
mininet> xterm R1 R2
```

### 🤝 Kiểm tra Quan hệ Láng giềng OSPF (Neighbor Adjacency)
Trên Router **R1**, kiểm tra xem nó đã thiết lập láng giềng với R2, R3 (Area 0) và R4 (Area 10) chưa:
```bash
# Trong cửa sổ terminal của R1
vtysh -c "show ip ospf neighbor"
```

### 🛤️ Xem Bảng Định tuyến (Routing Table)
Trên Router **R6** (vùng sâu nhất), kiểm tra xem nó có học được các route từ Area 0 và Area 10 không:
```bash
# Trong cửa sổ terminal của R6
vtysh -c "show ip route"
```

### 🧪 Thử nghiệm Chuyển mạch Dự phòng (Failover Test)
Kịch bản: Giả lập đường truyền chính từ Thư viện (R5) về KTX (R6) bị đứt.
1.  Đánh sập đường kết nối chính trên R5:
    ```bash
    ip link set r5-eth1 down
    ```
2.  Theo dõi log OSPF hoặc kiểm tra bảng định tuyến trên R6.
3.  Kết quả mong đợi: Lưu lượng tự động chuyển sang đường dự phòng qua R2 (đường nét đứt màu cam trên sơ đồ).

---

## 4. 🔬 Phân tích Gói tin với Wireshark

### 🎯 Mục tiêu
Sử dụng Wireshark giúp chúng ta "nhìn sâu" vào bên trong hoạt động của giao thức OSPF thay vì chỉ xem kết quả cuối cùng. Điều này giúp:
*   **Xác thực cấu hình**: Đảm bảo các tham số như Router ID, Area ID, Network Type được quảng bá chính xác.
*   **Gỡ lỗi (Troubleshooting)**: Phát hiện nguyên nhân lỗi thiết lập láng giềng (sai Hello Timer, sai Area, sai mask...).
*   **Hiểu sâu cơ chế**: Quan sát trực tiếp quá trình trao đổi gói tin Hello và LSA.

### 📊 Phân tích Chi tiết Gói tin OSPF Hello
Dưới đây là bảng phân tích một gói tin Hello mẫu bắt được trên R1:

| Trường Dữ liệu | Giá trị Ví dụ | Ý nghĩa & Minh chứng cho Bài Lab |
| :--- | :--- | :--- |
| **Source OSPF Router** | `1.1.1.1` | **Xác thực Định danh**: Chứng tỏ R1 đang gửi gói tin với đúng Router ID đã cấu hình trong script. |
| **Area ID** | `0.0.0.10` | **Xác thực Multi-Area**: Gói tin này được bắt trên cổng `r1-eth1`, chứng tỏ R1 đang hoạt động đúng vai trò ABR cho Area 10. |
| **Destination IP** | `224.0.0.5` | **Multicast**: Gói tin được gửi đến địa chỉ Multicast dành cho tất cả các OSPF Router (AllSPFRouters). |
| **Designated Router** | `0.0.0.0` | **Xác thực Network Type**: Giá trị `0.0.0.0` là bằng chứng cho thấy liên kết này là **Point-to-Point**. Không có quá trình bầu chọn DR/BDR diễn ra tại đây. |
| **Active Neighbor** | `4.4.4.4` | **Xác thực Láng giềng**: R1 đã "nhìn thấy" gói Hello từ R4, xác nhận quan hệ 2 chiều (2-Way) đã thiết lập. |

### 🛠️ Hướng dẫn Thực hành
Để bắt gói tin trên Router R1, làm theo các bước sau:

1.  **Mở Terminal riêng cho Router R1** (nếu chưa mở):
    ```bash
    mininet> xterm r1
    ```

2.  **Khởi chạy Wireshark trên R1**:
    Trong cửa sổ xterm của R1, gõ lệnh:
    ```bash
    wireshark &
    ```

3.  **Chọn Interface và Bộ lọc**:
    *   Chọn interface `r1-eth1` (kết nối về Area 10) hoặc `r1-eth0` (kết nối về Area 0) để bắt gói tin.
    *   Nhập vào ô Filter: `ospf`.
    *   Quan sát các gói tin **Hello Packet** (xuất hiện mỗi 10s) và **LS Update**.
