# HƯỚNG DẪN THỰC HÀNH LAB 4: PHÂN TÍCH LUỒNG GÓI TIN & OSPF

Tài liệu này cung cấp kịch bản từng bước để bạn tự chạy, thuyết trình và giải thích cho sinh viên/nhóm khác cách hoạt động của hệ thống mạng đa vùng (Multi-Area OSPF) và ACL thông qua Wireshark và CLI. 

Tài liệu cũng bao gồm các **kinh nghiệm xử lý lỗi thực tế** (Troubleshooting) khi môi trường không chạy như ý muốn.

---

## BƯỚC 1: CHUẨN BỊ MÔI TRƯỜNG TỪ SỐ 0

Trong quá trình cài đặt thực tế trên Ubuntu mới, bạn thường gặp màn hình "đứng hình" đòi chọn Yes/No của Wireshark. Để bỏ qua và cài đặt cấu hình tự động trơn tru 100%, hãy chạy cụm lệnh sau:

```bash
# Bỏ qua màn hình debconf chặn tiến trình cài đặt của wireshark
echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mininet wireshark tshark tcpdump frr frr-pythontools
```

---

## BƯỚC 2: KHỞI ĐỘNG MÔ HÌNH MẠNG

Để Mininet có thể gọi được các cửa sổ đồ họa của máy chủ thật (như Gnome Terminal / Wireshark), chúng ta bắt buộc phải chạy lệnh khởi động kèm theo tham số bảo lưu biến môi trường màn hình (`-E`):

```bash
cd /home/poeency/Documents/MangNangCao/Advanced-Computer-Networks-Lab/Lab4_Packet_Analysis
sudo -E python3 src/topology.py
```
*(Đợi 3-5 giây để tiến trình OSPF đồng bộ xong, bạn sẽ thấy dấu nhắc lệnh `mininet> `).*

---

## BƯỚC 3: KIỂM TRA BẢN CHẤT CỦA BỘ ĐỊNH TUYẾN 

Thay vì bắt gói tin mù mờ ngay lập tức, một kỹ sư thực thụ phải chui được vào "Bộ não định tuyến" của Router.
Đề bài yêu cầu có 5 Router. Hệ thống mã nguồn đã chia nhỏ và cô lập file socket của chúng để tránh **Lỗi Đụng Độ Dịch Vụ - Socket Collision** vào mục `/tmp/rX/`.

### 1. Mở Cửa sổ Terminal cho một Router
Tại dấu nhắc `mininet>`, hệ thống đã tích hợp sẵn lệnh `gterm` mạnh mẽ:
```bash
mininet> gterm r1
```
*(Lập tức, một cửa sổ Gnome Terminal đen riêng biệt của R1 sẽ bật lên).*

### 2. Xem Bảng Định Tuyến OSPF của R1
Tại cửa sổ mới bật lên của R1, bạn gõ lệnh kiểm tra hệ thống định tuyến VTYSH (Bản sao của Cisco IOS). **Bắt buộc** phải trỏ đúng dường dẫn Socket đã được cô lập (`/tmp/r1`) nếu không sẽ báo lỗi `ospfd is not running`:

```bash
sudo vtysh --vty_socket /tmp/r1
```
Lúc này dấu nhắc thay đổi thành `r1#`, đây là lúc bạn phô diễn các câu lệnh kinh điển:
- Kiểm tra các mạng nội bộ OSPF hội tụ: `show ip route` (Tìm những dòng có ký hiệu `O` và `O IA`).
- Kiểm tra hàng xóm OSPF: `show ip ospf neighbor` (Cột State phải là `FULL`).
- Kiểm tra cơ sở dữ liệu Link-State: `show ip ospf database`

*(Để thoát khỏi não bộ OSPF trở về Linux shell, gõ `exit`).*

---

## BƯỚC 4: HƯỚNG DẪN XEM GÓI TIN BẰNG WIRESHARK (GUI)

Vẫn tại cửa sổ Gnome Terminal của **R1** (như bạn vừa mở ở Bước 3):
1. Bạn gõ tiếp lệnh sau để bật giao diện Wireshark bắt cổng `r1-eth1` (cổng hướng về Staff Area):
   ```bash
   wireshark &
   ```
   *(Ấn Start Capture sau khi chọn cổng).*

2. Quay lại cửa sổ Terminal đang chạy `mininet>` (cửa sổ gốc của máy ảo), gõ lệnh lệnh yêu cầu PC nhân viên (Staff) tự gửi ICMP Ping vào Server DMZ:
   ```bash
   mininet> staff_pc ping -c 4 172.16.10.100
   ```
3. Tại giao diện Wireshark, chỉ cho mọi người thấy sự xuất hiện của các gói tin, đặc biệt là sự trừ lùi của tham số **TTL** ở thanh header IPv4.

---

## BƯỚC 5: CÁC KỊCH BẢN THUYẾT TRÌNH DEMO

Khi đang bật Wireshark ở R1, hãy thao diễn 2 kịch bản đắt giá này:

**🥇 Kịch bản 1: Cắt cáp và chứng kiến OSPF hội phục**
- Trong thanh lọc (filter) của Wireshark, gõ `ospf`.
- Tại cửa sổ `mininet>`, "cắt" dây nối R1-R3:
  `mininet> link r1 r3 down`
- Ngay lập tức, Wireshark của bạn sẽ bắn ra hàng loạt các gói mạng đỏ chót LSU (Link-State Update Type 1) để rêu rao về việc đứt cáp. Sau đó 10s hãy bật lại link bằng `link r1 r3 up`.

**🥈 Kịch bản 2: Chứng minh ACL đang chặn Web -> Management**
- Tại cửa sổ `mininet>`, bạn hãy "Kích hoạt" tấm khiên ACL bảo mật của hệ thống bằng lệnh:
  `mininet> acl`
- Vẫn tại cửa sổ `mininet>`, gõ lệnh sau để mở Terminal của R2 (DMZ Router): 
  `mininet> gterm r2`
- Trên cửa sổ R2 vừa xuất hiện, chạy `wireshark &` để bắt ở thẻ `any`, gõ filter `icmp`.
- Kêu Web Server thực hiện tấn công dò mạng vào nhánh Quản lý (bị cấm) trên cửa sổ `mininet>`:
  `mininet> web_srv ping -c 3 192.16.20.10`
- Chiếu kết quả trên Wireshark của R2: Rõ ràng mạng ngập Echo Request của Web Server đánh vào (Inbound cổng `r2-eth1`), **NHƯNG** cổng Outbound (`r2-eth0`) lại tịt ngòi, trống trơn. Đây là bằng chứng không thể chối cãi của Iptables ACL đã Drop gói tin từ trong trứng nước!

---

## BƯỚC 6: XUẤT PCAP TỰ ĐỘNG (Dùng để hoàn thành báo cáo nhanh)
Nếu nhóm bạn không thích tự bấm Wireshark rườm rà, bạn có thể gọi thẳng cờ tự động hóa mà chúng ta đã code:

```bash
sudo -E python3 src/topology.py --capture
```
Script sẽ tự động chạy tất cả mọi tình huống và 1 phút sau nhả đầy đủ các file lưu `.pcap` vào thư mục `/captures/`. 

