# Hướng — Nền tảng tuyển dụng hai chiều

MVP giao diện được dựng theo tài liệu **PHÂN TÍCH VÀ THIẾT KẾ DỰ ÁN.pdf**, tập trung vào trải nghiệm sinh viên và luồng gợi ý ứng viên cho nhà tuyển dụng.

## Chạy ứng dụng

Đăng nhập/đăng ký cần chạy API. Xem [backend/README.md](backend/README.md) để khởi động PostgreSQL, Mailpit, migration và FastAPI; sau đó mở `http://localhost:8000`. Google Fonts cần kết nối Internet; ngoại tuyến ứng dụng dùng font dự phòng.

## Cấu trúc thư mục

```text
.
├── index.html
├── src/
│   ├── scripts/       # Tương tác giao diện và dữ liệu mẫu
│   └── styles/        # CSS chung và kiểu nhà tuyển dụng
├── backend/
│   └── app/            # FastAPI, cấu hình, database và API versioned
├── docker-compose.yml # PostgreSQL local
├── assets/
│   └── images/        # Hình ảnh, logo
└── docs/              # Phân tích chức năng và tài liệu dự án
```

Danh sách chức năng cần thiết theo mức ưu tiên P0/P1/P2 nằm trong [docs/CHUC_NANG_CAN_CO.md](docs/CHUC_NANG_CAN_CO.md).
Tài khoản demo và cách tạo admin local được ghi trong [backend/README.md](backend/README.md).
Ma trận quyền cho sinh viên, nhà tuyển dụng, thành viên công ty và admin nằm trong [docs/PHAN_QUYEN.md](docs/PHAN_QUYEN.md).

## Luồng prototype hiện có

- Sinh viên xem, tìm kiếm, lọc và mở chi tiết việc làm.
- Mỗi tin có điểm phù hợp và lý do mẫu; đây chưa phải kết quả từ mô hình AI.
- Lưu/bỏ lưu việc làm mẫu; tài khoản thật đăng tin và ứng tuyển qua API có kiểm tra vai trò, ngăn ứng tuyển trùng và lưu trạng thái đơn.
- Xem hồ sơ sinh viên, thay đổi trạng thái công khai và chỉnh sửa một số trường mẫu.
- Nhà tuyển dụng xem ứng viên gợi ý, đọc lý do và gửi lời mời mẫu.
- Bố cục thích ứng màn hình nhỏ; thao tác phản hồi bằng thông báo trong ứng dụng.

## Giới hạn hiện tại

Luồng đăng nhập, hồ sơ, CV, xác minh doanh nghiệp, tin tuyển dụng và ứng tuyển đã có backend/API; xem [backend/README.md](backend/README.md) để chạy database và migration. Quyền được kiểm tra ở API: chỉ nhà tuyển dụng được quản lý tin của công ty mình; công ty chưa xác minh chỉ tạo nháp, công ty đã xác minh mới công khai. Chỉ sinh viên được ứng tuyển/xem/rút đơn của mình; nhà tuyển dụng có quyền trong công ty chỉ xem và xử lý đơn thuộc tin của công ty. Bản demo chạy offline vẫn dùng dữ liệu cục bộ. Duyệt tin tuyển dụng, AI matching thực, chat và thông báo đa kênh chưa triển khai. Không dùng dữ liệu mẫu để ra quyết định tuyển dụng thực tế.
