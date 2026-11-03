# Hướng dẫn cài đặt môi trường nền tảng

## Yêu cầu

- Python 3.11 trở lên.
- MySQL 8.0 trở lên đang chạy trên máy.
- Git (nếu lấy mã nguồn qua Git).

## Cài đặt lần đầu trên Windows PowerShell

Tại thư mục gốc dự án:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env`, đặt `DJANGO_SECRET_KEY` thành chuỗi ngẫu nhiên riêng và nhập tên database, người dùng, mật khẩu MySQL. Không commit `.env`. Khi có `DB_NAME`, cấu hình development dùng MySQL như các biến `DB_*` đã khai báo.

Muốn chạy thử giao diện mà chưa cài MySQL: không tạo `.env`; development sẽ dùng SQLite tại `.local.sqlite3`. SQLite chỉ là lựa chọn tạm cho chạy thử local. Production vẫn dùng MySQL.

Khi dùng MySQL, tạo database rỗng trong MySQL Workbench hoặc MySQL CLI:

```sql
CREATE DATABASE da_ttc
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Tạo người dùng database riêng và cấp quyền trên `da_ttc` theo cấu hình máy cá nhân; không dùng tài khoản quản trị MySQL trong môi trường triển khai.

## Khởi chạy

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Mở `http://127.0.0.1:8000/` để vào dashboard (chưa đăng nhập sẽ được chuyển đến trang đăng nhập), hoặc `http://127.0.0.1:8000/dang-ky/` để tạo tài khoản. Trang quản trị Django ở `http://127.0.0.1:8000/admin/`. Các vai trò đã có gồm sinh viên, nhà tuyển dụng và quản trị viên; đăng ký công khai chỉ cho chọn sinh viên hoặc nhà tuyển dụng.

Sau khi đăng ký, sinh viên mở `/ho-so/` để cập nhật hồ sơ; nhà tuyển dụng mở `/ho-so-nha-tuyen-dung/` để cập nhật tổ chức. CV chỉ nhận PDF/DOCX tối đa 5 MB và tải xuống qua kiểm tra quyền. Tắt tùy chọn hiển thị hồ sơ để không xuất hiện trong tìm kiếm ứng viên.

Nhà tuyển dụng có thể quản lý tin tại `/nha-tuyen-dung/tin/`; tin mới gửi vào trạng thái chờ duyệt. Quản trị viên mở Django Admin → Tin tuyển dụng, chọn các tin chờ duyệt và dùng thao tác duyệt/từ chối. Danh sách tin đã duyệt nằm tại `/viec-lam/`.

Tại `/viec-lam/`, người dùng có thể tìm theo từ khóa, danh mục, địa điểm, hình thức, loại công việc và khoảng lương; kết quả có phân trang và sắp xếp. Sinh viên đăng nhập để lưu/bỏ lưu tin và xem danh sách ở `/viec-lam-da-luu/`.

## Phân tích CV

Sau khi cài thư viện bằng `pip install -r requirements.txt`, sinh viên tải CV PDF/DOCX tại `/ho-so/` rồi chọn **Phân tích kỹ năng từ CV**. Hệ thống dùng từ điển kỹ năng cục bộ, cho phép chọn kỹ năng để thêm vào hồ sơ và gợi ý mục hồ sơ cần bổ sung. Nội dung CV không được lưu sau khi phân tích hoặc gửi tới dịch vụ bên ngoài. PDF dạng ảnh chưa được OCR nên có thể không trích xuất được văn bản.

## Trợ lý AI trong website

Trợ lý AI chỉ xuất hiện với người dùng đã đăng nhập. Để bật, thêm `OPENAI_API_KEY` vào `.env`; có thể đổi model bằng `OPENAI_MODEL` (mặc định `gpt-4o-mini`) rồi khởi động lại Django. API key chỉ được đọc ở máy chủ, không đưa vào trình duyệt hoặc commit lên Git. Khi chưa có key, các chức năng tuyển dụng và matching hiện tại vẫn hoạt động.

Trợ lý dùng OpenAI Responses API để trả lời câu hỏi về cách dùng nền tảng. Câu hỏi và tối đa 8 lượt hội thoại gần nhất được gửi tới OpenAI; mã không tự gửi hồ sơ, CV, email hay dữ liệu ứng viên. Nhắc người dùng không nhập CV, mật khẩu hoặc thông tin riêng tư vào khung chat. Mỗi phiên có giới hạn số lượt hỏi để giảm lạm dụng.

## Thông báo gợi ý việc làm và ứng viên

Người dùng đăng nhập mở **Thông báo** trên thanh điều hướng rồi chọn **Tạo thông báo phù hợp**. Sinh viên nhận tin tuyển dụng phù hợp; nhà tuyển dụng nhận gợi ý ứng viên đã bật chế độ cho phép tìm kiếm. Hệ thống dùng ngưỡng matching từ 50/100, mỗi lần tạo tối đa 20 thông báo mới và không gửi trùng cùng một cặp gợi ý. Đây là thao tác quét theo yêu cầu, không phải email hoặc thông báo đẩy tự động.

Có thể đánh dấu đồng ý dùng AI trong biểu mẫu để AI viết giải thích ngắn. Khi bật lựa chọn đó, tiêu đề công việc, điểm matching và kỹ năng khớp/còn thiếu được gửi tới OpenAI; tên ứng viên, email và nội dung CV không được gửi. Nếu AI chưa cấu hình hoặc không phản hồi, thông báo vẫn được tạo bằng giải thích từ matching hiện có.

## Cấu hình production

Đặt `DJANGO_SETTINGS_MODULE=config.settings.production`, cấu hình `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` và biến `DB_*` trong môi trường triển khai. Cấu hình production tắt debug, bắt buộc HTTPS, đánh dấu cookie session/CSRF chỉ dùng qua HTTPS và bật HSTS trong một năm. Chỉ bật cấu hình này sau khi tên miền và HTTPS đã hoạt động ổn định; trình duyệt sẽ ghi nhớ yêu cầu HTTPS trong thời hạn HSTS. Không bật HSTS cho tên miền còn cần truy cập HTTP.

Mật khẩu mới phải đạt tối thiểu 12 ký tự và vượt qua các bộ kiểm tra mật khẩu mặc định của Django. Giữ `DJANGO_SECRET_KEY` và thông tin MySQL trong biến môi trường hoặc `.env` riêng; không đưa bí mật thật vào mã nguồn.

## Xử lý lỗi cài mysqlclient trên Windows

Nếu `pip install -r requirements.txt` không tìm thấy wheel phù hợp và báo thiếu compiler/MySQL headers, cài Microsoft C++ Build Tools cùng MySQL client development headers rồi chạy lại lệnh cài đặt. Không thay đổi engine sang SQLite vì dự án định hướng MySQL.
