"""Create repeatable local demo accounts, CVs, jobs, and applications."""

import re
import unicodedata
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from ung_dung.ho_so_sv.models import Skill, StudentProfile, StudentResume, StudentSkill
from ung_dung.nha_tuyen_dung.models import EmployerProfile
from ung_dung.tai_khoan.demo_accounts import (
    DEMO_ADMIN_EMAIL,
    DEMO_PASSWORD,
    get_demo_login_accounts,
)
from ung_dung.tai_khoan.models import AccountEmail, UserRole
from ung_dung.tin_tuyen_dung.models import Job, JobCategory, JobSkill
from ung_dung.ung_tuyen.models import Application


SAMPLE_JOBS = [
    {
        "title": "Thực tập sinh Python / Django",
        "category": "Phát triển phần mềm",
        "organization": "Công ty Công nghệ Sao Việt",
        "major": "Công nghệ thông tin",
        "skills": ["Python", "Django", "SQL"],
        "location": "Quận 1, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.HYBRID,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Tham gia phát triển tính năng web bằng Django, xây dựng API và phối hợp với nhóm sản phẩm.",
        "requirements": "Biết Python cơ bản, SQL và Git. Có dự án cá nhân là lợi thế.",
    },
    {
        "title": "Frontend Developer Intern",
        "category": "Phát triển phần mềm",
        "organization": "Pixel Việt Studio",
        "major": "Công nghệ thông tin",
        "skills": ["JavaScript", "React", "HTML", "CSS"],
        "location": "Quận Bình Thạnh, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.ONSITE,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Xây dựng giao diện web responsive bằng React và làm việc cùng nhóm thiết kế UI/UX.",
        "requirements": "Nắm HTML, CSS, JavaScript; biết React và Git là lợi thế.",
    },
    {
        "title": "Thực tập sinh Phân tích dữ liệu",
        "category": "Dữ liệu và phân tích",
        "organization": "Mây Data Solutions",
        "major": "Hệ thống thông tin",
        "skills": ["Python", "SQL", "Excel"],
        "location": "Quận 3, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.HYBRID,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Làm sạch dữ liệu, tổng hợp báo cáo và hỗ trợ phân tích chỉ số kinh doanh.",
        "requirements": "Sử dụng được Excel và SQL; có tư duy phân tích, biết Python là lợi thế.",
    },
    {
        "title": "Thực tập sinh Thiết kế UI/UX",
        "category": "Thiết kế",
        "organization": "Mộc Design Lab",
        "major": "Thiết kế đồ họa",
        "skills": ["Figma", "UI/UX", "Photoshop"],
        "location": "Quận 7, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.REMOTE,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Thiết kế luồng người dùng, wireframe và giao diện cho ứng dụng web, mobile.",
        "requirements": "Có portfolio cơ bản, sử dụng Figma và sẵn sàng tiếp nhận phản hồi.",
    },
    {
        "title": "Thực tập sinh Digital Marketing",
        "category": "Marketing",
        "organization": "Bước Tiến Media",
        "major": "Marketing",
        "skills": ["SEO", "Content", "Excel"],
        "location": "Quận Tân Bình, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.HYBRID,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Hỗ trợ lập kế hoạch nội dung, tối ưu SEO và theo dõi hiệu quả chiến dịch.",
        "requirements": "Viết nội dung rõ ràng, biết Excel và có kiến thức SEO cơ bản.",
    },
    {
        "title": "Java Backend Developer Intern",
        "category": "Phát triển phần mềm",
        "organization": "Kết Nối Số JSC",
        "major": "Kỹ thuật phần mềm",
        "skills": ["Java", "Spring Boot", "SQL", "Git"],
        "location": "Quận 10, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.ONSITE,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Phát triển dịch vụ backend, viết API và tham gia cải thiện cơ sở dữ liệu.",
        "requirements": "Có kiến thức Java, SQL và lập trình hướng đối tượng.",
    },
    {
        "title": "Thực tập sinh Kiểm thử phần mềm",
        "category": "Kiểm thử phần mềm",
        "organization": "An Tâm Software",
        "major": "Công nghệ thông tin",
        "skills": ["Manual Testing", "SQL", "Jira"],
        "location": "Quận Phú Nhuận, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.HYBRID,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Đọc yêu cầu, viết test case, kiểm thử chức năng và phối hợp báo lỗi với nhóm phát triển.",
        "requirements": "Cẩn thận, tư duy logic; biết SQL và Jira là lợi thế.",
    },
    {
        "title": "Cộng tác viên Thiết kế đồ họa",
        "category": "Thiết kế",
        "organization": "Nắng Creative House",
        "major": "Thiết kế đồ họa",
        "skills": ["Photoshop", "Illustrator", "Figma"],
        "location": "TP. Thủ Đức, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.REMOTE,
        "employment": Job.EmploymentType.PART_TIME,
        "description": "Thiết kế ấn phẩm mạng xã hội, banner và tài liệu truyền thông theo bộ nhận diện.",
        "requirements": "Có portfolio, sử dụng Photoshop hoặc Illustrator và đảm bảo tiến độ.",
    },
    {
        "title": "Thực tập sinh Tuyển dụng",
        "category": "Nhân sự",
        "organization": "Nhân Lực Mở",
        "major": "Quản trị nhân lực",
        "skills": ["Giao tiếp", "Excel", "Tuyển dụng"],
        "location": "Quận 1, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.ONSITE,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Hỗ trợ đăng tin, sàng lọc hồ sơ, sắp lịch phỏng vấn và cập nhật dữ liệu ứng viên.",
        "requirements": "Giao tiếp tốt, cẩn thận, sử dụng được Excel và yêu thích công việc nhân sự.",
    },
    {
        "title": "Thực tập sinh Phân tích nghiệp vụ",
        "category": "Phân tích nghiệp vụ",
        "organization": "Đường Dài Digital",
        "major": "Hệ thống thông tin",
        "skills": ["Phân tích nghiệp vụ", "SQL", "Excel"],
        "location": "Quận 4, TP. Hồ Chí Minh",
        "mode": Job.WorkMode.HYBRID,
        "employment": Job.EmploymentType.INTERNSHIP,
        "description": "Thu thập yêu cầu, mô tả quy trình và hỗ trợ kết nối giữa khách hàng với nhóm phát triển.",
        "requirements": "Tư duy hệ thống, giao tiếp tốt; biết SQL và Excel là lợi thế.",
    },
]

SAMPLE_STUDENTS = [
    ("Nguyễn Minh Anh", "Đại học Công nghệ TP.HCM", "Công nghệ thông tin", ["Python", "Django", "SQL"]),
    ("Trần Quốc Bảo", "Đại học Khoa học Tự nhiên", "Công nghệ thông tin", ["JavaScript", "React", "HTML", "CSS"]),
    ("Lê Ngọc Chi", "Đại học Kinh tế TP.HCM", "Hệ thống thông tin", ["Python", "SQL", "Excel"]),
    ("Phạm Gia Hân", "Đại học Văn Lang", "Thiết kế đồ họa", ["Figma", "UI/UX", "Photoshop"]),
    ("Võ Thành Đạt", "Đại học Tài chính - Marketing", "Marketing", ["SEO", "Content", "Excel"]),
    ("Đặng Hoàng Long", "Đại học Công nghiệp TP.HCM", "Kỹ thuật phần mềm", ["Java", "Spring Boot", "SQL", "Git"]),
    ("Bùi Khánh Linh", "Đại học Sư phạm Kỹ thuật", "Công nghệ thông tin", ["Manual Testing", "SQL", "Jira"]),
    ("Đỗ Tuấn Kiệt", "Đại học Hoa Sen", "Thiết kế đồ họa", ["Photoshop", "Illustrator", "Figma"]),
    ("Phan Thảo My", "Đại học Mở TP.HCM", "Quản trị nhân lực", ["Giao tiếp", "Excel", "Tuyển dụng"]),
    ("Hồ Đức Nam", "Đại học Công nghệ TP.HCM", "Hệ thống thông tin", ["Phân tích nghiệp vụ", "SQL", "Excel"]),
]


def _ascii(value):
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("ascii")


def _make_sample_pdf(lines):
    commands = ["BT", "/F1 12 Tf", "50 790 Td", "15 TL"]
    for index, line in enumerate(lines):
        safe = _ascii(line).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"({safe}) Tj")
        if index < len(lines) - 1:
            commands.append("T*")
    commands.append("ET")
    stream = "\n".join(commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


class Command(BaseCommand):
    help = "Tạo dữ liệu demo nội bộ trong SQLite: tài khoản, CV, việc làm và đơn ứng tuyển."

    @transaction.atomic
    def handle(self, *args, **options):
        if connection.vendor != "sqlite":
            raise CommandError("Lệnh này chỉ chạy trên SQLite để tránh đưa dữ liệu demo vào database khác.")

        User = get_user_model()
        now = timezone.now()
        today = timezone.localdate()

        admin = self._user(User, DEMO_ADMIN_EMAIL, "admin", is_admin=True)
        self._assign_role(admin, UserRole.Role.ADMIN)

        categories = {}
        skill_map = {}
        for job_data in SAMPLE_JOBS:
            category, _ = JobCategory.objects.get_or_create(
                name=job_data["category"],
                defaults={"description": f"Cơ hội việc làm thuộc nhóm {job_data['category'].lower()}."},
            )
            categories[job_data["category"]] = category
            for skill_name in job_data["skills"]:
                skill_map[skill_name.casefold()] = Skill.objects.get_or_create(
                    normalized_name=skill_name.casefold(),
                    defaults={"name": skill_name},
                )[0]

        employers = []
        jobs = []
        for number, data in enumerate(SAMPLE_JOBS, start=1):
            employer_user = self._user(
                User,
                f"nhatuyendung{number:02d}@example.com",
                f"demo-employer-{number:02d}",
            )
            self._assign_role(employer_user, UserRole.Role.EMPLOYER)
            employer, _ = EmployerProfile.objects.update_or_create(
                user=employer_user,
                defaults={
                    "organization_name": data["organization"],
                    "industry": data["category"],
                    "description": f"{data['organization']} là đơn vị mẫu phục vụ kiểm thử chức năng tuyển dụng.",
                    "address": data["location"],
                    "phone": f"09000000{number:02d}",
                },
            )
            employers.append(employer)

            job, _ = Job.objects.get_or_create(
                employer=employer,
                title=data["title"],
                defaults={
                    "category": categories[data["category"]],
                    "description": data["description"],
                    "requirements": data["requirements"],
                    "location": data["location"],
                    "work_mode": data["mode"],
                    "employment_type": data["employment"],
                    "salary_min": 5000000 + number * 500000,
                    "salary_max": 9000000 + number * 500000,
                    "deadline": today + timedelta(days=60),
                    "status": Job.Status.PUBLISHED,
                    "published_at": now,
                },
            )
            job.category = categories[data["category"]]
            job.description = data["description"]
            job.requirements = data["requirements"]
            job.location = data["location"]
            job.work_mode = data["mode"]
            job.employment_type = data["employment"]
            job.salary_min = 5000000 + number * 500000
            job.salary_max = 9000000 + number * 500000
            job.deadline = today + timedelta(days=60)
            job.status = Job.Status.PUBLISHED
            job.published_at = job.published_at or now
            job.save()
            for skill_name in data["skills"]:
                JobSkill.objects.update_or_create(
                    job=job,
                    skill=skill_map[skill_name.casefold()],
                    defaults={"required_level": StudentSkill.Proficiency.INTERMEDIATE, "is_required": True},
                )
            jobs.append(job)

        for number, (name, school, major, skills) in enumerate(SAMPLE_STUDENTS, start=1):
            email = f"sinhvien{number:02d}@example.com"
            student_user = self._user(User, email, f"demo-student-{number:02d}")
            self._assign_role(student_user, UserRole.Role.STUDENT)
            profile, _ = StudentProfile.objects.update_or_create(
                user=student_user,
                defaults={
                    "full_name": name,
                    "school": school,
                    "major": major,
                    "education": f"Sinh viên năm 3 ngành {major}.",
                    "experience": "Đã tham gia bài tập nhóm và dự án thực hành tại trường.",
                    "bio": f"Ứng viên mẫu {number:02d}, mong muốn học hỏi và phát triển trong lĩnh vực {major.lower()}.",
                    "location": "TP. Hồ Chí Minh",
                    "preferred_work_mode": StudentProfile.WorkMode.ANY,
                    "salary_min": 5000000,
                    "salary_max": 12000000,
                    "available_time": "Có thể bắt đầu trong tháng này",
                    "is_searchable": True,
                },
            )
            for skill_name in skills:
                skill = skill_map[skill_name.casefold()]
                StudentSkill.objects.update_or_create(
                    student_profile=profile,
                    skill=skill,
                    defaults={"proficiency": StudentSkill.Proficiency.INTERMEDIATE},
                )

            resume_name = f"CV_{number:02d}_{re.sub(r'[^a-z0-9]+', '_', _ascii(name).lower()).strip('_')}.pdf"
            relative_path = f"resumes/{student_user.pk}/demo_{number:02d}.pdf"
            pdf = _make_sample_pdf([
                f"HO SO UNG VIEN - {name}",
                f"Email: {email}",
                f"Truong: {school}",
                f"Chuyen nganh: {major}",
                f"Ky nang: {', '.join(skills)}",
                "Kinh nghiem: Du an hoc tap va lam viec nhom.",
                "Muc tieu: Tim co hoi thuc tap va phat trien chuyen mon.",
            ])
            if not default_storage.exists(relative_path):
                default_storage.save(relative_path, ContentFile(pdf))
            resume, _ = StudentResume.objects.update_or_create(
                student_profile=profile,
                original_name=resume_name,
                defaults={
                    "file": relative_path,
                    "content_type": "application/pdf",
                    "size_bytes": len(pdf),
                },
            )
            if profile.current_resume_id != resume.pk:
                profile.current_resume = resume
                profile.save(update_fields=("current_resume", "updated_at"))

            Application.objects.get_or_create(
                student_profile=profile,
                job=jobs[number - 1],
                defaults={
                    "resume": resume,
                    "cover_letter": f"Tôi là {name}, quan tâm đến vị trí {jobs[number - 1].title}. Mong muốn được trao đổi thêm về kinh nghiệm và kỹ năng phù hợp.",
                    "status": Application.Status.SUBMITTED,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            "Đã chuẩn bị dữ liệu mẫu trong database hiện tại: 1 admin, 10 sinh viên/CV/đơn ứng tuyển và 10 nhà tuyển dụng/tin tuyển dụng."
        ))
        self.stdout.write(f"Mật khẩu chung cho các tài khoản mẫu: {DEMO_PASSWORD}")
        self.stdout.write("Tài khoản admin dùng email trong form đăng nhập; tại /admin dùng username admin.")

    @staticmethod
    def _user(User, email, username, *, is_admin=False):
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            user = User.objects.filter(username=username).first()
        if user is None:
            user = User(username=username, email=email)
        else:
            user.username = username
            user.email = email
        user.is_active = True
        user.is_staff = is_admin
        user.is_superuser = is_admin
        user.set_password(DEMO_PASSWORD)
        user.save()
        AccountEmail.objects.update_or_create(user=user, defaults={"email": email})
        return user

    @staticmethod
    def _assign_role(user, role):
        UserRole.objects.get_or_create(user=user, role=role)
