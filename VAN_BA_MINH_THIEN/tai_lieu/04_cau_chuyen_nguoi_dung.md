# User stories và tiêu chí chấp nhận

| ID | Câu chuyện người dùng | Tiêu chí chấp nhận |
|---|---|---|
| US-01 | Là khách, tôi muốn tạo tài khoản để sử dụng nền tảng. | Email hợp lệ và duy nhất; mật khẩu không lưu dạng rõ; báo lỗi khi email đã tồn tại. |
| US-02 | Là sinh viên, tôi muốn tạo hồ sơ năng lực để được gợi ý việc phù hợp. | Có thể cập nhật học vấn, địa điểm, kỹ năng, kinh nghiệm, lương và thời gian; dữ liệu được lưu và chỉ chủ hồ sơ sửa được. |
| US-03 | Là sinh viên, tôi muốn kiểm soát việc nhà tuyển dụng tìm thấy hồ sơ. | Mặc định tắt; có thể bật/tắt; khi tắt, truy vấn kho ứng viên không trả về hồ sơ. |
| US-04 | Là sinh viên, tôi muốn tải CV riêng tư. | Hệ thống kiểm tra loại và kích thước tệp; người không có quyền không thể tải CV bằng cách đoán URL. |
| US-05 | Là sinh viên, tôi muốn tìm và lọc việc làm. | Có thể tìm từ khóa và lọc theo tiêu chí; kết quả phân trang; không có kết quả vẫn hiển thị trạng thái rỗng rõ ràng. |
| US-06 | Là sinh viên, tôi muốn lưu việc để xem sau. | Lưu/bỏ lưu thành công; không có bản ghi trùng cho cùng tin. |
| US-07 | Là sinh viên, tôi muốn ứng tuyển bằng CV đã chọn. | Chỉ nhận hồ sơ cho tin đang mở; chặn nộp trùng; trạng thái ban đầu là `submitted`. |
| US-08 | Là sinh viên, tôi muốn theo dõi tiến trình hồ sơ. | Chỉ xem hồ sơ của mình và thấy trạng thái/thời điểm cập nhật. |
| US-09 | Là nhà tuyển dụng, tôi muốn quản lý tin tuyển dụng. | Tạo/sửa/đóng tin; chỉ chủ sở hữu được sửa; tin hết hạn/đóng không nhận ứng tuyển mới. |
| US-10 | Là nhà tuyển dụng, tôi muốn tìm ứng viên phù hợp. | Chỉ kết quả đang bật hiển thị; lọc được theo tiêu chí; có phân trang và điểm matching giải thích được. |
| US-11 | Là nhà tuyển dụng, tôi muốn lưu ứng viên tiềm năng. | Lưu/bỏ lưu; không tạo liên kết trùng; chỉ nhà tuyển dụng tạo liên kết mới được quản lý danh sách đó. |
| US-12 | Là nhà tuyển dụng, tôi muốn mời sinh viên ứng tuyển vào vị trí cụ thể. | Lời mời gắn tin; chặn trùng đang chờ; có giới hạn gửi và trạng thái phản hồi. |
| US-13 | Là sinh viên, tôi muốn phản hồi lời mời. | Chỉ người nhận được phản hồi; trạng thái chuyển một lần từ `pending` sang chấp nhận/từ chối. |
| US-14 | Là nhà tuyển dụng, tôi muốn xử lý hồ sơ ứng tuyển. | Chỉ xem hồ sơ vào tin mình sở hữu; trạng thái chỉ chuyển theo luồng cho phép. |
| US-15 | Là quản trị viên, tôi muốn kiểm duyệt tin và quản lý người dùng. | Chỉ admin truy cập; thao tác kiểm duyệt có kết quả/lý do và ghi nhật ký. |
| US-16 | Là người dùng, tôi muốn hiểu điểm matching. | Điểm trong khoảng 0–100; nêu tiêu chí đóng góp và kỹ năng còn thiếu; không tuyên bố đây là kết luận tuyển dụng. |

## Ràng buộc dùng chung

- Mọi quyền được kiểm tra phía máy chủ cho từng đối tượng cụ thể.
- Khi yêu cầu không hợp lệ, hệ thống trả thông báo có thể hiểu được và không ghi dữ liệu một phần.
- Không hiển thị dữ liệu cá nhân/CV vượt quá phạm vi người dùng đã cho phép.
