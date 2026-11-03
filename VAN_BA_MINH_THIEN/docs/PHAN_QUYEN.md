# Ma trận vai trò và quyền

Quyền được kiểm tra ở API theo danh tính trong access token. Giao diện chỉ ẩn hoặc khóa thao tác để người dùng dễ hiểu; không được dùng giao diện làm lớp bảo vệ duy nhất.

| Vai trò | Tin tuyển dụng | Hồ sơ/CV và đơn ứng tuyển | Doanh nghiệp | Quản trị |
|---|---|---|---|---|
| Khách | Xem tin đã công khai | Không xem hồ sơ cá nhân hay nộp đơn | Không truy cập dữ liệu nội bộ | Không |
| Sinh viên | Xem tin đã công khai; không tạo/sửa/đóng tin | Chỉ đọc/sửa hồ sơ, CV của mình; nộp đơn, xem/rút đơn của mình | Không | Không |
| Nhà tuyển dụng | Tạo/sửa/đóng tin thuộc công ty mình; công ty chưa xác minh chỉ tạo nháp | Không nộp đơn, không xem danh sách đơn của sinh viên khác | Chỉ truy cập công ty đã tham gia | Không |
| Thành viên công ty `owner`/`manager` | Quản lý tin và xem/xử lý đơn của công ty | Chỉ xem CV được đính kèm vào đơn thuộc tin của công ty | Đọc, sửa hồ sơ và tải giấy tờ xác minh | Không |
| Thành viên công ty `recruiter` | Quản lý tin và xem/xử lý đơn của công ty | Chỉ xem CV được đính kèm vào đơn thuộc tin của công ty | Đọc hồ sơ và tài liệu; không sửa hồ sơ/xác minh | Không |
| Thành viên công ty `viewer` | Chỉ xem danh sách tin của công ty | Không xem CV hoặc xử lý đơn | Chỉ đọc hồ sơ/tài liệu | Không |
| `platform_admin`, `moderator` | Không ứng tuyển hoặc dùng workspace sinh viên/nhà tuyển dụng | Không truy cập dữ liệu cá nhân qua endpoint tự sở hữu | Duyệt/từ chối doanh nghiệp và xem giấy tờ cần duyệt | Có quyền admin đã triển khai |

## Quy tắc ở API

- `GET /api/v1/jobs` chỉ trả tin `published`.
- `POST/PATCH/DELETE /api/v1/jobs` và `POST /api/v1/jobs/{id}/publish` yêu cầu nhà tuyển dụng là thành viên công ty sở hữu tin. Chỉ `owner`, `manager`, `recruiter` được ghi; `viewer` không được ghi. Chỉ công ty `verified` được công khai tin.
- `POST /api/v1/jobs/{id}/applications`, `GET /api/v1/applications/me` và `DELETE /api/v1/applications/me/{id}` chỉ dành cho sinh viên; mọi thao tác giới hạn theo chính `student_id`. Mỗi sinh viên chỉ có một đơn cho mỗi tin. CV đính kèm phải thuộc sinh viên đó.
- `GET /api/v1/recruiter/jobs/{id}/applications`, `PATCH /api/v1/recruiter/applications/{id}` và tải CV ứng viên chỉ dành cho thành viên có quyền tuyển dụng của đúng công ty sở hữu tin. Email/điện thoại không được trả trong danh sách ứng viên.
- Hồ sơ công ty và giấy tờ chỉ truy cập được bởi thành viên của công ty; sửa hồ sơ/tải giấy tờ yêu cầu `owner` hoặc `manager`.
- API admin chỉ nhận `platform_admin` hoặc `moderator`.

Vai trò `school_admin` và việc mời/quản lý thành viên công ty chưa được bật; form đăng ký công khai chỉ cho tạo tài khoản sinh viên hoặc nhà tuyển dụng.
