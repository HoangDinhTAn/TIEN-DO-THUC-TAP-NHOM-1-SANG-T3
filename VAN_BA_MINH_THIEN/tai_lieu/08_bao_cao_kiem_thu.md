# Báo cáo kiểm thử và trạng thái bàn giao

## Trạng thái hiện tại

- Các module chức năng M01–M10 đã được triển khai trong mã nguồn theo phạm vi đồ án.
- Chưa có kết quả kiểm thử tự động hoặc kiểm thử thủ công được ghi nhận trong báo cáo này. Các tình huống bên dưới đang ở trạng thái **chưa thực hiện**; không xem đây là xác nhận nghiệm thu.
- Phân tích CV hiện dò kỹ năng từ văn bản PDF/DOCX bằng từ điển cục bộ. PDF dạng ảnh chưa có OCR.
- Trợ lý AI đã có giao diện và tích hợp API tùy chọn; cần cấu hình `OPENAI_API_KEY` để trả lời thật. Luồng gọi API chưa được xác thực bằng khóa thật.
- Trung tâm thông báo matching hai chiều đã được bổ sung; cần chạy migration để tạo bảng `notifications`. Tạo gợi ý hiện là thao tác thủ công trong website, chưa có lịch chạy nền.

## Kịch bản cần kiểm tra trước khi nghiệm thu

| Nhóm | Tình huống | Kết quả mong đợi | Trạng thái |
|---|---|---|---|
| Tài khoản | Đăng ký bằng email đã tồn tại hoặc mật khẩu yếu | Từ chối và báo lỗi rõ ràng | Chưa thực hiện |
| Phân quyền | Sinh viên mở trang quản trị hoặc sửa tin của người khác | Bị từ chối truy cập | Chưa thực hiện |
| Hồ sơ/CV | Tải PDF/DOCX hợp lệ, tệp sai định dạng, tệp vượt 5 MB | Chỉ nhận tệp hợp lệ trong giới hạn | Chưa thực hiện |
| Quyền riêng tư | Tắt hiển thị hồ sơ rồi tìm trong kho ứng viên | Hồ sơ không xuất hiện | Chưa thực hiện |
| Tin tuyển dụng | Nhà tuyển dụng tạo tin, quản trị viên duyệt/từ chối | Chỉ tin đã duyệt xuất hiện công khai | Chưa thực hiện |
| Tìm việc | Lọc, sắp xếp, phân trang và lưu/bỏ lưu tin | Kết quả khớp tiêu chí; danh sách lưu cập nhật | Chưa thực hiện |
| Ứng tuyển | Ứng tuyển hai lần hoặc vào tin đã đóng/hết hạn | Không tạo hồ sơ trùng hoặc hồ sơ không hợp lệ | Chưa thực hiện |
| Lời mời | Gửi lời mời, sinh viên chấp nhận/từ chối, gửi trùng | Trạng thái và quyền truy cập đúng quy tắc | Chưa thực hiện |
| Matching | Đổi kỹ năng hoặc điều kiện công việc | Điểm và giải thích phù hợp với dữ liệu đầu vào | Chưa thực hiện |
| Phân tích CV | PDF/DOCX có kỹ năng, tệp lỗi, PDF scan | Trích xuất có giới hạn; lỗi được báo; PDF scan có thể không có kết quả | Chưa thực hiện |
| Trợ lý AI | Hỏi về quy trình bằng tài khoản thường, kiểm tra thiếu/sai API key và lỗi kết nối | Trả lời tiếng Việt; báo lỗi dễ hiểu; không làm hỏng chức năng khác | Chưa thực hiện |
| Thông báo matching | Sinh viên tạo gợi ý việc; nhà tuyển dụng tạo gợi ý ứng viên đã bật tìm kiếm; thử tạo lại | Lưu đúng người nhận, chặn trùng, mở đúng trang; không lộ hồ sơ tắt tìm kiếm | Chưa thực hiện |
| Báo cáo/quản trị | Gửi báo cáo, xử lý báo cáo và xem dashboard | Chỉ quản trị viên thao tác; số liệu khớp dữ liệu | Chưa thực hiện |

## Các bước kiểm tra khi chạy local

1. Tạo môi trường ảo, cài `requirements.txt` và cấu hình database theo `07_huong_dan_cai_dat.md`.
2. Chạy `python manage.py check` và `python manage.py migrate`.
3. Tạo tài khoản quản trị bằng `python manage.py createsuperuser`; tạo tài khoản sinh viên và nhà tuyển dụng qua trang đăng ký.
4. Thực hiện các tình huống trong bảng bằng ít nhất ba vai trò: khách, sinh viên, nhà tuyển dụng; dùng quản trị viên để duyệt tin và xử lý báo cáo.
5. Ghi kết quả thực tế, lỗi phát hiện và môi trường chạy trước khi đánh dấu nghiệm thu.

## Giới hạn và điều kiện triển khai

- Không dùng `runserver` làm máy chủ production.
- Chỉ dùng cấu hình production sau khi HTTPS hoạt động, vì cấu hình này ép HTTPS và bật HSTS một năm.
- Dùng tài khoản MySQL riêng với quyền tối thiểu; không đưa `.env`, khóa bí mật hoặc CV thật vào kho mã nguồn.
- Kết quả matching và phân tích CV chỉ mang tính hỗ trợ; người dùng cần xem xét trước khi ra quyết định tuyển dụng.
