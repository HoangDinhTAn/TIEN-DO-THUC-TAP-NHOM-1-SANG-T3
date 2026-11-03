# Danh mục chức năng đầy đủ

Nguồn: tài liệu **PHÂN TÍCH VÀ THIẾT KẾ DỰ ÁN.pdf** (51 trang). Giữ mã chức năng trong tài liệu để đối chiếu. P0 = MVP; P1 = giai đoạn hoàn thiện; P2 = mở rộng. Thứ tự dưới đây là thứ tự triển khai đề xuất theo phụ thuộc, không phải lời hứa rằng prototype hiện đã có chức năng.

## 0. Nền tảng dùng chung

- [ ] Chọn kiến trúc web/API/AI; cấu hình môi trường dev và production, quản lý secrets, logging, OpenAPI.
- [ ] Thiết kế PostgreSQL và migration; mô hình user, consent, profile, company, job, application, match, message, notification, report, audit log.
- [ ] Quy ước REST `/api/v1`, phân trang, mã lỗi thống nhất, idempotency cho ứng tuyển/lời mời, rate limit và tài liệu API.
- [ ] Quản lý file an toàn: giới hạn kích thước/định dạng, quét virus, URL ký tạm thời [SYS-03, P0].
- [ ] Tìm kiếm toàn văn; PostgreSQL FTS trước, vector search khi có dữ liệu [SYS-04, P0].
- [ ] Hàng đợi tác vụ parse CV, tính match, gửi email và tạo embedding [SYS-05, P0].
- [ ] Rate limit theo người dùng/IP [SYS-07, P0]; backup/khôi phục [SYS-09, P0].
- [ ] Cache Redis [SYS-06, P1]; log/metrics/cảnh báo [SYS-08, P1]; FAQ/trợ giúp [SYS-10, P1].
- [ ] Tiếng Việt/Anh [SYS-01, P1], SEO/JobPosting [SYS-02, P1], responsive/PWA [SYS-11, P1], accessibility [SYS-12, P2], feature flags [SYS-13, P2], public API/webhook [SYS-14, P2].

## 1. Tài khoản, xác thực, đồng ý dữ liệu (AUTH)

- [ ] AUTH-01 Đăng ký sinh viên bằng email, tên, mật khẩu mạnh và đồng ý chính sách [P0].
- [ ] AUTH-02 Đăng ký nhà tuyển dụng bằng email công ty, tên công ty, MST, chức vụ [P0].
- [ ] AUTH-03 Xác minh email bằng link/OTP hết hạn 15 phút; giới hạn gửi lại [P0].
- [ ] AUTH-04 Đăng nhập email/mật khẩu, access token và refresh token [P0].
- [ ] AUTH-05 Đăng nhập Google/LinkedIn/GitHub [P1].
- [ ] AUTH-06 Quên/đặt lại mật khẩu bằng link một lần hết hạn 30 phút; thu hồi phiên cũ [P0].
- [ ] AUTH-07 Đổi mật khẩu/email có xác minh lại [P0].
- [ ] AUTH-08 2FA, bắt buộc cho Admin và HR chủ tài khoản [P1].
- [ ] AUTH-09 Xem thiết bị/phiên và đăng xuất từ xa [P1].
- [ ] AUTH-10 Khóa tạm sau 5 lần sai, CAPTCHA và giới hạn theo IP [P0].
- [ ] AUTH-11 RBAC: Guest, Student, Recruiter, Company Admin, Platform Admin, Moderator, School Admin [P0].
- [ ] AUTH-12 Xác thực sinh viên bằng email trường, mã SV hoặc trường duyệt [P1].
- [ ] AUTH-13 Xóa mềm 30 ngày rồi xóa/anonymize theo chính sách [P0].
- [ ] AUTH-14 Lưu lịch sử đồng ý/rút đồng ý theo mục đích và phiên bản chính sách [P0].
- [ ] AUTH-15 Xuất dữ liệu cá nhân JSON/PDF [P1].
- [ ] AUTH-16 Onboarding hỏi nguyện vọng/ngành/địa điểm để xử lý cold start [P0].

## 2. Hồ sơ sinh viên (SP)

- [ ] SP-01 Thông tin cá nhân, avatar, liên hệ, địa phương, giới thiệu; dữ liệu nhạy cảm không dùng để chấm điểm [P0].
- [ ] SP-02 Học vấn: trường, khoa, ngành, GPA/thang điểm, thời gian học, môn nổi bật [P0].
- [ ] SP-03 Kỹ năng taxonomy, cấp độ, số năm và nhóm kỹ năng [P0].
- [ ] SP-04 Kinh nghiệm thực tập/part-time/freelance/tình nguyện và thành tựu [P0].
- [ ] SP-05 Dự án, vai trò, công nghệ, kết quả, link demo/GitHub [P0].
- [ ] SP-06 Chứng chỉ và thông tin xác minh [P1].
- [ ] SP-07 Ngoại ngữ và chứng chỉ/điểm [P0].
- [ ] SP-08 Giải thưởng, hoạt động ngoại khóa [P1].
- [ ] SP-09 LinkedIn/GitHub/Behance/portfolio/blog [P1].
- [ ] SP-10 Nhiều nguyện vọng có thứ tự: nghề, loại hình, địa điểm, lương, ngày bắt đầu, quy mô/văn hóa [P0].
- [ ] SP-11 Nhiều CV PDF/DOCX ≤10MB, CV mặc định và quét virus [P0].
- [ ] SP-12 Parse CV, hiện độ tin cậy theo trường, xác nhận của SV trước khi lưu [P0].
- [ ] SP-13 Tạo CV từ mẫu ATS-friendly, xem trước và xuất PDF [P1].
- [ ] SP-14 % hoàn thiện hồ sơ và gợi ý mục cần bổ sung [P0].
- [ ] SP-15 Công khai/chỉ NTD đã mời/ẩn; chặn công ty cụ thể [P0].
- [ ] SP-16 Che số điện thoại/email cho tới khi đủ điều kiện kết nối [P0].
- [ ] SP-17 Trạng thái tìm việc: gấp/sẵn sàng/chưa có nhu cầu [P1].
- [ ] SP-18 Lịch sử phiên bản hồ sơ [P2].
- [ ] SP-19 Link hồ sơ công khai dạng portfolio [P2].

## 3. Tìm việc và ứng tuyển (SJ)

- [ ] SJ-01 Dashboard cá nhân: gợi ý, tin mới/sắp hết hạn, đơn và lời mời [P0].
- [ ] SJ-02 Full-text tiếng Việt có/không dấu, chịu lỗi chính tả và autocomplete [P0].
- [ ] SJ-03 Tìm kiếm câu tự nhiên bằng ngữ nghĩa [P1].
- [ ] SJ-04 Bộ lọc ngành, nghề, kỹ năng, địa điểm, lương, loại hình, cấp bậc, kinh nghiệm, quy mô, thời gian, remote và ngoại ngữ [P0].
- [ ] SJ-05 Sắp xếp phù hợp/mới/lương/hạn nộp [P0].
- [ ] SJ-06 Chi tiết tin: mô tả, yêu cầu, quyền lợi, quy trình, hạn, công ty, tin tương tự [P0].
- [ ] SJ-07 Điểm phù hợp, kỹ năng khớp/thiếu, lương và địa điểm có hợp nguyện vọng không [P0].
- [ ] SJ-08 Lưu/bỏ lưu, nhóm và ghi chú riêng [P0].
- [ ] SJ-09 Theo dõi công ty và nhận tin mới [P1].
- [ ] SJ-10 Job alert theo bộ lọc, gửi hằng ngày/tuần [P1].
- [ ] SJ-11 Ứng tuyển bằng CV/thư/câu hỏi/portfolio; ngăn trùng [P0].
- [ ] SJ-12 Ứng tuyển nhanh một lần bấm [P1].
- [ ] SJ-13 Rút đơn, ghi lý do; giới hạn theo giai đoạn [P0].
- [ ] SJ-14 Timeline trạng thái đơn đầy đủ [P0].
- [ ] SJ-15 Nhận lời mời, chấp nhận/từ chối, chặn công ty [P0].
- [ ] SJ-16 Lịch phỏng vấn, xác nhận/đề xuất lại, nhắc 24h/1h và lịch Google [P1].
- [ ] SJ-17 Nhận phản hồi từ chối có cấu trúc nếu NTD cung cấp [P1].
- [ ] SJ-18 Lịch sử tin đã xem [P1].
- [ ] SJ-19 Báo cáo tin lừa đảo/sai sự thật/thu phí/spam [P0].
- [ ] SJ-20 Đánh giá công ty/quy trình ẩn danh sau khi kết thúc [P2].
- [ ] SJ-21 Gợi ý thực tập theo lịch học/số giờ/năm học [P1].
- [ ] SJ-22 Job fair/sự kiện tuyển dụng [P2].

## 4. AI hỗ trợ sinh viên (SAI)

- [ ] SAI-01 Chấm CV theo rubric; điểm tổng và thành phần [P1].
- [ ] SAI-02 Góp ý/câu viết lại; người dùng chấp nhận hoặc bỏ qua, không bịa dữ liệu [P1].
- [ ] SAI-03 Tùy biến CV cho một JD, chỉ nhấn nội dung có thật [P1].
- [ ] SAI-04 Skill gap xếp theo tần suất và tầm quan trọng [P1].
- [ ] SAI-05 Lộ trình học 1–3–6 tháng [P2].
- [ ] SAI-06 Gợi ý nghề theo ngành/kỹ năng/sở thích và dữ liệu thị trường [P1].
- [ ] SAI-07 Chatbot nghề nghiệp RAG có nguồn, từ chối ngoài phạm vi [P2].
- [ ] SAI-08 Sinh thư xin việc để SV chỉnh sửa, không bịa [P1].
- [ ] SAI-09 Mô phỏng phỏng vấn, rubric STAR và lịch sử [P2].
- [ ] SAI-10 Câu hỏi phỏng vấn thường gặp [P2].
- [ ] SAI-11 Tư vấn đàm phán theo dữ liệu tin đăng [P2].
- [ ] SAI-12 Giải thích mỗi gợi ý và cách tăng độ phù hợp [P0].
- [ ] SAI-13 Like/dislike và lý do để điều chỉnh gợi ý [P0].
- [ ] SAI-14 Minh bạch dữ liệu đã dùng và tùy chọn tắt cá nhân hóa [P1].

## 5. Công ty và đăng tin (EMP)

- [ ] EMP-01 Hồ sơ công ty: logo/ảnh, MST, ngành, quy mô, chi nhánh, website, giới thiệu, văn hóa, phúc lợi [P0].
- [ ] EMP-02 Xác minh doanh nghiệp: giấy phép/MST/domain và admin duyệt [P0].
- [ ] EMP-03 Mời HR, phân quyền owner/manager/recruiter/viewer [P1].
- [ ] EMP-04 Tạo tin với chức danh, cấp bậc, loại hình, headcount, lương, địa điểm, mô tả, quyền lợi, hạn và đối tượng [P0].
- [ ] EMP-05 Kỹ năng bắt buộc/ưu tiên, mức tối thiểu và trọng số [P0].
- [ ] EMP-06 Câu hỏi sàng lọc/knockout [P1].
- [ ] EMP-07 AI viết JD [P2].
- [ ] EMP-08 AI phát hiện thiên kiến/yêu cầu phi thực tế/lừa đảo [P2].
- [ ] EMP-09 Vòng đời tin nháp → chờ duyệt → đăng → tạm dừng → hết hạn/đóng [P0].
- [ ] EMP-10 Nhân bản/gia hạn/đóng tin [P0].
- [ ] EMP-11 Import tin CSV/Excel [P2].
- [ ] EMP-12 Mẫu JD tái sử dụng [P1].
- [ ] EMP-13 Thống kê lượt xem/lưu/đơn/chuyển đổi/nguồn [P1].
- [ ] EMP-14 Trang thương hiệu tuyển dụng công khai [P2].

## 6. ATS / quản lý ứng viên

- [ ] ATS-01 Danh sách đơn, lọc theo điểm/trạng thái/kỹ năng/trường/GPA/ngày [P0].
- [ ] ATS-02 Điểm, breakdown, kỹ năng khớp/thiếu và đoạn CV liên quan [P0].
- [ ] ATS-03 Chi tiết hồ sơ, CV, thư, câu trả lời và lịch sử [P0].
- [ ] ATS-04 Kanban giai đoạn cấu hình theo công ty [P0].
- [ ] ATS-05 So sánh 2–5 ứng viên [P1].
- [ ] ATS-06 Ghi chú nội bộ, mention và tag [P1].
- [ ] ATS-07 Scorecard nhiều người đánh giá [P1].
- [ ] ATS-08 Thao tác hàng loạt [P1].
- [ ] ATS-09 Mẫu email mời/từ chối/offer [P1].
- [ ] ATS-10 Đặt lịch phỏng vấn, người tham dự, link và tránh trùng lịch [P1].
- [ ] ATS-11 Offer lương/ngày bắt đầu/hạn trả lời, theo dõi phản hồi [P1].
- [ ] ATS-12 Từ chối với lý do chuẩn [P0].
- [ ] ATS-13 Phát hiện hồ sơ trùng/CV nhồi từ khóa [P2].
- [ ] ATS-14 Blind review [P2].
- [ ] ATS-15 Audit hoạt động trên hồ sơ [P1].
- [ ] ATS-16 Xuất CSV/Excel theo quyền [P2].

## 7. Tìm và mời ứng viên (SRC)

- [ ] SRC-01 Tìm hồ sơ công khai theo kỹ năng/ngành/trường/năm/GPA/địa điểm/ngoại ngữ/trạng thái [P0].
- [ ] SRC-02 Top-N ứng viên cho mỗi tin kèm giải thích [P0].
- [ ] SRC-03 Lời mời cá nhân hóa, giới hạn số lượng/ngày [P0].
- [ ] SRC-04 Talent pool có nhóm/tag/nhắc liên hệ [P1].
- [ ] SRC-05 Tìm ứng viên tương tự bằng embedding [P2].
- [ ] SRC-06 Lưu tìm kiếm và báo ứng viên mới [P2].
- [ ] SRC-07 Giới hạn xem, ghi log và chặn lạm dụng [P0].
- [ ] SRC-08 Theo dõi trạng thái lời mời và tỷ lệ phản hồi [P1].

## 8. Matching hai chiều (MT)

- [ ] MT-01 Chuẩn hóa hồ sơ/JD thành đặc trưng và taxonomy kỹ năng [P0].
- [ ] MT-02 Điểm SV→Job (mức SV đáp ứng yêu cầu việc) [P0].
- [ ] MT-03 Điểm Job→SV (mức tin đáp ứng mong muốn SV) [P0].
- [ ] MT-04 Điểm hai chiều harmonic mean, hiển thị phù hợp cho từng phía [P0].
- [ ] MT-05 Lọc cứng theo điều kiện bắt buộc/địa điểm/loại hình/block [P0].
- [ ] MT-06 Tính lại khi hồ sơ/JD/tin đổi; xử lý nền [P0].
- [ ] MT-07 Mutual match và chỉ mở chat khi đủ điều kiện [P1].
- [ ] MT-08 Thao tác quan tâm/bỏ qua hai phía [P1].
- [ ] MT-09 Giải thích bằng breakdown/mẫu/LLM, không dùng thuộc tính nhạy cảm [P0].
- [ ] MT-10 Ghi feedback hành vi [P0].

## 9. Giao tiếp và thông báo (CM)

- [ ] CM-01 Chat realtime 1:1 sau ứng tuyển được xem/lời mời được nhận/mutual match [P1].
- [ ] CM-02 Trạng thái đang nhập/đã gửi/đã đọc/online [P1].
- [ ] CM-03 Đính kèm ≤10MB, giới hạn định dạng và quét file [P1].
- [ ] CM-04 Lịch sử/tìm tin nhắn [P1].
- [ ] CM-05 Chặn và báo cáo quấy rối [P1].
- [ ] CM-06 Phát hiện sớm yêu cầu chuyển tiền/link lừa đảo [P2].
- [ ] CM-07 Thông báo trong app, nhóm loại và đánh dấu đã đọc [P0].
- [ ] CM-08 Email xác nhận đơn/lời mời/trạng thái/lịch và digest [P0].
- [ ] CM-09 Push web/mobile [P1].
- [ ] CM-10 Cài đặt kênh và loại sự kiện [P1].
- [ ] CM-11 Đồng bộ Calendar/Outlook và Meet/Zoom [P2].
- [ ] CM-12 Tin nhắn mẫu HR [P2].

## 10. Quản trị (AD)

- [ ] AD-01 Dashboard DAU/MAU, user, tin, đơn, match, tuyển thành công, lỗi [P0].
- [ ] AD-02 Tìm/xem/khóa/mở/đặt lại/gán vai trò người dùng [P0].
- [ ] AD-03 Duyệt doanh nghiệp, xem chứng từ, từ chối/yêu cầu bổ sung có lý do [P0].
- [ ] AD-04 Kiểm duyệt tin gắn cờ, duyệt/gỡ/yêu cầu sửa [P0].
- [ ] AD-05 Xử lý báo cáo, phân loại mức độ, cảnh cáo/gỡ/khóa và phản hồi [P0].
- [ ] AD-06 Danh sách đen doanh nghiệp/domain/SĐT/từ khóa [P1].
- [ ] AD-07 CRUD ngành/kỹ năng/alias/trường/chuyên ngành/địa điểm [P0].
- [ ] AD-08 Cấu hình trọng số/ngưỡng/tính năng/mô hình/ngân sách AI [P1].
- [ ] AD-09 Giám sát chất lượng/lỗi/chi phí/độ trễ/công bằng [P2].
- [ ] AD-10 Quản lý nội dung hướng nghiệp/mẫu CV/FAQ/banner [P1].
- [ ] AD-11 Quản lý mẫu email/thông báo [P1].
- [ ] AD-12 Audit log bất biến, lọc/xuất [P0].
- [ ] AD-13 Gói và hạn mức tin/lời mời/lượt xem [P2].
- [ ] AD-14 Xử lý yêu cầu xóa/xuất dữ liệu cá nhân [P1].
- [ ] AD-15 Xuất báo cáo Excel/PDF [P1].

## 11. Cổng nhà trường (SC, tùy chọn)

- [ ] SC-01 Tài khoản cán bộ khoa/quan hệ doanh nghiệp [P2].
- [ ] SC-02 Import/đối chiếu mã sinh viên [P2].
- [ ] SC-03 Thống kê việc làm/ngành/lương/doanh nghiệp [P2].
- [ ] SC-04 Đối chiếu kỹ năng thị trường với chương trình đào tạo [P2].
- [ ] SC-05 Giảng viên giới thiệu sinh viên [P2].
- [ ] SC-06 Quản lý job fair/workshop [P2].

## 12. Quy tắc nghiệp vụ bắt buộc

- [ ] BR-01 Email duy nhất; một vai trò chính SV hoặc NTD.
- [ ] BR-02 Công ty chưa xác minh chỉ được tạo nháp.
- [ ] BR-03 Hạn tin trong tương lai, tối đa 90 ngày; có gia hạn.
- [ ] BR-04 Một đơn mỗi SV/tin; nộp lại theo điều kiện sau rút/từ chối.
- [ ] BR-05 Chỉ xem hồ sơ đầy đủ khi hồ sơ công khai, đã ứng tuyển hoặc đã nhận lời mời.
- [ ] BR-06 Che thông tin liên hệ tới khi SV ứng tuyển/chấp nhận kết nối.
- [ ] BR-07 Chỉ mở chat khi đơn được xem, lời mời được nhận hoặc mutual match.
- [ ] BR-08 Giới hạn lời mời/ngày; không mời lại người đã từ chối cùng tin.
- [ ] BR-09 Tin có dấu hiệu lừa đảo bị gắn cờ và ẩn tới khi duyệt.
- [ ] BR-10 AI không tự từ chối ứng viên; quyết định do NTD.
- [ ] BR-11 Không đưa thuộc tính nhạy cảm vào điểm xếp hạng.
- [ ] BR-12 Ghi log NTD xem hồ sơ; SV có thể xem lịch sử.
- [ ] BR-13 Tin hết hạn tự đóng; không làm mất đơn đang xử lý.
- [ ] BR-14 Nhắc NTD khi đơn chưa được phản hồi quá hạn.
- [ ] BR-15 Báo cáo lặp nhiều lần đưa tài khoản vào hàng xét duyệt.
- [ ] BR-16 Dữ liệu tài khoản xóa được anonymize khỏi thống kê.
- [ ] BR-17 File CV quét virus/kiểm định định dạng/làm sạch trước khi gửi LLM.
- [ ] BR-18 Điểm thấp có thể không vào gợi ý chủ động nhưng vẫn xuất hiện khi tìm kiếm.
- [ ] BR-19 Tin thực tập không yêu cầu kinh nghiệm chính thức quá mức; cảnh báo yêu cầu bất hợp lý.
- [ ] BR-20 SV chỉ thấy tên công ty và đầu mối được công ty cho phép.

## 13. Vòng đời trạng thái

- Tin: Nháp → Chờ duyệt → Đang đăng ↔ Tạm dừng → Hết hạn/Đã đóng; từ chối → Cần chỉnh sửa; vi phạm → Bị gỡ.
- Đơn: Đã nộp → Đã xem → Sàng lọc → Phỏng vấn → Đề nghị → Nhận việc; nhánh kết thúc: Từ chối/Rút/Hết hạn. Mọi lần chuyển phải lưu log và phát thông báo.
- Lời mời: Đã gửi → Đã xem → Chấp nhận/Từ chối/Hết hạn; NTD thu hồi trước khi chấp nhận.
- Phỏng vấn: Đề xuất → Xác nhận/Đề xuất giờ khác → Đã diễn ra → Kết quả/Hủy/Vắng mặt.
- Kết nối: Chưa quan tâm → một/both phía quan tâm → Mutual match → mở chat; có thể bỏ qua.

## 14. Yêu cầu phi chức năng và AI

- [ ] CV Parser: PDF/DOCX/OCR, phân đoạn, trích JSON theo schema, chuẩn hóa kỹ năng, độ tin cậy mỗi trường và SV xác nhận [P0 cơ bản].
- [ ] JD Parser và Skill Normalizer: trích điều kiện, chuẩn hóa alias/chức danh theo taxonomy [P0 cơ bản].
- [ ] Matching Engine: luật có trọng số; sau đó hybrid BM25/vector [P0 rồi P1].
- [ ] Re-ranker và recommender hybrid; chỉ học từ hành vi khi đã có dữ liệu đánh giá đủ tin cậy [P2].
- [ ] Explainer từ score breakdown, tiếng Việt, nêu kỹ năng khớp/thiếu, không nêu yếu tố nhạy cảm [P0].
- [ ] CV Reviewer, career advisor/RAG, interview simulator và AI JD generator theo các mục SAI/EMP ở trên [P1/P2].
- [ ] Moderation tin/hồ sơ/tin nhắn; luật + classifier/LLM, chuyển người duyệt khi chưa chắc chắn [P0 cơ bản; nâng cao P2].
- [ ] Fairness monitor: so sánh kết quả giữa nhóm có kỹ năng tương đương, báo Admin và yêu cầu rà soát [P2].
- [ ] Hiệu năng: LCP <2.5s, API đọc p95 <500ms, tìm kiếm p95 <800ms, gợi ý p95 <2s.
- [ ] Tải: MVP 500 đồng thời, hướng mở rộng 5.000; uptime ≥99%, RTO ≤4h, RPO ≤24h.
- [ ] Bảo mật: TLS/HSTS, cookie an toàn, hash mật khẩu Argon2/bcrypt, RBAC, chống OWASP Top 10, rate limit, file scan.
- [ ] Quyền riêng tư: consent, xuất/xóa dữ liệu ≤30 ngày, ẩn danh, log xem hồ sơ.
- [ ] Khả dụng: responsive, tiếng Việt Unicode, keyboard/screen-reader, WCAG 2.1 AA luồng chính.
- [ ] Vận hành: CI/CD, OpenAPI, correlation ID, metrics/cảnh báo, backup và khôi phục.
- [ ] AI: giải thích được, fallback, prompt versioning, giới hạn token/chi phí, ẩn danh log, timeout/retry, chống prompt injection.
- [ ] Matching: luật/trọng số trước; hybrid BM25+vector/Top-K khi có dữ liệu; re-rank học máy sau khi đủ nhãn.
- [ ] Đánh giá: Precision/Recall/NDCG/MRR/MAP, CTR, apply rate, fairness, độ hữu ích của giải thích.

## 15. Kịch bản nghiệm thu cốt lõi

- [ ] Từ đăng ký → xác minh → onboarding → hồ sơ → tìm việc → ứng tuyển → trạng thái.
- [ ] Công ty đăng ký → xác minh → tạo tin nháp → duyệt → công khai.
- [ ] NTD xem Top-N, breakdown điểm, lọc ứng viên và chuyển trạng thái; quyết định do người.
- [ ] Upload file giả dạng PDF bị từ chối; prompt injection trong CV không đổi điểm.
- [ ] Ứng tuyển trùng bị chặn; NTD chưa xác minh không đăng công khai.
- [ ] Hồ sơ ẩn không bị NTD xem; liên hệ bị che trước khi kết nối.
- [ ] Vector search lỗi thì tìm từ khóa vẫn chạy; lỗi AI không làm hỏng luồng.
- [ ] Chat trái điều kiện bị từ chối; giới hạn lời mời có hiệu lực.
- [ ] Xóa tài khoản xử lý dữ liệu cá nhân và anonymize thống kê theo chính sách.
- [ ] Hai hồ sơ tương đương về kỹ năng nhận điểm gần nhau dù khác thuộc tính nhạy cảm.

## Trạng thái dự án và thứ tự làm

- Prototype hiện có: màn hình tìm việc/hồ sơ/ứng tuyển mẫu và danh sách ứng viên giả lập.
- **Nền tảng API — Đã khởi tạo, chưa nghiệm thu:** FastAPI, PostgreSQL/SQLAlchemy, Alembic migrations, Mailpit local, health/readiness.
- **AUTH P0 cơ bản — Đã viết và nối UI, cần nghiệm thu/hardening:** đăng ký Student/Recruiter, consent, email verification/resend, login + khóa tạm, refresh rotation, logout, `/me`, quên/đặt lại mật khẩu. RBAC cốt lõi cho Guest/Student/Recruiter/Platform Admin/Moderator và quyền thành viên company owner/manager/recruiter/viewer đã được nối ở API; xem [PHAN_QUYEN.md](PHAN_QUYEN.md). School Admin, CAPTCHA/IP rate-limit, thu hồi consent, đổi email/mật khẩu, 2FA và xóa/export có lịch chờ chưa triển khai.
- **Hồ sơ SV P0 cơ bản — API và UI đã nối, cần nghiệm thu:** lưu hồ sơ, học vấn, kỹ năng, kinh nghiệm, dự án, nguyện vọng, visibility và completeness; dữ liệu demo giữ local, tài khoản backend lưu qua API.
- **CV P0 — Đã viết, cần nghiệm thu:** upload PDF/DOCX ≤10MB, kiểm tra magic bytes, lưu private local, chọn mặc định/xóa, trích văn bản và gợi ý email/điện thoại/kỹ năng để người dùng rà soát. Còn quét virus/OCR/LLM extraction.
- **Quyền, tin tuyển dụng và ATS-lite — Đã nối luồng cốt lõi, cần nghiệm thu:** nhà tuyển dụng tạo/sửa/đóng tin của công ty mình; công ty chưa xác minh chỉ tạo nháp; sinh viên nộp/xem/rút đơn của mình; trùng đơn bị chặn; công ty chỉ xem và xử lý ứng viên của tin thuộc công ty, tải CV có phân quyền. Còn duyệt tin, CV bắt buộc/câu hỏi sàng lọc, timeline đầy đủ và báo cáo.
- **Bước kế tiếp:** xác minh hồ sơ sinh viên; tiếp theo hoàn thiện duyệt tin, ATS và nghiệm thu end-to-end các luồng đã nối.
- **Bước 2:** AUTH P0 (đăng ký, xác minh email, đăng nhập, khôi phục, RBAC, consent, rate limit).
- **Bước 3:** hồ sơ SV + onboarding + quyền riêng tư.
- **Bước 4:** công ty/xác minh/tin/duyệt/tìm việc.
- **Bước 5:** ứng tuyển và ATS-lite.
- **Bước 6:** matching giải thích được + sourcing + phản hồi.
- **Bước 7:** admin, thông báo, bảo mật/vận hành; sau đó lần lượt các P1 rồi P2.

Mục được đánh dấu là yêu cầu mục tiêu, chưa mặc định đã triển khai. Cập nhật dấu `[ ]` thành `[x]` và ghi chú khi chức năng hoàn tất.
