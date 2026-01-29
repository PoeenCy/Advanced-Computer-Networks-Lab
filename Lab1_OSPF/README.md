# Thiết kế và Mô phỏng Mạng Xương sống TDTU với OSPFv2 Multi-Area

![TDTU Network Banner](https://img.shields.io/badge/TDTU-Network%20Simulation-blue?style=for-the-badge&logo=linux)

## 🎓 Tổng quan Dự án

Dự án này mô phỏng hệ thống mạng xương sống của Đại học Tôn Đức Thắng (TDTU) trên nền tảng **Mininet** với giao thức **OSPFv2 Multi-Area**. Mục tiêu là xây dựng một hệ thống mạng phân cấp, hiệu năng cao và có khả năng chịu lỗi.

![Sơ đồ Mạng TDTU](tdtu_topology_design.png)

## 📂 Cấu trúc Tài liệu

Để giúp bạn dễ dàng theo dõi, tài liệu dự án được chia thành các phần chi tiết:

*   **[🗺️ Kiến trúc & Thiết kế Mạng (DESIGN.md)](docs/DESIGN.md)**:
    *   Sơ đồ chi tiết (Mermaid Diagram).
    *   Bảng quy hoạch IP, Interface và OSPF Areas.
    *   Giải thích lý do thiết kế (Cost, Priority, P2P...).
*   **[🚀 Hướng dẫn Cài đặt & Sử dụng (USAGE.md)](docs/USAGE.md)**:
    *   Các bước cài đặt Mininet/Open vSwitch.
    *   Cách chạy script mô phỏng.
    *   Các lệnh CLI để kiểm tra định tuyến và test lỗi.

## 🛠️ Công nghệ Sử dụng

| Thành phần | Công nghệ |
| :--- | :--- |
| **OS** | Kali Linux |
| **Simulation** | Mininet + Python |
| **Routing** | FRRouting (FRR) |
| **Visualization** | NetworkX |

## ⚡ Bắt đầu Nhanh

```bash
# 1. Cài đặt dependencies
sudo apt install mininet openvswitch-switch

# 2. Chạy mô phỏng
sudo python3 tdtu_ospf.py
```
