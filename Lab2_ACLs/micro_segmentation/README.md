# ĐỒ ÁN LAB 3: MICRO-SEGMENTATION & ZERO TRUST NETWORK

> **Cảnh báo bảo mật**: Bài Lab này mô phỏng các kỹ thuật tấn công và phòng thủ thực tế. Chỉ thực hiện trong môi trường Lab.

---

## 1. Giới thiệu (Overview)
Trong kỷ nguyên số, mô hình bảo mật truyền thống "tường bao" (Perimeter Security) đã không còn đủ an toàn. Một khi Hacker vượt qua được tường lửa biên, họ có thể tự do di chuyển trong mạng nội bộ (**Lateral Movement**) để khai thác các hệ thống quan trọng.

Bài Lab này yêu cầu sinh viên triển khai kỹ thuật **Micro-segmentation** (Phân đoạn vi mô) theo tư duy **Zero Trust**, nhằm cô lập và kiểm soát chặt chẽ luồng dữ liệu giữa các máy chủ, ngăn chặn tấn công lan tỏa ngay cả khi một thiết bị đã bị xâm nhập.

---

## 2. Tài liệu & Yêu cầu (Documents)

Để hoàn thành bài Lab, sinh viên cần nghiên cứu kỹ các tài liệu sau:

### 📖 [1. CỐT TRUYỆN CHI TIẾT (SCENARIO)](./docs/SCENARIO.md)
*   Hiểu rõ bối cảnh cuộc tấn công mạng giả định.
*   Xem **Sơ đồ Mạng (Topology)** và **Quy trình Tấn công (Attack Flow)** minh họa.
*   Nhận diện vai trò của từng thiết bị: Attacker (PC-A), Victim (PC-B), và Target (PC-C).

### 📝 [2. ĐỀ BÀI CHÍNH THỨC (ASSIGNMENT)](./docs/ASSIGNMENT.md)
*   Các yêu cầu kỹ thuật cụ thể cần triển khai.
*   Chính sách bảo mật (Security Policy) cần áp dụng.
*   Tiêu chí chấm điểm và nghiệm thu sản phẩm.

---

## 3. Mục tiêu Đầu ra (Objectives)
Sau khi hoàn thành đồ án này, sinh viên sẽ đạt được:
1.  Hiểu rõ sự nguy hiểm của mạng phẳng (Flat Network).
2.  Nắm vững nguyên lý **Zero Trust**: "Never Trust, Always Verify".
3.  Có khả năng thiết kế chính sách **Micro-segmentation** để cô lập thiết bị nhiễm mã độc.

---
*Chúc các bạn hoàn thành tốt bài tập!*
