# Mô tả đề tài

## Tên đề tài

**Xây dựng nền tảng tuyển dụng thông minh ứng dụng AI hỗ trợ kết nối việc làm hai chiều giữa sinh viên và nhà tuyển dụng.**

## 1. Bối cảnh

Các nền tảng tuyển dụng phổ biến thường tập trung vào quy trình nhà tuyển dụng đăng tin và ứng viên chủ động gửi hồ sơ. Sinh viên có thể khó tìm được vị trí phù hợp với kỹ năng, ngành học, địa điểm và lịch học; nhà tuyển dụng cũng khó tiếp cận ứng viên phù hợp nếu chỉ chờ hồ sơ ứng tuyển.

Đề tài xây dựng nền tảng kết nối hai chiều: sinh viên chủ động tìm việc, còn nhà tuyển dụng có thể chủ động tìm hồ sơ sinh viên đã cho phép hiển thị và gửi lời mời ứng tuyển. Hệ thống cung cấp điểm matching cùng giải thích về mức độ phù hợp để hỗ trợ người dùng đánh giá.

## 2. Mục tiêu

- Tập trung tin tuyển dụng và hồ sơ năng lực sinh viên trên một nền tảng.
- Hỗ trợ sinh viên tìm kiếm, lọc, lưu việc và theo dõi hồ sơ ứng tuyển.
- Cho phép nhà tuyển dụng quản lý tin, tìm hồ sơ được chia sẻ và gửi lời mời gắn với vị trí cụ thể.
- Tính điểm tương thích giữa hồ sơ và công việc, đồng thời nêu rõ tiêu chí phù hợp và kỹ năng còn thiếu.
- Bảo vệ quyền riêng tư, kiểm soát truy cập CV và để sinh viên chủ động bật/tắt khả năng được tìm thấy.
- Cung cấp chức năng quản trị cơ bản cho tài khoản, danh mục, kiểm duyệt và thống kê.

## 3. Đối tượng sử dụng

1. **Sinh viên:** quản lý hồ sơ, kỹ năng và CV; tìm việc, ứng tuyển, lưu việc; quản lý quyền hiển thị và phản hồi lời mời.
2. **Nhà tuyển dụng:** quản lý hồ sơ tổ chức và tin tuyển dụng; tìm/lưu ứng viên được phép hiển thị; gửi lời mời và xử lý hồ sơ.
3. **Quản trị viên:** quản lý tài khoản, vai trò và danh mục; kiểm duyệt tin, xử lý báo cáo và theo dõi hoạt động quản trị.

## 4. Phạm vi phiên bản đầu

Phiên bản đầu tập trung vào tài khoản và phân quyền, hồ sơ sinh viên/nhà tuyển dụng, tin tuyển dụng, tìm kiếm việc làm, ứng tuyển, lưu việc, kho CV có kiểm soát, lời mời ứng tuyển, matching hai chiều theo quy tắc và phần quản trị thiết yếu.

Phân tích CV bằng NLP/AI nâng cao là phần mở rộng. Các chức năng cốt lõi vẫn phải hoạt động khi không kết nối dịch vụ AI bên ngoài. Thuật toán matching ban đầu là thuật toán chấm điểm theo tiêu chí và trọng số; không mô tả nó như mô hình AI đã được huấn luyện.

## 5. Giá trị và nguyên tắc

- Kết nối chủ động từ cả hai phía thay vì chỉ dựa vào hồ sơ ứng tuyển.
- Kết quả matching có thể giải thích, dùng để tham khảo và không tự động quyết định thay người dùng.
- Hồ sơ sinh viên mặc định riêng tư; sinh viên có quyền thu hồi khả năng hiển thị.
- Quyền truy cập được xác minh ở phía máy chủ; CV không được cung cấp qua đường dẫn công khai.
- Hạn chế lời mời lặp hoặc quá thường xuyên để tránh làm phiền sinh viên.

## 6. Kết quả dự kiến

Sản phẩm là ứng dụng web tiếng Việt, có giao diện cho sinh viên, nhà tuyển dụng và quản trị viên; cơ sở dữ liệu quan hệ; quy trình tuyển dụng và ứng tuyển; dịch vụ matching có giải thích; cùng tài liệu yêu cầu, thiết kế, hướng dẫn cài đặt và kiểm thử.

## 7. Công nghệ định hướng

README định hướng ứng dụng Django theo kiến trúc phân lớp, Django ORM và MySQL. Giao diện có thể dùng Django Templates; chỉ bổ sung API riêng khi phát sinh nhu cầu tích hợp frontend độc lập hoặc ứng dụng di động. CV được lưu riêng tư với kiểm tra định dạng, kích thước và quyền truy cập.

## 8. Tài liệu liên quan

- [Yêu cầu hệ thống](02_yeu_cau_he_thong.md)
- [Danh sách chức năng và use case](03_danh_sach_chuc_nang.md)
- [User stories và tiêu chí chấp nhận](04_cau_chuyen_nguoi_dung.md)
- [Kế hoạch triển khai](05_ke_hoach_sprint.md)
- [Thiết kế cơ sở dữ liệu](06_thiet_ke_co_so_du_lieu.md)
