PHÂN TÍCH VÀ THIẾT KẾ DỰ ÁN
Tên đề tài: Xây dựng nền tảng tuyển dụng thông minh ứng dụng AI hỗ trợ kết nối việc làm hai chiều giữa sinh viên và nhà tuyển dụng.


Điểm cốt lõi của dự án là sinh viên chủ động tìm việc, nhà tuyển dụng chủ động tìm CV và hai bên được hệ thống gợi ý kết nối phù hợp. AI là thành phần hỗ trợ quyết định, không tự động quyết định thay người dùng.
1. Tổng quan dự án
1.1. Bài toán cần giải quyết
Các nền tảng tuyển dụng thông thường thường tập trung vào việc nhà tuyển dụng đăng tin và ứng viên gửi hồ sơ. Dự án này mở rộng quy trình theo hướng hai chiều:
- Sinh viên khó xác định công việc nào phù hợp với kỹ năng, ngành học, địa điểm và lịch học.
- Nhà tuyển dụng khó tìm ứng viên phù hợp nếu chỉ chờ hồ sơ ứng tuyển.
- CV của sinh viên có thể thiếu thông tin, trình bày chưa tốt hoặc chưa thể hiện được năng lực.
- Người dùng khó đánh giá mức độ phù hợp giữa yêu cầu tuyển dụng và năng lực thực tế.
- Sinh viên cần kiểm soát thông tin cá nhân và tránh các lời mời tuyển dụng không mong muốn.
1.2. Mục tiêu hệ thống
1. Tập trung thông tin tuyển dụng trên một nền tảng.
2. Xây dựng hồ sơ năng lực cho sinh viên.
3. Hỗ trợ tìm kiếm và xếp hạng công việc phù hợp.
4. Cho phép nhà tuyển dụng tìm kiếm CV và gửi lời mời ứng tuyển.
5. Sử dụng thuật toán matching để giải thích mức độ tương thích.
6. Hỗ trợ phân tích CV và xác định kỹ năng còn thiếu.
7. Đảm bảo phân quyền, bảo vệ dữ liệu và kiểm soát lời mời tuyển dụng.
8. Cung cấp thống kê phục vụ sinh viên, nhà tuyển dụng và quản trị viên.

2. Đối tượng sử dụng và quyền hạn
   Sinh viên — Student
- Tạo tài khoản, cập nhật hồ sơ năng lực và CV.
- Tìm kiếm, lọc, lưu việc làm.
- Ứng tuyển và theo dõi trạng thái hồ sơ.
- Bật hoặc tắt chế độ cho phép nhà tuyển dụng tìm kiếm hồ sơ.
- Nhận, chấp nhận hoặc từ chối lời mời tuyển dụng.
- Xem kết quả matching và đề xuất cải thiện CV.
Nhà tuyển dụng — Employer
- Tạo hồ sơ doanh nghiệp hoặc đơn vị tuyển dụng.
- Đăng, sửa, đóng và quản lý tin tuyển dụng.
- Tìm kiếm, lọc và xem hồ sơ ứng viên đã cho phép hiển thị.
- Xem điểm phù hợp giữa ứng viên và vị trí tuyển dụng.
- Lưu danh sách ứng viên tiềm năng.
- Gửi lời mời ứng tuyển và quản lý phản hồi.
- Xem CV, xử lý hồ sơ ứng tuyển và cập nhật trạng thái.
Quản trị viên — Admin
- Quản lý tài khoản và vai trò.
- Quản lý danh mục nghề nghiệp.
- Kiểm duyệt tin tuyển dụng và xử lý báo cáo.
- Quản lý các trường hợp spam, lạm dụng lời mời.
- Theo dõi thống kê và nhật ký hoạt động quản trị.


3. Phân tích chức năng hệ thống
Nên chia thành các module độc lập để dễ lập trình, kiểm thử và phân công cho các thành viên.
Mã	Module	Chức năng chính	Mức độ
M01	Tài khoản và phân quyền	Đăng ký, đăng nhập, vai trò, bảo mật	Bắt buộc
M02	Hồ sơ sinh viên	Kỹ năng, học vấn, kinh nghiệm, CV	Bắt buộc
M03	Quản lý tuyển dụng	Đăng tin, sửa tin, đóng tin	Bắt buộc
M04	Tìm kiếm việc làm	Từ khóa, bộ lọc, sắp xếp	Bắt buộc
M05	Ứng tuyển	Gửi CV, trạng thái xử lý hồ sơ	Bắt buộc
M06	Kho CV ứng viên	Tìm kiếm và lọc ứng viên	Điểm nhấn
M07	Lời mời tuyển dụng	Gửi, nhận và phản hồi lời mời	Điểm nhấn
M08	Matching thông minh	Chấm điểm tương thích hai chiều	Điểm nhấn
M09	Phân tích CV	Trích xuất kỹ năng, gợi ý cải thiện	Mở rộng
M10	Quản trị và báo cáo	Kiểm duyệt, thống kê, xử lý báo cáo	Bắt buộc cơ bản
Phạm vi phiên bản đầu tiên: hoàn thiện M01–M08 và phần quản trị thiết yếu. M09 có thể làm sau; không nên phụ thuộc vào API AI bên ngoài để toàn bộ hệ thống mới hoạt động.


4. Thiết kế quy trình nghiệp vụ
4.1. Quy trình dành cho sinh viên
   <img width="956" height="1952" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/46ba09db-10a1-4aea-ada1-196e5dbeee67" />
Sinh viên có thể sử dụng nền tảng để tìm việc mà không cần bật hồ sơ công khai. Khi bật chế độ tìm kiếm hồ sơ, sinh viên đồng ý cho nhà tuyển dụng đủ điều kiện tìm thấy hồ sơ theo phạm vi được quy định.
4.2. Quy trình dành cho nhà tuyển dụng
   <img width="928" height="2164" alt="mermaid-diagram (1)" src="https://github.com/user-attachments/assets/4bdf9265-b4db-47df-9685-8e98536ce281" />
4.3. Quy tắc nghiệp vụ quan trọng
- Nhà tuyển dụng chỉ được chỉnh sửa tin tuyển dụng do mình tạo.
- Sinh viên không được xem CV riêng tư của người khác.
- Nhà tuyển dụng chỉ tìm thấy sinh viên đã bật chế độ cho phép tìm kiếm hồ sơ.
- Một sinh viên không thể gửi nhiều hồ sơ ứng tuyển trùng cho cùng một tin tuyển dụng đang xử lý.
- Lời mời phải gắn với một công việc cụ thể và có trạng thái rõ ràng.
- Tin đã đóng hoặc hết hạn không nhận ứng tuyển mới.
- Điểm matching chỉ là gợi ý, không phải kết luận ứng viên chắc chắn phù hợp.
- Hệ thống không cho phép nhà tuyển dụng gửi lời mời vô hạn hoặc liên tục làm phiền cùng một sinh viên.

5. Thiết kế thuật toán matching hai chiều
Đây là phần tạo chiều sâu cho đồ án. Không cần bắt đầu bằng mô hình AI lớn; có thể tự xây dựng thuật toán chấm điểm và kiểm thử bằng dữ liệu mẫu.
5.1. Sinh viên phù hợp với công việc
Hệ thống so sánh hồ sơ sinh viên với yêu cầu của tin tuyển dụng.
Tiêu chí	Trọng số minh họa
Kỹ năng	35%
Ngành học và chuyên môn	15%
Kinh nghiệm	15%
Địa điểm hoặc hình thức làm việc	15%
Mức lương mong muốn	10%
Thời gian có thể làm việc	10%
Tổng	100%

Công thức:<img width="324" height="132" alt="image" src="https://github.com/user-attachments/assets/bc805f68-6a81-43e8-8af9-339a20d1aa6b" />
Trong đó \(w_i\) là trọng số của tiêu chí, \(s_i\) là điểm phù hợp từ 0 đến 100. Trọng số trên là đề xuất ban đầu và cần được kiểm thử, điều chỉnh dựa trên dữ liệu thực tế.

Ví dụ minh họa:<img width="791" height="414" alt="image" src="https://github.com/user-attachments/assets/eb177530-fb2b-4d7e-8a2a-4b6461632a3c" />
5.2. Nhà tuyển dụng phù hợp với sinh viên
Chiều ngược lại không có nghĩa là chấm điểm nhà tuyển dụng dựa trên năng lực sinh viên. Hệ thống nên trả lời hai câu hỏi khác nhau:
- Đối với sinh viên: Công việc nào phù hợp với hồ sơ của tôi?
- Đối với nhà tuyển dụng: Ứng viên nào đáp ứng tốt nhất các yêu cầu của vị trí này?
Cả hai có thể dùng chung điểm tương thích giữa hồ sơ và công việc, nhưng kết quả hiển thị, tiêu chí sắp xếp và quyền truy cập dữ liệu sẽ khác nhau.
5.3. Nâng cấp bằng AI/NLP
Sau khi thuật toán cơ bản hoạt động, có thể bổ sung:
- Chuẩn hóa tên kỹ năng đồng nghĩa, ví dụ “MS Excel” và “Microsoft Excel”.
- Trích xuất kỹ năng từ CV và mô tả công việc.
- Sử dụng TF-IDF và Cosine Similarity để so sánh văn bản.
- Đưa ra giải thích: kỹ năng nào phù hợp, yêu cầu nào còn thiếu.
Điều quan trọng là không gọi một thuật toán chấm điểm theo quy tắc đơn thuần là mô hình AI đã được huấn luyện. Trong báo cáo cần phân biệt rõ thuật toán matching ban đầu với phần NLP/ML mở rộng.
6. Thiết kế cơ sở dữ liệu
T đề xuất 12 bảng chính để mô hình hóa đầy đủ việc làm, hồ sơ ứng viên và cơ chế kết nối hai chiều. Có thể triển khai bằng MySQL và Django ORM.
STT	Bảng	Mục đích và dữ liệu chính
1	users	Tài khoản, email, mật khẩu đã băm, vai trò, trạng thái
2	student_profiles	Trường học, ngành học, địa điểm mong muốn, mức lương, trạng thái hiển thị hồ sơ
3	skills	Danh mục kỹ năng chuẩn hóa
4	student_skills	Liên kết sinh viên với kỹ năng và mức độ thành thạo
5	employers	Thông tin doanh nghiệp hoặc đơn vị tuyển dụng
6	job_categories	Danh mục nghề nghiệp
7	jobs	Tin tuyển dụng, mức lương, yêu cầu, thời hạn, trạng thái
8	job_skills	Kỹ năng và mức độ yêu cầu của từng công việc
9	applications	Hồ sơ ứng tuyển, CV sử dụng và trạng thái xử lý
10	saved_jobs	Danh sách công việc yêu thích
11	job_invitations	Lời mời ứng tuyển do nhà tuyển dụng gửi
12	saved_candidates	Danh sách ứng viên tiềm năng do nhà tuyển dụng lưu
Ngoài ra, nếu triển khai đầy đủ chức năng quản trị và AI, có thể bổ sung các bảng reports để tiếp nhận báo cáo vi phạm, notifications để lưu thông báo và cv_analyses để lưu kết quả phân tích CV. Không nhất thiết phải tạo tất cả trong phiên bản đầu.
6.1. Các quan hệ giữa bảng
  <img width="806" height="479" alt="image" src="https://github.com/user-attachments/assets/a42a4b89-4203-40c0-9072-0e05017699bd" />
6.2. Những ràng buộc dữ liệu cần có
- Email tài khoản phải duy nhất.
- Mỗi tài khoản sinh viên có tối đa một hồ sơ sinh viên; tương tự với nhà tuyển dụng.
- Mỗi cặp user_id, job_id chỉ xuất hiện một lần trong applications.
- Mỗi cặp user_id, job_id chỉ xuất hiện một lần trong saved_jobs.
- Bảng student_skills và job_skills cần khóa duy nhất theo cặp đối tượng–kỹ năng.
- Lời mời cần lưu người gửi, người nhận, công việc, thời điểm gửi và trạng thái phản hồi.
- Mọi khóa ngoại phải được xác định rõ; khi xóa dữ liệu cần cân nhắc xóa dây chuyền hay giữ lịch sử.
Lưu ý: users có thể chứa nhiều vai trò khác nhau, nhưng logic nghiệp vụ phải xác minh vai trò thực tế trước khi cho phép đăng tuyển, ứng tuyển hoặc tìm kiếm CV. Không chỉ dựa vào việc ẩn nút trên giao diện.
7. Thiết kế kiến trúc phần mềm
Với trình độ và phạm vi đồ án hiện tại, t khuyên dùng kiến trúc phân lớp trong một ứng dụng Django, thay vì tách nhiều microservice. Cách này dễ triển khai, chạy được trên máy cá nhân và vẫn thể hiện được tư duy thiết kế hệ thống.
<img width="778" height="660" alt="image" src="https://github.com/user-attachments/assets/d193504c-ed71-478d-afc2-07e5558c5728" />
Vai trò của từng lớp:
- Giao diện: hiển thị trang tìm việc, hồ sơ, tin tuyển dụng và bảng điều khiển.
- Django Views/Forms: nhận yêu cầu, kiểm tra dữ liệu đầu vào và trả về kết quả.
- Lớp nghiệp vụ: xử lý quyền hạn, quy trình ứng tuyển, lời mời và trạng thái tin tuyển dụng.
- Matching Service: tính điểm phù hợp và tạo danh sách gợi ý.
- CV Analysis Service: đọc nội dung CV và trích xuất thông tin nếu chức năng này được bật.
- MySQL: lưu dữ liệu có cấu trúc.
- Kho lưu trữ CV: lưu tệp riêng biệt, kiểm tra định dạng và giới hạn quyền truy cập.
Trong mã nguồn, có thể chia thành các Django apps như accounts, profiles, jobs, applications, matching và dashboard. Không cần xây dựng API riêng nếu ứng dụng ban đầu sử dụng Django Templates; Django REST Framework chỉ cần khi có nhu cầu tích hợp frontend độc lập hoặc ứng dụng di động.
8. Thiết kế giao diện chính
T đề xuất giao diện theo phong cách nền tảng tuyển dụng hiện đại: dễ sử dụng, ưu tiên thao tác tìm kiếm và hiển thị rõ điểm matching.
<img width="890" height="571" alt="image" src="https://github.com/user-attachments/assets/cfe37ebb-53f6-4bf7-9be6-7cd4cf606403" />
9. Yêu cầu phi chức năng
Ngoài các chức năng chính, đồ án cần xác định những yêu cầu về chất lượng.
Tiêu chí	Yêu cầu đề xuất
Bảo mật	Băm mật khẩu bằng cơ chế chuẩn của Django; kiểm tra quyền ở phía máy chủ
Quyền riêng tư	Sinh viên tự chọn hiển thị hồ sơ; hạn chế truy cập và tải CV
Hiệu năng	Tối ưu truy vấn tìm kiếm, phân trang danh sách kết quả
Tính đúng đắn	Không cho ứng tuyển trùng; kiểm tra thời hạn và trạng thái tin
Khả năng sử dụng	Giao diện tiếng Việt, responsive, thông báo lỗi rõ ràng
Khả năng mở rộng	Chia module nghiệp vụ, dùng Django ORM và cấu hình môi trường
Độ tin cậy	Ghi nhận lỗi, xử lý trường hợp dữ liệu thiếu hoặc tệp CV không hợp lệ
Đối với tệp CV, cần kiểm tra loại tệp, kích thước, quyền truy cập và tránh phục vụ trực tiếp các tệp chưa được kiểm tra. Hệ thống cũng nên cho phép sinh viên thu hồi quyền hiển thị hồ sơ.
10. Thiết kế kiểm thử
Một đồ án Công nghệ phần mềm tốt không chỉ có nhiều chức năng mà còn phải chứng minh được các chức năng hoạt động đúng.
Nhóm kiểm thử	Ví dụ tình huống
Tài khoản	Đăng ký email trùng, đăng nhập sai mật khẩu
Phân quyền	Sinh viên thử truy cập trang quản trị
Tìm việc	Tìm kiếm không có kết quả, lọc nhiều tiêu chí
Ứng tuyển	Gửi hai lần vào cùng công việc
Tìm CV	Tìm ứng viên đã tắt hiển thị hồ sơ
Lời mời	Gửi lời mời, chấp nhận, từ chối, gửi trùng
Matching	Thay đổi kỹ năng hoặc địa điểm để kiểm tra điểm số
Bảo mật tệp	Tải lên tệp không hợp lệ hoặc truy cập CV trái quyền
Tin tuyển dụng	Ứng tuyển vào tin đã đóng hoặc hết hạn
Nên sử dụng Django TestCase hoặc pytest để viết kiểm thử tự động cho các quy tắc quan trọng; đồng thời kiểm thử thủ công giao diện trên trình duyệt.
11. Kế hoạch thực hiện theo giai đoạn
Dưới đây là tiến độ tham khảo cho nhóm sinh viên. Có thể điều chỉnh theo thời hạn môn học và số lượng thành viên.
Giai đoạn 1

Khảo sát và phân tích

Yêu cầu chức năng, use case, sơ đồ nghiệp vụ, ERD.


Giai đoạn 2

Thiết kế và nền tảng

Django, MySQL, đăng nhập, phân quyền, hồ sơ.


Giai đoạn 3

Tuyển dụng và ứng tuyển

CRUD tin tuyển dụng, tìm kiếm, ứng tuyển, lưu việc.


Giai đoạn 4

Matching hai chiều

Kho CV, lọc ứng viên, tính điểm phù hợp, lời mời.


Giai đoạn 5

Hoàn thiện và kiểm thử

Dashboard, bảo mật, kiểm thử, tài liệu và báo cáo.



AI phân tích CV và nhận diện tin tuyển dụng đáng ngờ nên là phần mở rộng sau khi quy trình cốt lõi đã hoạt động ổn định.
12. Đánh giá tính khả thi và điểm khác biệt
Tính ứng dụng

Giải quyết cả nhu cầu tìm việc của sinh viên và nhu cầu chủ động tìm ứng viên của nhà tuyển dụng.


Tính kỹ thuật

Có phân quyền, mô hình cơ sở dữ liệu quan hệ, quy trình nghiệp vụ, thuật toán xếp hạng và kiểm thử.


Tính mở rộng

Có thể bổ sung NLP, phân tích CV, thống kê thị trường và đánh giá rủi ro tuyển dụng sau này.


Rủi ro cần kiểm soát

AI có thể trích xuất sai kỹ năng, điểm matching có thể thiên lệch và CV chứa dữ liệu cá nhân. Cần có giải thích kết quả, quyền riêng tư và sự giám sát của con người.



Kết luận và phạm vi nên chốt
Theo t, phiên bản tốt nhất cho đồ án của m là nền tảng có ba chức năng tạo khác biệt:
1. Nhà tuyển dụng chủ động tìm kiếm CV và gửi lời mời ứng tuyển.
2. Matching hai chiều có điểm số và giải thích lý do phù hợp.
3. Phân tích kỹ năng từ hồ sơ để gợi ý việc làm và chỉ ra khoảng cách kỹ năng.
Các chức năng đăng nhập, đăng tin, tìm kiếm, ứng tuyển, quản trị và bảo mật là nền tảng bắt buộc. AI phân tích CV nâng cao có thể làm sau, tránh khiến toàn bộ dự án phụ thuộc vào dịch vụ bên ngoài.

Với thiết kế này, đề tài đủ chiều sâu để trình bày phân tích yêu cầu, Use Case, Activity Diagram, ERD, kiến trúc phần mềm, thuật toán matching, kiểm thử và đánh giá sản phẩm mà vẫn có thể chia nhỏ để nhóm triển khai từng phần.

  




