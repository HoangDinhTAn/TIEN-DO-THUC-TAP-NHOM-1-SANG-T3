# Danh sách chức năng và use case

## 1. Danh mục chức năng

| Mã | Chức năng | Tác nhân chính | Ưu tiên |
|---|---|---|---|
| UC-01 | Đăng ký/đăng nhập/đăng xuất | Khách, người dùng | Bắt buộc |
| UC-02 | Quản lý hồ sơ sinh viên, kỹ năng và CV | Sinh viên | Bắt buộc |
| UC-03 | Bật/tắt hiển thị hồ sơ | Sinh viên | Bắt buộc |
| UC-04 | Quản lý hồ sơ nhà tuyển dụng | Nhà tuyển dụng | Bắt buộc |
| UC-05 | Tạo/sửa/đóng tin tuyển dụng | Nhà tuyển dụng | Bắt buộc |
| UC-06 | Kiểm duyệt tin | Quản trị viên | Cơ bản |
| UC-07 | Tìm/lọc/sắp xếp việc làm | Khách, sinh viên | Bắt buộc |
| UC-08 | Lưu/bỏ lưu việc làm | Sinh viên | Bắt buộc |
| UC-09 | Ứng tuyển và theo dõi hồ sơ | Sinh viên | Bắt buộc |
| UC-10 | Quản lý hồ sơ ứng tuyển | Nhà tuyển dụng | Bắt buộc |
| UC-11 | Tìm kiếm kho ứng viên | Nhà tuyển dụng | Điểm nhấn |
| UC-12 | Lưu/bỏ lưu ứng viên | Nhà tuyển dụng | Điểm nhấn |
| UC-13 | Gửi và phản hồi lời mời | Nhà tuyển dụng, sinh viên | Điểm nhấn |
| UC-14 | Xem điểm matching và giải thích | Sinh viên, nhà tuyển dụng | Điểm nhấn |
| UC-15 | Quản lý tài khoản/danh mục/báo cáo | Quản trị viên | Cơ bản |

## 2. Đặc tả luồng quan trọng

### UC-09 — Ứng tuyển

**Tiền điều kiện:** Đăng nhập với vai trò sinh viên; hồ sơ có CV hợp lệ; tin đang mở và chưa hết hạn.

**Luồng chính:**
1. Sinh viên mở trang chi tiết tin và chọn ứng tuyển.
2. Hệ thống xác nhận quyền sở hữu CV và kiểm tra tin còn nhận hồ sơ.
3. Hệ thống kiểm tra chưa tồn tại hồ sơ ứng tuyển cho cặp sinh viên–tin.
4. Sinh viên xác nhận CV/nội dung gửi.
5. Hệ thống tạo hồ sơ ở trạng thái `submitted` và thông báo kết quả.

**Luồng thay thế:** Thiếu CV thì yêu cầu cập nhật hồ sơ; tin đóng/hết hạn hoặc đã ứng tuyển thì từ chối thao tác, giữ nguyên dữ liệu.

### UC-11 — Tìm ứng viên

**Tiền điều kiện:** Đăng nhập với vai trò nhà tuyển dụng và có hồ sơ nhà tuyển dụng hợp lệ.

**Luồng chính:** Nhà tuyển dụng nhập tiêu chí → hệ thống chỉ truy vấn hồ sơ đang bật hiển thị → kết quả được phân trang và có thể sắp xếp theo mức matching → khi mở hồ sơ/CV, hệ thống kiểm tra lại quyền truy cập.

**Luồng thay thế:** Hồ sơ đã tắt hiển thị giữa hai lần truy cập thì không trả thông tin/CV trong lượt truy cập mới.

### UC-13 — Lời mời ứng tuyển

**Tiền điều kiện:** Nhà tuyển dụng sở hữu tin đang mở; sinh viên đang cho phép tìm kiếm.

**Luồng chính:** Chọn sinh viên và tin → kiểm tra giới hạn gửi và lời mời đang chờ → tạo lời mời `pending` → sinh viên xem lời mời → chấp nhận hoặc từ chối → hệ thống lưu trạng thái và thời điểm phản hồi.

**Luồng thay thế:** Tin không thuộc nhà tuyển dụng, sinh viên không hiển thị hoặc đã có lời mời đang chờ thì từ chối gửi.

### UC-14 — Matching

Hệ thống lấy hồ sơ và yêu cầu của tin, tính điểm từng tiêu chí theo cấu hình trọng số, tổng hợp về thang 0–100, sau đó trả điểm tổng và giải thích. Kết quả không thay thế quyết định của sinh viên/nhà tuyển dụng. Dữ liệu nhạy cảm không phải tiêu chí matching.

## 3. Trạng thái nghiệp vụ đề xuất

- Tin tuyển dụng: `draft` → `pending_review` → `published` → `closed` hoặc `expired`; quản trị viên có thể chuyển `pending_review` sang `rejected`.
- Hồ sơ ứng tuyển: `submitted` → `reviewing` → `interview` → `offered` / `rejected` / `withdrawn`.
- Lời mời: `pending` → `accepted` / `declined` / `cancelled` / `expired`.

Chuyển trạng thái phải được xác thực ở lớp nghiệp vụ; không nhận trạng thái tùy ý từ client.

## 4. Quy trình tổng quát

### Sinh viên

Đăng ký/đăng nhập → hoàn thiện hồ sơ và CV → tùy chọn bật hiển thị → tìm kiếm/lọc việc → xem matching → lưu tin hoặc ứng tuyển → theo dõi hồ sơ; đồng thời có thể nhận lời mời và chấp nhận/từ chối. Bật hiển thị là tùy chọn, không phải điều kiện để tìm việc/ứng tuyển.

### Nhà tuyển dụng

Đăng ký/đăng nhập → hoàn thiện hồ sơ tổ chức → tạo tin → chờ duyệt/đăng tin → quản lý ứng tuyển → tìm hồ sơ đang hiển thị → xem matching → lưu ứng viên/gửi lời mời → xử lý phản hồi.

### Quản trị viên

Đăng nhập → quản lý tài khoản/vai trò và danh mục → duyệt tin/báo cáo → ghi nhận hành động → xem thống kê.
