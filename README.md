# Hệ thống dự đoán nguy cơ mắc bệnh ung thư

Dự án xây dựng một hệ thống hỗ trợ dự đoán nguy cơ mắc bệnh ung thư từ dữ liệu bệnh nhân, kết hợp giữa **học máy**, **lưu trữ dữ liệu lớn**, và **giao diện web trực quan**.

## Giới thiệu

Dự án này được thực hiện nhằm xây dựng một ứng dụng có thể:

- Nhận dữ liệu bệnh nhân từ file Excel
- Tiền xử lý dữ liệu đầu vào
- Sử dụng mô hình học máy để dự đoán nguy cơ mắc bệnh ung thư
- Lưu trữ dữ liệu vào Apache Hive
- Hỗ trợ thống kê, tìm kiếm và tra cứu bệnh nhân qua giao diện web

## Chức năng chính

- Dự đoán nguy cơ mắc bệnh ung thư từ dữ liệu bệnh nhân
- Nhập dữ liệu từ file Excel
- Lưu trữ và truy vấn dữ liệu trên Apache Hive
- Tìm kiếm và lọc bệnh nhân theo các chỉ số
- Thống kê và trực quan hóa dữ liệu
- Giao diện web bằng Streamlit

## Công nghệ sử dụng

- **Ngôn ngữ:** Python
- **Giao diện:** Streamlit
- **Lưu trữ dữ liệu:** Apache Hive
- **Triển khai môi trường:** Docker
- **Tiền xử lý / hỗ trợ mô hình:** RapidMiner
- **Thư viện chính:** pandas, pyhive, altair, pickle

## Cấu trúc thư mục

```bash
Nhom16_HeThongDuDoanMacBenhUngThu/
├── ApplyModel.py
├── Cancer Prediction.py
├── Web.py
├── Hive_server.ipynb
├── model/
└── port/
