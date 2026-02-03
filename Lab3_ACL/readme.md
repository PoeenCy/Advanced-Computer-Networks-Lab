# BÀI TẬP THỰC HÀNH SỐ 1

## THIẾT KẾ VÀ TRIỂN KHAI ACL TRONG MÔ HÌNH MẠNG 3 LỚP CÓ DMZ (MININET)

---

## 1. Giới thiệu

Tài liệu này hướng dẫn chi tiết cách **thiết kế, triển khai và kiểm chứng Access Control List (ACL)** trong **mô hình mạng 3 lớp (Core – Distribution – Access)** có **vùng DMZ**, được mô phỏng bằng **Mininet trên Linux**.

Bài thực hành giúp sinh viên nắm vững cách kiểm soát lưu lượng mạng dựa trên **IP, Protocol và Port**, đồng thời rèn luyện tư duy thiết kế chính sách bảo mật trong hệ thống mạng thực tế.

---

## 2. Mục tiêu bài thực hành

Sau khi hoàn thành bài này, sinh viên có thể:

* Hiểu rõ **nguyên lý hoạt động của ACL** trong mạng máy tính.
* Phân biệt và sử dụng đúng:

  * **Standard ACL**: lọc theo IP nguồn
  * **Extended ACL**: lọc theo IP nguồn/đích, protocol, port
* Xác định đúng **vị trí đặt ACL** và **hướng áp dụng (in/out)** để:

  * Tăng cường bảo mật
  * Tối ưu hiệu suất hệ thống
* Áp dụng ACL trong môi trường **Mininet (Linux-based networking)**.

---

## 3. Mô hình mạng tổng thể

### 3.1 Kiến trúc 3 lớp

Mạng được thiết kế theo mô hình phân tầng chuẩn:

* **Core Layer**: Router trung tâm (định tuyến & kiểm soát truy cập)
* **Distribution Layer**: Switch L3 (phân chia VLAN, áp ACL)
* **Access Layer**: Switch L2 (kết nối các host)

### 3.2 Phân vùng mạng (Security Zones)

| Vùng    | Mô tả          | Địa chỉ IP                                                  |
| ------- | -------------- | ----------------------------------------------------------- |
| Inside  | Mạng nội bộ    | VLAN Sinh viên: 10.1.1.0/24  \ VLAN Giảng viên: 10.1.2.0/24 |
| DMZ     | Vùng công cộng | Web Server: 172.16.10.100                                   |
| Outside | Internet       | Mạng ngoài (giả lập)                                        |

---

## 4. Các chính sách ACL cần triển khai

### 4.1 Chính sách 1 – Security (Bảo mật)

**Mục tiêu:** Bảo vệ mạng nội bộ khỏi Internet

* Cho phép Internet truy cập **Web Server trong DMZ** qua:

  * HTTP (TCP 80)
  * HTTPS (TCP 443)
* Chặn **toàn bộ truy cập từ Internet vào Inside**

➡ Áp dụng bằng **Extended ACL** tại cổng kết nối Outside → Router (Inbound)

---

### 4.2 Chính sách 2 – Privacy (Riêng tư)

**Mục tiêu:** Cách ly VLAN Sinh viên và VLAN Giảng viên

* VLAN Sinh viên (`10.1.1.0/24`):

  * Được phép truy cập Web Server trong DMZ
  * Bị chặn truy cập VLAN Giảng viên (`10.1.2.0/24`)

➡ Áp dụng bằng **Extended ACL** tại interface VLAN Sinh viên (Inbound)

---

### 4.3 Chính sách 3 – Management (Quản trị)

**Mục tiêu:** Giới hạn quyền quản trị thiết bị mạng

* Chỉ máy Admin `10.1.2.50`:

  * Được phép SSH (TCP 22)
  * Quản trị Router & Core Switch
* Các host khác:

  * Bị từ chối truy cập SSH

➡ Áp dụng bằng **Extended ACL** trên interface quản trị hoặc control-plane

---

## 5. Quy hoạch ACL (ACL Planning)

| Chính sách | Loại ACL | Vị trí áp dụng             | Hướng |
| ---------- | -------- | -------------------------- | ----- |
| Security   | Extended | Router – Outside Interface | In    |
| Privacy    | Extended | VLAN Sinh viên             | In    |
| Management | Extended | Router/Core (SSH)          | In    |

---

## 6. Triển khai trên Mininet

### 6.1 Môi trường yêu cầu

* Ubuntu 20.04 / 22.04
* Mininet
* Python 3
* Open vSwitch
* Quyền sudo

### 6.2 Mô hình Mininet (Logic)

* Router/Core: Linux Router (enable IP forwarding)
* Switch: OVS (Access & Distribution)
* Host:

  * sinhvien1,sinhvien2 (VLAN Sinh viên)
  * giangvien1,giangvien2 (VLAN Giảng viên)
  * admin (10.1.2.50)
  * webserver (172.16.10.100)
  * internet (Internet giả lập)

ACL được mô phỏng bằng:

* `iptables` (filter table)
* Rule theo source IP, destination IP, port

---

## 7. Kiểm chứng (Verify)

### 7.1 Kiểm tra bằng Ping

* Internet → Inside ❌ (Fail)
* Internet → Web Server (80/443) ✅
* Sinh viên → Giảng viên ❌
* Sinh viên → DMZ ✅

### 7.2 Kiểm tra dịch vụ

* `curl http://172.16.10.100` từ Outside/Sinh viên → Thành công
* `ssh` từ Admin → Router/Core → Thành công
* `ssh` từ host khác → Bị từ chối

### 7.3 Quan sát bằng Mininet CLI

* `pingall`
* `hX traceroute hY`
* Theo dõi rule hit bằng `iptables -L -v`

---

## 8. Kết luận

Bài thực hành giúp sinh viên:

* Hiểu rõ vai trò ACL trong bảo mật mạng
* Áp dụng ACL đúng vị trí, đúng mục đích
* Tiếp cận tư duy **Firewall – Zone-based Security**
* Làm quen với mô phỏng mạng thực tế bằng **Mininet**

---

## 9. Ghi chú

* ACL có thứ tự xử lý **từ trên xuống** – cần sắp xếp rule hợp lý
* Luôn tồn tại **implicit deny** ở cuối ACL
* Nên kiểm tra từng chính sách độc lập trước khi kết hợp

---


