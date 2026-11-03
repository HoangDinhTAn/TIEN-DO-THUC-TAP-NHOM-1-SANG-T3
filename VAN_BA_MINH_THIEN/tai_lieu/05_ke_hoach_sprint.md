# Kế hoạch triển khai theo giai đoạn

Kế hoạch bám theo phạm vi trong README. Mỗi giai đoạn tạo đầu ra có thể xem xét trước khi chuyển bước; các tính năng lõi không phụ thuộc dịch vụ AI bên ngoài.

| Giai đoạn | Nội dung | Đầu ra / điều kiện hoàn thành |
|---|---|---|
| 1. Khảo sát và phân tích | Chốt tác nhân, yêu cầu, use case, quy trình, quy tắc và ERD | Tài liệu 02–06 thống nhất; trạng thái và quyền đã xác định |
| 2. Thiết kế và nền tảng | Khởi tạo ứng dụng Django, cấu hình DB, tài khoản/roles, hồ sơ sinh viên và nhà tuyển dụng | Có thể chạy ứng dụng; đăng nhập và phân quyền phía máy chủ; cấu hình không chứa bí mật |
| 3. Tuyển dụng và ứng tuyển | CRUD tin, duyệt tin, tìm kiếm/lọc, lưu tin, ứng tuyển, xử lý hồ sơ | Quy tắc chủ sở hữu, trạng thái tin và chống trùng được thực thi |
| 4. Matching hai chiều | Kho ứng viên, lọc, lưu ứng viên, matching có giải thích, lời mời | Tôn trọng quyền hiển thị; điểm có thể giải thích; lời mời có giới hạn và trạng thái |
| 5. Hoàn thiện | Dashboard/quản trị, bảo mật tệp, tài liệu, kiểm thử và sửa lỗi | Các luồng chính hoàn tất; kiểm tra quyền và ràng buộc dữ liệu; hướng dẫn cài đặt rõ |

## Trình tự chức năng trong từng giai đoạn

1. M01 tài khoản và phân quyền.
2. M02 hồ sơ sinh viên, kỹ năng và CV; hồ sơ nhà tuyển dụng.
3. M03 tin tuyển dụng và kiểm duyệt cơ bản.
4. M04 tìm/lọc việc và lưu việc.
5. M05 ứng tuyển và quản lý trạng thái.
6. M06 kho CV, chỉ mục tìm kiếm và quyền truy cập.
7. M08 matching có giải thích.
8. M07 lời mời và kiểm soát tần suất.
9. M10 quản trị, thống kê, hoàn thiện giao diện và tài liệu.

M09 phân tích CV bằng NLP/AI được xếp sau khi luồng lõi ổn định. Có thể thay đổi thứ tự triển khai nhỏ nếu phụ thuộc kỹ thuật yêu cầu, nhưng không bỏ qua điều kiện bảo mật và quyền riêng tư.
