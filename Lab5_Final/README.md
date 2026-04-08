# HỆ THỐNG ĐIỀU PHỐI VÀ ĐO LƯỜNG IPv6 SPINE-LEAF ZERO TRUST

Dự án này là mô hình thực nghiệm Trung tâm dữ liệu (Data Center) tiên tiến sử dụng kiến trúc mạng **Spine-Leaf Pure IPv6**. Hệ thống được trang bị Định tuyến động OSPFv3, cơ chế Cân bằng tải ECMP, Tường lửa vi mô Zero Trust (Micro-segmentation) và Dịch vụ biên dịch NAT64 để giao tiếp với Internet IPv4.

---

## 🏗️ Kiến Trúc Các Tập Tin Cốt Lõi

Dự án được vận hành bởi 6 tệp tin chính yếu sau đây. Mỗi tệp đóng một vai trò chuyên biệt để dựng nên vòng đời hoàn chỉnh của trung tâm dữ liệu:

### 1. `topology.py` - Trái Tim Đám Mây (Orchestrator)
Đây là tệp tin nền tảng, thiết lập toàn bộ mạng lưới SDN thông qua Mininet. 
- **Nhiệm vụ:** Dựng mô hình Topology Spine-Leaf gồm 7 Switch (2 Spine, 3 Leaf, 1 Border, 1 NAT Router) và 8 Hosts. Nó bơm cấu hình IP tĩnh, khởi tạo bộ định tuyến động `FRR` (OSPFv3) cho các Switch, và cung cấp bảng điều khiển CLI đa chức năng (`nat`, `acl`, `dropacl`, `failtest`).
- **Cách dùng:** Mở Terminal nền và chạy lệnh: `sudo python3 topology.py`

### 2. `microsegment.sh` - Khiên Hộ Vệ Vi Mô (Zero Trust Firewall)
Được kích hoạt tự động qua lệnh `acl` trong Mininet, đây là tệp kịch bản kiểm soát anh ninh mạng nghiêm ngặt dựa trên triết lý Zero Trust.
- **Nhiệm vụ:** 
  - Khóa chặt mọi giao tiếp rác, chỉ thả lỏng ICMPv6 cốt lõi (NDP) cho việc định vị MAC.
  - Cô lập nhóm Web (Web1 không thể ping Web2) để ngừa lây lan mã độc (Lateral Movement).
  - Bảo vệ lõi DB (Database): Cấm tiệt vạn vật, chỉ cho Web giao tiếp qua Port 3306 và Cluster DB nói chuyện với nhau.
  - Phân quyền ngặt nghèo cho Internet và cụm DNS (Port 53).

### 3. `nat_setup.sh` - Cổng Biên Dịch (NAT64 / DNS64)
Được kích hoạt bằng lệnh `nat` trong Mininet. Do mạng lõi là Pure IPv6, các Server không thể hiểu trực tiếp IP của `serverhcm` hay `internet` (vốn là chuẩn IPv4).
- **Nhiệm vụ:** Thiết lập lõi dịch thuật ảo `Tayga` (NAT64) tại Border Router R1. Tayga sẽ trộn chung dải IPv6 giả lập (`64:ff9b::/96`) với IPv4 thực tế, kết hợp NAT Table MASQUERADE để giúp thông tin từ v6 chảy mượt mà ra ngoài lưới điện v4 mà không gây rớt gói.

### 4. `failover_test.sh` - Kẻ Hủy Diệt (Downtime Injector)
Dùng để giả lập sự cố thiên tai/đứt cáp quang bằng tay (Kích hoạt qua lệnh `failtest`).
- **Nhiệm vụ:** Chủ động đánh sập (`down`) toàn bộ các Link kết nối từ hạ tầng Leaf (Lớp dưới) lên Spine S1. Kịch bản này ép mạng sập 1 bên để đánh giá tốc độ hội tụ và phục hồi tuyến tính cực nhanh của giao thức định tuyến OSPFv3 thông qua đường cáp tời Spine S2 dự phòng.

### 5. `tool.py` - Hệ Thống Nám Trắc Hình Ảnh (Diagnostic & Analytics GUI)
Tệp giao diện trực quan Tkinter dùng song song với Mininet. Là "con mắt thần" để Giám khảo nhìn thấy chất lượng thực sự của sơ đồ lớp.
- **Nhiệm vụ:** 
  - **Tool Tương Tác:** Chỉ định Host đích/nguồn để test RTT Ping, Rớt gói Loss%, và Trace lộ trình đa luồng theo thời gian thực.
  - **Academic Chart Reports:** Tích hợp 5 chức năng sinh biểu đồ Báo cáo học thuật cực mạnh. 
    + *(Case 1+2)*: Đo vẽ đồ thị Thời gian hội tụ OSPF khi mạng sập/rút cáp bằng dữ liệu `Bytes Raw` thật.
    + *(Case 3)*: Vẽ Ma Trận Heatmap phơi bày lỗ hổng Bảo Mật (Zero Trust ACL) đa Port (80, 3306, 53) bằng thuật toán quét song song (Threading).
    + *(Case 4+5)*: Bơm dữ liệu lớn (`iperf -P 8`) để kích hoạt cơ chế chia tải chẻ ngã ba OSPF ECMP, và vẽ bảng đồ thị băng thông hiển thị tường tận sức gánh của cả 2 Spine.
  - Đặc biệt: Tự động trích xuất mọi số liệu từ Nhân Linux (Counter) ra các File `.csv` đi kèm ảnh, đảm bảo độ trong sạch 100% của báo cáo khoa học.
- **Cách dùng:** Mở Terminal thứ hai (ngoài Mininet) và chạy: `sudo python3 tool.py`

### 6. `draw_topology.py` - Họa Sĩ Thiết Kế
Tệp phụ trợ dùng thư viện `NetworkX` và `Matplotlib` để phác thảo hình dáng tổng quan của Topology ra định dạng `.png`.
- **Nhiệm vụ:** Ánh xạ lại sơ đồ vật lý thực tế các Node và Link (Spine Vuông đỏ, Leaf Xanh lá, Hosts Tròn) trên lưới phẳng 2D. Sản phẩm này có thể đính kèm vào phần Mở đầu Môn học trong đồ án/báo cáo PDF để người đọc có cái nhìn trực quan trước khi chui vào lệnh Terminal.

---
## 🎯 Hướng dẫn Chạy Thử (Workflow)

1. **Khởi tạo Ảo Hóa:** `sudo python3 topology.py`
2. **Kích hoạt Dịch Vụ Core:** Ở giao diện `mininet>`, gõ `nat` và `acl` để lên đồ Firewall và Internet.
3. **Mở Giao Diện Analyzer:** Mở 1 cửa sổ Ubuntu mới (nhấn Ctrl+Alt+T), gõ `cd /d/download/MMTNC_FINAL/source` rồi chạy tiếp `sudo python3 tool.py`.
4. **Trích Xuất Dữ Liệu:** Click vào các nút Case 1..5 trên giao diện Tool để sinh ảnh Biểu đồ (`.png`) và Sheet Số liệu (`.csv`) xuất cực đẹp tại đường dẫn `/logs/`.
