# Yêu cầu hệ thống

## 1. Mục tiêu và phạm vi phiên bản đầu

Xây dựng nền tảng tuyển dụng hai chiều cho sinh viên và nhà tuyển dụng. Sinh viên chủ động tìm việc; nhà tuyển dụng có thể tìm hồ sơ đã được sinh viên cho phép hiển thị. Hệ thống xếp hạng và giải thích mức độ phù hợp để hỗ trợ quyết định của con người.

Phiên bản đầu gồm tài khoản và phân quyền, hồ sơ sinh viên, hồ sơ nhà tuyển dụng, tin tuyển dụng, tìm kiếm việc, ứng tuyển, lưu việc, kho CV có kiểm soát, lời mời ứng tuyển, matching theo quy tắc và quản trị cơ bản. Phân tích CV bằng NLP/AI nâng cao là phần mở rộng; hệ thống lõi không phụ thuộc API bên ngoài.

## 2. Tác nhân và quyền hạn

| Tác nhân | Quyền chính |
|---|---|
| Khách | Xem trang giới thiệu và tin tuyển dụng công khai; đăng ký, đăng nhập |
| Sinh viên | Quản lý hồ sơ/CV/kỹ năng; bật tắt hiển thị hồ sơ; tìm, lọc, lưu việc; ứng tuyển; xem trạng thái; phản hồi lời mời; xem giải thích matching |
| Nhà tuyển dụng | Quản lý hồ sơ doanh nghiệp; CRUD tin của mình; xem ứng viên đã bật hiển thị; lưu ứng viên; gửi lời mời; xem và xử lý hồ sơ ứng tuyển |
| Quản trị viên | Quản lý tài khoản, vai trò và danh mục; kiểm duyệt tin; xử lý báo cáo; xem thống kê và nhật ký quản trị |

Một tài khoản có thể mang nhiều vai trò, nhưng mọi thao tác phải được kiểm tra quyền ở máy chủ. Không dùng trạng thái hiển thị giao diện làm cơ chế phân quyền.

## 3. Yêu cầu chức năng

### M01 — Tài khoản và phân quyền
- FR-01: Đăng ký, đăng nhập, đăng xuất; email duy nhất; mật khẩu được băm bằng cơ chế chuẩn của framework.
- FR-02: Gán và quản lý vai trò Student, Employer, Admin; chặn thao tác không đúng vai trò ở máy chủ.
- FR-03: Người dùng có thể cập nhật thông tin tài khoản và trạng thái hoạt động.

### M02 — Hồ sơ sinh viên
- FR-04: Sinh viên tạo/cập nhật hồ sơ gồm trường, ngành, địa điểm, mong muốn lương, lịch/thời gian làm, kinh nghiệm và kỹ năng.
- FR-05: Sinh viên tải CV lên, thay thế hoặc gỡ CV; hệ thống giới hạn định dạng/kích thước và kiểm tra quyền tải xuống.
- FR-06: Sinh viên tự bật/tắt khả năng được nhà tuyển dụng tìm thấy; mặc định riêng tư.

### M03 — Nhà tuyển dụng và tin tuyển dụng
- FR-07: Nhà tuyển dụng tạo/cập nhật hồ sơ tổ chức.
- FR-08: Nhà tuyển dụng tạo, sửa, đóng và quản lý tin của chính mình; tin có trạng thái, hạn nộp, địa điểm/hình thức, mức lương, mô tả và kỹ năng yêu cầu.
- FR-09: Tin đóng, bị từ chối hoặc hết hạn không nhận ứng tuyển mới.
- FR-10: Quản trị viên có thể kiểm duyệt tin và ghi nhận lý do xử lý.

### M04 — Tìm việc và lưu việc
- FR-11: Người dùng tìm tin công khai theo từ khóa, danh mục, địa điểm/hình thức, mức lương và trạng thái; có sắp xếp và phân trang.
- FR-12: Sinh viên lưu/bỏ lưu tin; mỗi cặp sinh viên–tin chỉ có một bản ghi.

### M05 — Ứng tuyển
- FR-13: Sinh viên nộp hồ sơ cho tin đang mở, chọn CV và gửi nội dung bổ sung nếu có.
- FR-14: Không cho tạo hồ sơ trùng cho cùng sinh viên và tin; lưu thời điểm và trạng thái xử lý.
- FR-15: Nhà tuyển dụng chỉ xem hồ sơ gửi vào tin do mình sở hữu; cập nhật trạng thái theo luồng rõ ràng.
- FR-16: Sinh viên xem trạng thái hồ sơ của mình.

### M06 — Kho CV ứng viên
- FR-17: Nhà tuyển dụng đủ điều kiện tìm/lọc hồ sơ sinh viên đã bật hiển thị.
- FR-18: Chỉ hiển thị dữ liệu hồ sơ trong phạm vi được cho phép; CV được tải qua kiểm tra quyền, không cung cấp đường dẫn công khai.
- FR-19: Nhà tuyển dụng lưu/bỏ lưu ứng viên; không tạo bản ghi trùng.

### M07 — Lời mời ứng tuyển
- FR-20: Nhà tuyển dụng gửi lời mời gắn với một tin cụ thể đến sinh viên đang bật hiển thị.
- FR-21: Sinh viên chấp nhận hoặc từ chối; lời mời có trạng thái, thời điểm và người gửi/người nhận.
- FR-22: Chặn lời mời lặp đang chờ phản hồi và áp dụng giới hạn gửi để giảm quấy rối.

### M08 — Matching
- FR-23: Tính điểm tương thích 0–100 giữa hồ sơ và tin bằng các tiêu chí có trọng số: kỹ năng 35%, ngành/chuyên môn 15%, kinh nghiệm 15%, địa điểm/hình thức 15%, lương 10%, thời gian 10%.
- FR-24: Trả về điểm từng tiêu chí, kỹ năng phù hợp và yêu cầu còn thiếu; dữ liệu thiếu phải được xử lý nhất quán và không làm lỗi toàn bộ kết quả.
- FR-25: Hiển thị matching như gợi ý có giải thích, không tự động quyết định tuyển dụng.

### M10 — Quản trị cơ bản
- FR-26: Quản trị viên quản lý tài khoản/vai trò, danh mục nghề nghiệp, kiểm duyệt tin và xem báo cáo/thống kê cơ bản.
- FR-27: Ghi nhật ký cho thao tác quản trị quan trọng.

## 4. Yêu cầu phi chức năng

- Bảo mật: kiểm tra quyền phía máy chủ, chống truy cập ngang quyền, bảo vệ CSRF và dùng xác thực an toàn.
- Riêng tư: hồ sơ riêng tư mặc định; có thể thu hồi quyền hiển thị; CV không được phục vụ trực tiếp từ thư mục công khai.
- Tính đúng: ràng buộc duy nhất chống ứng tuyển/lưu tin trùng; kiểm tra hạn và trạng thái tin tại thời điểm ghi dữ liệu.
- Hiệu năng: phân trang, truy vấn có chỉ mục phù hợp và tránh tải toàn bộ hồ sơ/CV.
- Khả dụng: giao diện tiếng Việt, tương thích màn hình di động, lỗi đầu vào dễ hiểu.
- Cấu hình: thông tin nhạy cảm và cấu hình môi trường không đặt cứng trong mã nguồn.
- Độ tin cậy: xử lý trường hợp dữ liệu thiếu, tệp không hợp lệ và lỗi nghiệp vụ bằng thông báo rõ ràng.

## 5. Quy tắc nghiệp vụ và tiêu chí chấp nhận cấp cao

1. Chỉ chủ sở hữu tin tuyển dụng được sửa/đóng tin đó.
2. Chỉ sinh viên đã bật hiển thị mới xuất hiện trong kho CV; tắt hiển thị sẽ ngăn các lượt tìm kiếm mới.
3. Chỉ chủ hồ sơ, nhà tuyển dụng sở hữu tin liên quan (đối với hồ sơ ứng tuyển), hoặc quản trị viên có quyền phù hợp mới xem CV.
4. Ứng tuyển phải bị từ chối nếu tin đóng/hết hạn hoặc đã có hồ sơ đang tồn tại theo cặp sinh viên–tin.
5. Lời mời luôn gắn với tin cụ thể, có trạng thái và được giới hạn tần suất.
6. Matching có thể tái lập từ dữ liệu đầu vào và trọng số; giải thích được tiêu chí đóng góp.
7. Hành động bị cấm phải trả về lỗi phù hợp và không làm thay đổi dữ liệu.

## 6. Ngoài phạm vi phiên bản đầu

Huấn luyện mô hình AI riêng; tự động phân loại/từ chối ứng viên; tích hợp thanh toán; microservice; ứng dụng di động độc lập; phân tích CV phụ thuộc dịch vụ bên ngoài. Có thể bổ sung sau khi các luồng cốt lõi ổn định.
